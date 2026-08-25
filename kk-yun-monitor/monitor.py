import asyncio
import json
import ipaddress
import logging
import re
import time
from pathlib import Path
from datetime import datetime

import aiohttp
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import settings
from telegram import send_alarm
from zoneinfo import ZoneInfo


LOG_DIR = Path(settings.log_dir)
LOG_DIR.mkdir(
    parents=True,
    exist_ok=True
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(
            LOG_DIR / "monitor.log",
            encoding="utf-8"
        ),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(
    "kk-monitor"
)

alarm_cache = {}




def now():
    return datetime.now(
        ZoneInfo(settings.timezone)
    ).strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def check_ip(ip):
    if not ip:
        return False

    ip = str(ip).strip()

    # IPv4:Port
    if "." in ip and ":" in ip:
        ip = ip.rsplit(":", 1)[0]

    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


class HttpClient:
    def __init__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(
                total=settings.timeout
            ),
            headers={
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Content-Type": "application/json;charset=UTF-8",
                "Origin": settings.base_url,
                "Referer": settings.base_url + "/",
                "User-Agent": settings.user_agent,
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
            }
        )

    async def post(self, url, data):
        start = time.time()

        try:
            async with self.session.post(
                url,
                json=data
            ) as resp:

                text = await resp.text()

                logger.info(
                    "POST %s status=%s cost=%.2fs",
                    url,
                    resp.status,
                    time.time() - start
                )

                return {
                    "code": resp.status,
                    "text": text
                }

        except Exception as e:
            logger.error(
                "POST failed url=%s error=%s",
                url,
                e
            )

            return {
                "code": 0,
                "error": str(e)
            }

    async def get(
        self,
        url,
        headers=None
    ):
        start = time.time()

        try:
            logger.info(
                "准备GET请求 url=%s headers=%r",
                url,
                headers
            )

            async with self.session.get(
                url,
                headers=headers
            ) as resp:

                text = await resp.text()

                logger.info(
                    "GET %s 状态=%s 耗时=%.2f秒 响应头=%r",
                    url,
                    resp.status,
                    time.time() - start,
                    dict(resp.headers)
                )

                return {
                    "code": resp.status,
                    "text": text
                }

        except Exception as e:
            logger.error(
                "GET请求失败 url=%s error=%s",
                url,
                e
            )

            return {
                "code": 0,
                "error": str(e)
            }

    async def close(self):
        await self.session.close()


http_client = None


async def get_client():
    global http_client

    if http_client is None:
        http_client = HttpClient()

    return http_client


async def create_measurement(
    project,
    domain,
    client
):
    # client = await get_client()
   

    payload = {
        "tool": "http",
        "target": domain,
        "mode": "once",
        "network": "all",
        "dns": {
            "type": "isp",
            "server": "",
            "recordType": "A"
        },
        "http": {
            "protocol": "auto",
            "resolveHost": "",
            "method": "HEAD",
            "referer": "",
            "userAgent": "",
            "cookie": "",
            "maxRedirects": 0
        },
        "sourceNodeId": ""
    }

    logger.info(
        "create measurement project=%s domain=%s",
        project,
        domain
    )

    result = await client.post(
        f"{settings.base_url}/api/kkyun/measurements",
        payload
    )

    if result.get("code") != 202:
        logger.error(
            "create measurement failed project=%s domain=%s result=%s",
            project,
            domain,
            result
        )

        return None

    try:
        return json.loads(
            result["text"]
        )

    except Exception:
        logger.exception(
            "create response json error project=%s domain=%s",
            project,
            domain
        )

        return None



async def wait_finished(
    project,
    domain,
    view_url,
    client
):
    client = await get_client()

    start = time.time()
    token = None

    url = f"{settings.base_url}{view_url}"

    logger.info(
        "开始等待测量完成 项目=%s 域名=%s 地址=%s",
        project,
        domain,
        url
    )

    while True:

        headers = {}

        if token:
            headers["Cookie"] = f"yxd_token={token}"

            logger.info(
                "第二阶段请求，携带Token 项目=%s 域名=%s Cookie=yxd_token=%s",
                project,
                domain,
                token
            )
        else:
            logger.info(
                "第一阶段请求，暂未携带Token 项目=%s 域名=%s",
                project,
                domain
            )

        result = await client.get(
            url,
            headers=headers
        )

        logger.info(
            "测量接口返回 项目=%s 域名=%s code=%s",
            project,
            domain,
            result.get("code")
        )

        text = result.get(
            "text",
            ""
        )

        logger.info(
            "测量接口原始返回 项目=%s 域名=%s 内容=%r...",
            project,
            domain,
            text[0:40]
        )

        # 检查是否返回Cookie脚本
        match = re.search(
            r"document\.cookie\s*=\s*['\"]yxd_token=([^;'\"]+)",
            text
        )

        if match:

            token = match.group(1)

            logger.info(
                "成功提取yxd_token 项目=%s 域名=%s token=%s",
                project,
                domain,
                token
            )

            # 立刻进入下一次请求
            continue

        # 如果不是JS，尝试解析JSON
        try:
            data = json.loads(
                text
            )

        except Exception:

            logger.error(
                "返回内容不是JSON，也没有检测到yxd_token 项目=%s 域名=%s 内容=%r",
                project,
                domain,
                text
            )

            await asyncio.sleep(2)

            continue

        status = data.get(
            "status"
        )

        logger.info(
            "测量状态 项目=%s 域名=%s 状态=%s",
            project,
            domain,
            status
        )

        if status == "finished":

            logger.info(
                "测量完成 项目=%s 域名=%s 耗时=%.2f秒",
                project,
                domain,
                time.time() - start
            )

            return data

        await asyncio.sleep(
            settings.poll_interval
        )



def analyse_result(
    project,
    domain,
    data
):
    progress = data.get(
        "progress",
        {}
    )

    dns_failed = 0
    access_failed = 0

    failed_ips = []

    rows = data.get(
        "rows",
        []
    )

    logger.info(
        "开始分析测量结果 项目=%s 域名=%s 节点数量=%s",
        project,
        domain,
        len(rows)
    )

    for row in rows:

        if row.get("status") != "failed":
            continue

        response_ip = row.get(
            "responseIp"
        )

        if check_ip(response_ip):

            access_failed += 1

            failed_ips.append(
                response_ip
            )

            logger.debug(
                "节点访问失败 项目=%s 域名=%s IP=%s",
                project,
                domain,
                response_ip
            )

        else:

            dns_failed += 1

            failed_ips.append(
                "DNS解析失败"
            )

            logger.debug(
                "节点DNS解析失败 项目=%s 域名=%s responseIp=%r",
                project,
                domain,
                response_ip
            )

    result = {
        "project": project,
        "domain": domain,
        "dns_failed": dns_failed,
        "access_failed": access_failed,
        "failed_ips": failed_ips,
        "progress": progress
    }

    logger.info(
        "测量结果分析完成 项目=%s 域名=%s DNS解析失败=%s 访问失败=%s 节点总数=%s",
        project,
        domain,
        dns_failed,
        access_failed,
        len(rows)
    )

    logger.debug(
        "测量结果详情 项目=%s 域名=%s 失败IP=%r 进度=%r",
        project,
        domain,
        failed_ips,
        progress
    )

    return result




async def request_measurement(
    project,
    domain
):

    client = HttpClient()

    try:

        logger.info("1. 开始创建测量任务 project=%s domain=%s",project,domain)

        result = await create_measurement(
            project,
            domain,
            client
        )

        logger.info("2. 创建测量任务完成 project=%s domain=%s result=%r",project,domain,result)

        if not result:
            logger.error("2.1 创建测量任务失败 project=%s domain=%s",project,domain)

            data = {
                "project": project,
                "domain": domain,
                "dns_failed": 0,
                "access_failed": 1,
                "failed_ips": [
                    "create failed"
                ]
            }

            logger.info("2.2 返回测量结果 project=%s domain=%s result=%r", project, domain, data)

            return data

        logger.info("3. 开始获取查看地址 project=%s domain=%s", project, domain)

        view_url = result.get("viewUrl")

        logger.info("4. 获取查看地址完成 project=%s domain=%s view_url=%s", project, domain,view_url)

        if not view_url:
            logger.error("4.1 查看地址不存在 project=%s domain=%s result=%r", project, domain, result)

            data = {
                "project": project,
                "domain": domain,
                "dns_failed": 1,
                "access_failed": 0,
                "failed_ips": [
                    "viewUrl missing"
                ]
            }

            logger.info("4.2 返回测量结果 project=%s domain=%s result=%r", project, domain, data)

            return data


        logger.info("5. 开始等待测量完成 project=%s domain=%s view_url=%s",project,domain,view_url)

        data = await wait_finished(project, domain, view_url, client)

        logger.info("6. 开始分析测量结果 project=%s domain=%s", project, domain)

        result = analyse_result(project, domain, data)

        logger.info("7. 分析测量结果完成 project=%s domain=%s result=%r", project, domain, result)

        # logger.info(
        #     "测量请求全部完成 project=%s domain=%s",
        #     project,
        #     domain
        # )

        return result
    
    finally: 
        await client.close() 
        logger.info( "测量客户端已关闭 项目=%s 域名=%s", project, domain )



def need_alarm(key):
    current = int(
        datetime.now().timestamp()
    )

    last = alarm_cache.get(
        key,
        0
    )

    if current - last < settings.alarm_cooldown:
        return False

    alarm_cache[key] = current

    return True


async def check_alarm(result):
    dns_failed = result.get(
        "dns_failed",
        0
    )

    access_failed = result.get(
        "access_failed",
        0
    )

    if (
        dns_failed < settings.alarm_threshold
        and access_failed < settings.alarm_threshold
    ):
        return

    key = (
        result["project"],
        result["domain"]
    )

    if not need_alarm(key):
        return

    message = (
        "🚨 KK Monitor Alarm\n\n"
        f"项目: {result['project']}\n"
        f"域名: {result['domain']}\n"
        f"时间: {now()}\n\n"
        f"DNS解析失败: {dns_failed}\n"
        f"访问失败: {access_failed}\n"
    )

    progress = result.get(
        "progress",
        {}
    )

    message += (
        "\n节点信息:\n"
        f"总节点: {progress.get('total', '-')}\n"
        f"完成: {progress.get('completed', '-')}\n"
        f"失败: {progress.get('failed', '-')}\n"
    )

    failed_ips = result.get(
        "failed_ips",
        []
    )

    if failed_ips:
        unique_ips = list(
            dict.fromkeys(failed_ips)
        )
        
        message += "\n失败详情:\n"
        message += "\n".join(
            unique_ips[:20]
        )

    logger.warning(
        "alarm project=%s domain=%s dns_failed=%s access_failed=%s",
        result["project"],
        result["domain"],
        dns_failed,
        access_failed
    )

    await send_alarm(
        message
    )


async def check_domain(
    project,
    domain
):
    start = time.time()

    logger.info(
        "check start project=%s domain=%s",
        project,
        domain
    )

    # result = await request_measurement(
    #     project,
    #     domain
    # )

    # await check_alarm(
    #     result
    # )

        
    result = None

    logger.error("开始for循环  project=%s domain=%s", project, domain)
    logger.error("开始for循环  settings.alarm_confirm_times=%s", settings.alarm_confirm_times)

    for i in range(settings.alarm_confirm_times):

        logger.error("首次发起检查请求 project=%s domain=%s", project, domain)

        result = await request_measurement(project, domain)

        logger.error("首次发起结束请求 i=%s result=%s", i, result)

        # 本次检测正常，直接结束
        if (
            result["dns_failed"] < settings.alarm_threshold
            and result["access_failed"] < settings.alarm_threshold
        ):
            return

        # 不是最后一次，则等待后重试
        if i < settings.alarm_confirm_times - 1:
            logger.warning(
                "confirm %d/%d failed, retry after %ss, project=%s domain=%s",
                i + 1,
                settings.alarm_confirm_times,
                settings.alarm_confirm_interval,
                project,
                domain,
            )
            await asyncio.sleep(settings.alarm_confirm_interval)

    # 连续多次都失败，才真正告警
    await check_alarm(result)



    logger.info(
        "check finish project=%s domain=%s cost=%.2fs",
        project,
        domain,
        time.time() - start
    )


async def check_all():
    start = time.time()

    logger.info(
        "========== monitor round start =========="
    )

    tasks = []

    for item in settings.projects:

        tasks.append(
            check_domain(
                item["name"],
                item["domain"]
            )
        )

    if tasks:
        await asyncio.gather(
            *tasks,
            return_exceptions=True
        )

    logger.info(
        "========== monitor round finish cost=%.2fs ==========",
        time.time() - start
    )


async def shutdown():
    global http_client

    if http_client:
        await http_client.close()

    logger.info(
        "KK Monitor stopped"
    )


async def main():

    logger.info(
        "KK Monitor started"
    )

    logger.info(
        "projects=%s interval=%ss",
        len(settings.projects),
        settings.interval
    )

    scheduler = AsyncIOScheduler()

    scheduler.add_job(
        check_all,
        "interval",
        seconds=settings.interval,
        max_instances=1,
        coalesce=True
    )

    scheduler.start()

    await check_all()

    try:
        while True:
            await asyncio.sleep(
                3600
            )

    except KeyboardInterrupt:
        logger.info(
            "receive stop signal"
        )

    finally:
        scheduler.shutdown()
        await shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
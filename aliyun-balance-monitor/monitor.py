#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import logging
from datetime import datetime

import httpx
import yaml

from alibabacloud_bssopenapi20171214.client import Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_util import models as util_models


# =========================
# 日志
# =========================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

logger = logging.getLogger("aliyun-monitor")


# =========================
# 读取配置
# =========================

with open("config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

telegram = config["telegram"]

BOT_TOKEN = telegram["token"]
CHAT_ID = telegram["chat_id"]

INTERVAL = config.get("interval", 3600)

ACCOUNTS = config["accounts"]


# =========================
# Telegram
# =========================

def send_message(text: str):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    try:

        r = httpx.post(
            url,
            json={
                "chat_id": CHAT_ID,
                "text": text,
                "parse_mode": "Markdown"
            },
            timeout=15
        )

        if r.status_code == 200:
            logger.info("Telegram 推送成功")
        else:
            logger.error(r.text)

    except Exception as e:
        logger.error(e)


# =========================
# 阿里云 Client
# =========================

def create_client(keyid, keysecret, country):

    cfg = open_api_models.Config(
        access_key_id=keyid,
        access_key_secret=keysecret
    )

    if country.upper() == "CN":
        cfg.endpoint = "business.aliyuncs.com"
    else:
        cfg.endpoint = "business.ap-southeast-1.aliyuncs.com"

    return Client(cfg)


# =========================
# 查询余额
# =========================

def query_balance(account):

    try:

        client = create_client(
            account["keyid"],
            account["keysecret"],
            account["country"]
        )

        runtime = util_models.RuntimeOptions()

        response = client.query_account_balance_with_options(runtime)

        balance = float(
            response.body.data.available_amount.replace(",", "")
        )

        currency = response.body.data.currency

        logger.info(
            "%s -> %.2f %s",
            account["name"],
            balance,
            currency
        )

        return {
            "ok": True,
            "balance": balance,
            "currency": currency
        }

    except Exception as e:

        logger.exception(e)

        return {
            "ok": False,
            "error": str(e)
        }




# =========================
# 告警消息
# =========================

def build_alarm(account, result):

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return f"""🚨 *阿里云余额告警*

━━━━━━━━━━━━━━━━━━

☁️ *{account['name']}*
👤 账号：`{account['account']}`
📂 分组：{account['group']}
🌍 区域：{"中国站" if account["country"].upper()=="CN" else "国际站"}
💰 当前余额：*{result['balance']:.2f} {result['currency']}*
⚠️ 告警阈值：*{account['threshold']} {result['currency']}*

🕒 {now}
"""


def build_error(account, error):

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return f"""❌ *阿里云余额查询失败*

━━━━━━━━━━━━━━━━━━

☁️ *{account['name']}*
👤 账号：`{account['account']}`
📂 分组：{account['group']}
🌍 区域：{"中国站" if account["country"].upper()=="CN" else "国际站"}
📄 错误：{error}

🕒 {now}
"""


# =========================
# 检查一个账号
# =========================

def check_account(account):

    result = query_balance(account)

    if not result["ok"]:

        logger.error("%s 查询失败", account["name"])

        send_message(
            build_error(
                account,
                result["error"]
            )
        )

        return

    balance = result["balance"]

    threshold = float(account["threshold"])

    if balance <= threshold:

        logger.warning(
            "%s 余额不足 %.2f %s",
            account["name"],
            balance,
            result["currency"]
        )

        send_message(
            build_alarm(
                account,
                result
            )
        )

    else:

        logger.info(
            "%s 正常 %.2f %s",
            account["name"],
            balance,
            result["currency"]
        )


# =========================
# 检查全部账号
# =========================

def check_all():

    logger.info("=" * 60)
    logger.info("开始检查阿里云余额")

    for account in ACCOUNTS:

        try:

            check_account(account)

        except Exception:

            logger.exception(
                "检查账号失败：%s",
                account["name"]
            )

    logger.info("检查完成")
    logger.info("=" * 60)


# =========================
# main
# =========================

if __name__ == "__main__":

    logger.info("Aliyun Balance Monitor 启动")

    while True:

        try:

            check_all()

        except Exception:

            logger.exception("本轮检查异常")

        logger.info(
            "休眠 %s 秒...",
            INTERVAL
        )

        time.sleep(INTERVAL)
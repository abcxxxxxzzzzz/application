from cloudflare import Cloudflare

import cloudflare


class CloudflareError(Exception):
    pass


class CloudflareService:

    def __init__(self, api_token: str):
        self.client = Cloudflare(
            api_token=api_token,
        )

    # ---------------------------------------------------------
    # Token
    # ---------------------------------------------------------

    def verify_token(self) -> dict:
    
        try:
            response = self.client.user.tokens.verify()

            return {
                "id": response.id,
                "status": response.status,
            }

        except cloudflare.AuthenticationError as e:
            raise CloudflareError(
                "Cloudflare API Token 无效"
            ) from e

        except cloudflare.PermissionDeniedError as e:
            raise CloudflareError(
                "Cloudflare API Token 没有权限"
            ) from e

        except cloudflare.RateLimitError as e:
            raise CloudflareError(
                "Cloudflare API 请求频率过高，请稍后再试"
            ) from e

        except cloudflare.APIConnectionError as e:
            raise CloudflareError(
                "无法连接 Cloudflare API"
            ) from e

        except cloudflare.APIStatusError as e:
            raise CloudflareError(
                f"Cloudflare API 请求失败: HTTP {e.status_code}"
            ) from e

    # ---------------------------------------------------------
    # 获取 Zone ID
    # ---------------------------------------------------------
    def get_zone_id(self, name: str) -> str:
        """
        获取 Cloudflare Zone ID。
        """
        name = name.strip().rstrip(".").lower()

        zones = self.client.zones.list(name=name)

        if not zones.result:
            raise RuntimeError(f"Cloudflare Zone 不存在: {name}")

        zone = next(
            (
                z for z in zones.result
                if z.name.strip().rstrip(".").lower() == name
            ),
            None,
        )

        if zone is None:
            raise RuntimeError(
                f"Cloudflare Zone 未找到精确匹配: {name}，"
                f"查询结果: {[z.name for z in zones.result]}"
            )

        return zone.id


    async def get_zone(
        self,
        zone_id: str,
    ):
        """
        根据 Zone ID 获取 Zone。
        """
        try:
            zone = await self.client.zones.get(
                zone_id=zone_id,
            )

            return zone

        except Exception as e:
            raise CloudflareError(
                f"获取 Cloudflare Zone 失败: {e}"
            ) from e

    def find_zone_id_for_domain(self, domain: str,):
        """
        根据 顶级域名获取 Cloudflare zone id
        """

        domain = domain.lower().rstrip(".")

        parts = domain.split(".")

        if len(parts) < 2:
            raise CloudflareError(
                f"无效域名: {domain}"
            )

        # 只取顶级 Zone
        zone_name = ".".join(parts[-2:])

        zone_id = self.get_zone_id(name=zone_name)

        return zone_id

    # ---------------------------------------------------------
    # 获取 Zone 下所有 DNS 记录。
    # ---------------------------------------------------------

    def list_records(self, zone_id: str) -> list:
        """
        获取 Zone 下所有 DNS 记录。
        """
        records = self.client.dns.records.list(
            zone_id=zone_id,
        )

        return records.result or [] 

    # ---------------------------------------------------------
    # 查找指定域名的 CNAME 记录。
    # ---------------------------------------------------------
    def get_cname_record(self, zone_id: str, name: str,):
        """
        查找指定域名的 CNAME 记录。
        """
        records = self.list_records(zone_id)

        name = name.rstrip(".").lower()

        for record in records:
            if (
                record.type == "CNAME"
                and record.name.rstrip(".").lower() == name
            ):
                return record

        return None



    # ---------------------------------------------------------
    # CNAME：
    #     - 已存在：更新
    #     - 不存在：创建
    # ---------------------------------------------------------
    def upsert_cname(self, zone_id: str, name: str, content: str, ttl: int = 60, proxied: bool = True):
        """
        CNAME：
        - 已存在：更新
        - 不存在：创建
        """
        name = name.rstrip(".")

        # 1. 查询现有记录
        record = self.get_cname_record(zone_id=zone_id, name=name)

        # 2. 已存在，更新
        if record:
            print(f"[UPDATE] CNAME {name}: "f"{record.content} -> {content}")

            response = self.client.dns.records.edit(
                dns_record_id=record.id,
                zone_id=zone_id,
                name=name,
                ttl=ttl,
                type="CNAME",
                content=content,
                proxied=proxied,
            )

            return response

        # 3. 不存在，创建
        print(f"[CREATE] CNAME {name} -> {content}")

        response = self.client.dns.records.create(
            zone_id=zone_id,
            name=name,
            ttl=ttl,
            type="CNAME",
            content=content,
            proxied=proxied,
        )

        return response
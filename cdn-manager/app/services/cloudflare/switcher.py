class CDNService:

    def __init__(self, account):
        self.cloudflare = CloudflareService(
            api_token=account.api_token,
        )

    async def switch_to_cf(
        self,
        domain: Domain,
    ):
        record = await self.cloudflare.get_dns_record(
            domain.domain_zone_id,
            domain.domain,
        )

        if record is None:
            raise CloudflareError(
                f"DNS Record 不存在: {domain.domain}"
            )

        if record["type"] != "CNAME":
            raise CloudflareError(
                f"{domain.domain} 不是 CNAME 记录"
            )

        return await self.cloudflare.update_dns_record(
            domain.domain_zone_id,
            record["id"],
            record_type="CNAME",
            name=record["name"],
            content=record["content"],
            proxied=True,
            ttl=record.get("ttl", 1),
        )

    async def switch_to_aws(
        self,
        domain: Domain,
    ):
        if not domain.target_cname:
            raise CloudflareError(
                "未配置 target_cname"
            )

        record = await self.cloudflare.get_dns_record(
            domain.domain_zone_id,
            domain.domain,
        )

        if record is None:
            raise CloudflareError(
                f"DNS Record 不存在: {domain.domain}"
            )

        if record["type"] != "CNAME":
            raise CloudflareError(
                f"{domain.domain} 不是 CNAME 记录"
            )

        return await self.cloudflare.update_dns_record(
            domain.domain_zone_id,
            record["id"],
            record_type="CNAME",
            name=record["name"],
            content=domain.target_cname,
            proxied=False,
            ttl=record.get("ttl", 1),
        )
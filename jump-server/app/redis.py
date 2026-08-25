import json

from redis.asyncio import Redis

from .config import settings


redis = Redis.from_url(
    settings.redis_url,
    encoding="utf-8",
    decode_responses=True,
)


def normalize_domain(
    domain: str,
) -> str:
    return (
        domain
        .strip()
        .lower()
        .rstrip(".")
    )


def domain_cache_key(
    domain: str,
) -> str:
    domain = normalize_domain(
        domain
    )

    return f"jump:domain:{domain}"


async def get_domain_cache(
    domain: str,
):
    key = domain_cache_key(
        domain
    )

    value = await redis.get(key)

    if not value:
        return None

    try:
        return json.loads(value)
    except Exception:
        return None


async def set_domain_cache(
    domain: str,
    data: dict,
    ttl: int | None = None,
):
    key = domain_cache_key(
        domain
    )

    await redis.set(
        key,
        json.dumps(
            data,
            ensure_ascii=False,
        ),
        ex=ttl or settings.cache_ttl,
    )


async def delete_domain_cache(
    domain: str,
):
    await redis.delete(
        domain_cache_key(
            domain
        )
    )


async def delete_domain_caches(
    domains: list[str],
):
    if not domains:
        return

    keys = [
        domain_cache_key(domain)
        for domain in domains
    ]

    await redis.delete(*keys)


async def delete_all_domain_caches():
    pattern = "jump:domain:*"

    cursor = 0
    deleted = 0

    while True:
        cursor, keys = await redis.scan(
            cursor=cursor,
            match=pattern,
            count=1000,
        )

        if keys:
            deleted += await redis.delete(*keys)

        if cursor == 0:
            break

    return deleted


async def close_redis():
    await redis.aclose()
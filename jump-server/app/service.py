import random
import secrets
import string

from .redis import (
    get_domain_cache,
    set_domain_cache,
)

# 延迟导入，避免循环依赖
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from .database import SessionLocal
from .models import Domain


RANDOM_CHARS = (
    string.ascii_lowercase
    + string.digits
)


def normalize_host(host: str) -> str:
    host = host.strip().lower()

    if ":" in host:
        host = host.split(":", 1)[0]

    return host.rstrip(".")


def random_subdomain(
    length: int = 10,
) -> str:
    return "".join(
        secrets.choice(RANDOM_CHARS)
        for _ in range(length)
    )


def generate_wildcard_target(
    target: str,
) -> str:
    if not target:
        return ""

    if "*" not in target:
        return target

    return target.replace(
        "*",
        random_subdomain(),
        1,
    )


def choose_random_pool(
    pool: list[dict],
) -> str | None:

    enabled = [
        item
        for item in pool
        if item.get("enabled", True)
        and item.get("target_domain")
    ]

    if not enabled:
        return None

    total_weight = sum(
        max(
            1,
            int(
                item.get(
                    "weight",
                    1,
                )
            ),
        )
        for item in enabled
    )

    value = random.randint(
        1,
        total_weight,
    )

    current = 0

    for item in enabled:
        current += max(
            1,
            int(
                item.get(
                    "weight",
                    1,
                )
            ),
        )

        if value <= current:
            return item["target_domain"]

    return enabled[-1]["target_domain"]


def resolve_target(
    config: dict,
) -> str | None:

    jump_type = config.get(
        "jump_type"
    )

    if jump_type == "direct":
        return config.get(
            "target_domain"
        )

    if jump_type == "wildcard":
        return generate_wildcard_target(
            config.get(
                "target_domain"
            )
        )

    if jump_type == "random":
        target = choose_random_pool(
            config.get(
                "pool",
                [],
            )
        )

        if target and "*" in target:
            target = generate_wildcard_target(
                target
            )

        return target

    return None


async def get_domain_config(
    host: str,
) -> dict | None:

    host = normalize_host(host)

    if not host:
        return None

    cached = await get_domain_cache(
        host
    )

    if cached is not None:
        return cached



    async with SessionLocal() as db:

        result = await db.execute(
            select(Domain)
            .options(
                selectinload(Domain.pool),
                selectinload(Domain.group),
            )
            .where(
                Domain.domain == host,
                Domain.enabled.is_(True),
            )
        )

        domain = (
            result
            .scalar_one_or_none()
        )

        if not domain:
            return None

        data = {
            "id": domain.id,
            "domain": domain.domain,
            "group_id": domain.group_id,
            "jump_type": domain.jump_type,
            "jump_method": domain.jump_method,
            "status_code": domain.status_code,
            "target_domain":
                domain.target_domain,
            "embedded_code":
                domain.embedded_code,
            "enabled": domain.enabled,

            # 域名是否使用分组参数
            "use_group_params": domain.use_group_params,

            # 分组信息
            "group": (
                {
                    "id": domain.group.id,
                    "name": domain.group.name,
                    "custom_params": domain.group.custom_params,
                }
                if domain.group
                else None
            ),

             # 随机池
            "pool": [
                {
                    "id": item.id,
                    "target_domain":
                        item.target_domain,
                    "weight": item.weight,
                    "enabled": item.enabled,
                }
                for item in domain.pool
            ],
        }

        await set_domain_cache(
            host,
            data,
        )

        return data
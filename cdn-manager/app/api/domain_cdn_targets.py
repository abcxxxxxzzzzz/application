from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import Domain, DomainCDNTarget
from app.schemas.domain_cdn_target import (
    DomainCDNTargetCreate,
    DomainCDNTargetResponse,
    DomainCDNTargetUpdate,
)
from app.core.auth import require_auth

router = APIRouter(
    prefix="/api",
    tags=["Domain CDN Targets"],
    dependencies=[Depends(require_auth)],
)


def normalize_cdn(cdn: str) -> str:
    return cdn.strip().lower()


def normalize_cname(cname: str) -> str:
    return cname.strip().lower().rstrip(".")


async def get_domain(
    domain_id: int,
    db: AsyncSession,
) -> Domain:
    result = await db.execute(
        select(Domain).where(
            Domain.id == domain_id
        )
    )

    domain = result.scalar_one_or_none()

    if domain is None:
        raise HTTPException(
            status_code=404,
            detail="域名不存在",
        )

    return domain


@router.post(
    "/domains/{domain_id}/cdn-targets",
    response_model=DomainCDNTargetResponse,
)
async def create_cdn_target(
    domain_id: int,
    data: DomainCDNTargetCreate,
    db: AsyncSession = Depends(get_db),
):
    
    print("!!!!!!!!!! CDN TARGET CREATE V2 !!!!!!!!!!")
    print(f"=========接受到： {data.proxied}")

    # 1. 检查 Domain
    await get_domain(domain_id, db)

    cdn = normalize_cdn(data.cdn)
    cname = normalize_cname(data.cname)

    # 2. 检查是否已经配置
    result = await db.execute(
        select(DomainCDNTarget).where(
            DomainCDNTarget.domain_id == domain_id,
            DomainCDNTarget.cdn == cdn,
        )
    )

    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=400,
            detail=f"{cdn} CDN 已经配置",
        )

    # 3. 创建
    target = DomainCDNTarget(
        domain_id=domain_id,
        cdn=cdn,
        cname=cname,
        proxied=data.proxied,
    )

    db.add(target)

    await db.commit()
    await db.refresh(target)

    return target


@router.get(
    "/domains/{domain_id}/cdn-targets",
    response_model=list[DomainCDNTargetResponse],
)
async def list_cdn_targets(
    domain_id: int,
    db: AsyncSession = Depends(get_db),
):
    await get_domain(domain_id, db)

    result = await db.execute(
        select(DomainCDNTarget)
        .where(
            DomainCDNTarget.domain_id == domain_id
        )
        .order_by(DomainCDNTarget.id.asc())
    )

    return result.scalars().all()


@router.put(
    "/domains/{domain_id}/cdn-targets/{target_id}",
    response_model=DomainCDNTargetResponse,
)
async def update_cdn_target(
    domain_id: int,
    target_id: int,
    data: DomainCDNTargetUpdate,
    db: AsyncSession = Depends(get_db),
):
    await get_domain(domain_id, db)

    # 1. 获取 Target
    result = await db.execute(
        select(DomainCDNTarget).where(
            DomainCDNTarget.id == target_id,
            DomainCDNTarget.domain_id == domain_id,
        )
    )

    target = result.scalar_one_or_none()

    if target is None:
        raise HTTPException(
            status_code=404,
            detail="CDN Target 不存在",
        )

    new_cdn = (
        normalize_cdn(data.cdn)
        if data.cdn is not None
        else target.cdn
    )

    new_cname = (
        normalize_cname(data.cname)
        if data.cname is not None
        else target.cname
    )


    # 2. 如果 CDN 名称发生变化，检查唯一性
    if new_cdn != target.cdn:
        result = await db.execute(
            select(DomainCDNTarget).where(
                DomainCDNTarget.domain_id == domain_id,
                DomainCDNTarget.cdn == new_cdn,
                DomainCDNTarget.id != target_id,
            )
        )

        if result.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=400,
                detail=f"{new_cdn} CDN 已经配置",
            )

    target.cdn = new_cdn
    target.cname = new_cname
    target.proxied = data.proxied

    await db.commit()
    await db.refresh(target)

    return target


@router.delete(
    "/domains/{domain_id}/cdn-targets/{target_id}",
)
async def delete_cdn_target(
    domain_id: int,
    target_id: int,
    db: AsyncSession = Depends(get_db),
):
    await get_domain(domain_id, db)

    result = await db.execute(
        select(DomainCDNTarget).where(
            DomainCDNTarget.id == target_id,
            DomainCDNTarget.domain_id == domain_id,
        )
    )

    target = result.scalar_one_or_none()

    if target is None:
        raise HTTPException(
            status_code=404,
            detail="CDN Target 不存在",
        )

    await db.delete(target)
    await db.commit()

    return {
        "success": True,
        "message": "CDN Target 删除成功",
    }
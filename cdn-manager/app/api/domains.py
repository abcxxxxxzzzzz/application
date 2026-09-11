from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import require_auth
from app.core.database import get_db
from app.models.cdn_account import CDNAccount
from app.models.domain import Domain
from app.models.domain_cdn_target import DomainCDNTarget
from app.models.group import Group
from app.schemas.domain import (
    DomainCreate,
    DomainResponse,
    DomainSwitchRequest,
    DomainUpdate,
)

from app.schemas.domain_cdn_target import (
    DomainCDNTargetCreate,
    DomainCDNTargetResponse,
    DomainCDNTargetUpdate,
)

from app.services.cloudflare import (
    CloudflareError,
    CloudflareService,
)


router = APIRouter(
    tags=["Domains"],
    dependencies=[Depends(require_auth)],
)


# ============================================================
# 工具函数
# ============================================================

def normalize_domain(value: str) -> str:
    return value.strip().lower().rstrip(".")


def normalize_cdn(value: str) -> str:
    return value.strip().lower()


def normalize_cname(value: str) -> str:
    return value.strip().lower().rstrip(".")


async def get_domain_or_404(
    db: AsyncSession,
    domain_id: int,
) -> Domain:

    result = await db.execute(
        select(Domain)
        .where(Domain.id == domain_id)
    )

    domain = result.scalar_one_or_none()

    if domain is None:
        raise HTTPException(
            status_code=404,
            detail="域名不存在",
        )

    return domain


async def get_group_or_404(
    db: AsyncSession,
    group_id: int,
) -> Group:

    result = await db.execute(
        select(Group)
        .where(Group.id == group_id)
    )

    group = result.scalar_one_or_none()

    if group is None:
        raise HTTPException(
            status_code=404,
            detail="分组不存在",
        )

    return group


async def get_cdn_account_or_404(
    db: AsyncSession,
    account_id: int,
) -> CDNAccount:

    result = await db.execute(
        select(CDNAccount)
        .where(CDNAccount.id == account_id)
    )

    account = result.scalar_one_or_none()

    if account is None:
        raise HTTPException(
            status_code=404,
            detail="Cloudflare 账号不存在",
        )

    return account


# ============================================================
# Domain CRUD
# ============================================================

@router.post(
    "/api/groups/{group_id}/domains",
    response_model=DomainResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_domain(
    group_id: int,
    data: DomainCreate,
    db: AsyncSession = Depends(get_db),
):
    # --------------------------------------------------------
    # 1. 检查 Group
    # --------------------------------------------------------

    group = await get_group_or_404(
        db,
        group_id,
    )


    # --------------------------------------------------------
    # 2. 检查 Cloudflare Account
    # --------------------------------------------------------

    account = await get_cdn_account_or_404(
        db,
        data.cdn_account_id,
    )


    # --------------------------------------------------------
    # 3. 标准化域名
    # --------------------------------------------------------

    domain_name = normalize_domain(
        data.domain
    )


    if not domain_name:
        raise HTTPException(
            status_code=400,
            detail="域名不能为空",
        )


    # --------------------------------------------------------
    # 4. 检查域名是否已经存在
    # --------------------------------------------------------

    result = await db.execute(
        select(Domain.id)
        .where(Domain.domain == domain_name)
        .limit(1)
    )

    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=400,
            detail="该域名已经存在",
        )


    # --------------------------------------------------------
    # 5. Cloudflare 查找 ZoneId
    # --------------------------------------------------------

    cf = CloudflareService(account.api_token)

    try:
        zone_id = cf.find_zone_id_for_domain(domain_name)
    except CloudflareError as exc:
        raise HTTPException(status_code=400, detail=f"获取 Cloudflare Zone 失败: {exc}",)


    # # --------------------------------------------------------
    # # 6. 确定 CDN 类型
    # # --------------------------------------------------------
    # cdn = normalize_cdn(data.desired_cdn)


    # # --------------------------------------------------------
    # # 7. Cloudflare DNS 配置
    # # --------------------------------------------------------
    # if cdn == "cf":
    #     # ----------------------------------------------------
    #     # CF CDN
    #     #
    #     # Cloudflare 作为 CDN 代理
    #     # CNAME -> CF CDN 目标
    #     # proxied=True
    #     # ----------------------------------------------------
    #     cf.upsert_cname(
    #         zone_id=zone_id,
    #         name=domain_name,
    #         content=group.origin_address,
    #         proxied=True,
    #     )

    # else:
    #     # ----------------------------------------------------
    #     # 非 CF CDN
    #     #
    #     # Cloudflare 只作为 DNS
    #     # CNAME -> 实际 CDN
    #     # 不开启 Cloudflare Proxy
    #     # proxied=False
    #     # ----------------------------------------------------

    #     result = await db.execute(
    #         select(DomainCDNTarget)
    #         .where(
    #             DomainCDNTarget.domain_id == domain.id,
    #             DomainCDNTarget.cdn == cdn,
    #         )
    #     )

    #     target = result.scalar_one_or_none()

    #     if target is None:
    #         raise HTTPException(
    #             status_code=400,
    #             detail=(
    #                 f"域名 {domain.domain} "
    #                 f"没有配置 CDN [{cdn}] 的 CNAME"
    #             ),
    #         )

    #     content = normalize_cname(target.cname)
    #     proxied = False
    #     cf.upsert_cname(
    #         zone_id=zone_id,
    #         name=domain_name,
    #         content=content,
    #         proxied=False,
    #     )

    # --------------------------------------------------------
    # 8. 创建 Domain
    # --------------------------------------------------------

    domain = Domain(
        group_id=group.id,
        cdn_account_id=account.id,
        domain_zone_id=zone_id,
        domain=domain_name,
        # desired_cdn=cdn,
        enabled=data.enabled,
    )

    db.add(domain)

    await db.commit()

    await db.refresh(domain)

    return domain


# ============================================================
# Group Domains
# ============================================================

@router.get(
    "/api/groups/{group_id}/domains",
    response_model=list[DomainResponse],
)
async def list_group_domains(
    group_id: int,
    db: AsyncSession = Depends(get_db),
):
    await get_group_or_404(
        db,
        group_id,
    )

    result = await db.execute(
        select(Domain)
        .where(Domain.group_id == group_id)
        .order_by(Domain.id.desc())
    )

    return list(
        result.scalars().all()
    )


# ============================================================
# Domain Detail
# ============================================================

@router.get(
    "/api/domains/{domain_id}",
    response_model=DomainResponse,
)
async def get_domain(
    domain_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await get_domain_or_404(
        db,
        domain_id,
    )


# ============================================================
# Update Domain
# ============================================================

# @router.put("/api/domains/{domain_id}",response_model=DomainResponse,)
# async def update_domain(
#     domain_id: int,
#     data: DomainUpdate,
#     db: AsyncSession = Depends(get_db),
# ):
#     domain = await get_domain_or_404(
#         db,
#         domain_id,
#     )


#     # --------------------------------------------------------
#     # 确定新的域名
#     # --------------------------------------------------------

#     new_domain_name = domain.domain

#     if data.domain is not None:

#         new_domain_name = normalize_domain(
#             data.domain
#         )

#         if not new_domain_name:
#             raise HTTPException(
#                 status_code=400,
#                 detail="域名不能为空",
#             )


#     # --------------------------------------------------------
#     # 确定新的 Cloudflare Account
#     # --------------------------------------------------------

#     new_account_id = domain.cdn_account_id

#     if data.cdn_account_id is not None:
#         new_account_id = data.cdn_account_id


#     # --------------------------------------------------------
#     # 判断 Zone 是否需要重新获取
#     # --------------------------------------------------------

#     zone_changed = (
#         new_domain_name != domain.domain
#         or new_account_id != domain.cdn_account_id
#     )


#     account = await get_cdn_account_or_404(
#         db,
#         new_account_id,
#     )


#     # --------------------------------------------------------
#     # 域名全局唯一检查
#     # --------------------------------------------------------

#     if new_domain_name != domain.domain:

#         result = await db.execute(
#             select(Domain.id)
#             .where(
#                 Domain.domain == new_domain_name,
#                 Domain.id != domain.id,
#             )
#             .limit(1)
#         )

#         if result.scalar_one_or_none() is not None:
#             raise HTTPException(
#                 status_code=400,
#                 detail="该域名已经存在",
#             )


#     # --------------------------------------------------------
#     # 重新获取 Cloudflare Zone
#     # --------------------------------------------------------

#     if zone_changed:

#         cf = CloudflareService(account.api_token)

#         zone_id = await cf.find_zone_id_for_domain(new_domain_name)

#         domain.domain_zone_id = zone_id


#     # --------------------------------------------------------
#     # 更新字段
#     # --------------------------------------------------------

#     domain.domain = new_domain_name

#     domain.cdn_account_id = new_account_id


#     if data.desired_cdn is not None:

#         domain.desired_cdn = normalize_cdn(
#             data.desired_cdn
#         )


#     if data.enabled is not None:

#         domain.enabled = data.enabled


#     # --------------------------------------------------------
#     # 注意：
#     #
#     # switch_remark 不在这里修改
#     #
#     # 只有 /switch 成功之后才能修改
#     # --------------------------------------------------------

#     await db.commit()

#     await db.refresh(domain)

#     return domain


# ============================================================
# Delete Domain
# ============================================================

@router.delete(
    "/api/domains/{domain_id}",
)
async def delete_domain(
    domain_id: int,
    db: AsyncSession = Depends(get_db),
):
    domain = await get_domain_or_404(
        db,
        domain_id,
    )

    await db.delete(domain)

    await db.commit()

    return {
        "success": True,
        "message": "域名删除成功",
    }


# ============================================================
# CDN Target CRUD
# ============================================================

@router.post(
    "/api/domains/{domain_id}/cdn-targets",
    response_model=DomainCDNTargetResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_cdn_target(
    domain_id: int,
    data: DomainCDNTargetCreate,
    db: AsyncSession = Depends(get_db),
):
    await get_domain_or_404(
        db,
        domain_id,
    )


    cdn = normalize_cdn(
        data.cdn
    )

    cname = normalize_cname(
        data.cname
    )


    if not cdn:
        raise HTTPException(
            status_code=400,
            detail="CDN 不能为空",
        )


    if not cname:
        raise HTTPException(
            status_code=400,
            detail="CNAME 不能为空",
        )


    # --------------------------------------------------------
    # 检查重复
    # --------------------------------------------------------

    result = await db.execute(
        select(DomainCDNTarget.id)
        .where(
            DomainCDNTarget.domain_id == domain_id,
            DomainCDNTarget.cdn == cdn,
        )
        .limit(1)
    )

    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=400,
            detail=f"{cdn} 的 CNAME 已经配置",
        )


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


# ============================================================
# List CDN Targets
# ============================================================

@router.get(
    "/api/domains/{domain_id}/cdn-targets",
    response_model=list[DomainCDNTargetResponse],
)
async def list_cdn_targets(
    domain_id: int,
    db: AsyncSession = Depends(get_db),
):
    await get_domain_or_404(
        db,
        domain_id,
    )


    result = await db.execute(
        select(DomainCDNTarget)
        .where(
            DomainCDNTarget.domain_id == domain_id
        )
        .order_by(DomainCDNTarget.id.asc())
    )

    return list(
        result.scalars().all()
    )


# ============================================================
# Update CDN Target
# ============================================================

@router.put(
    "/api/domains/{domain_id}/cdn-targets/{target_id}",
    response_model=DomainCDNTargetResponse,
)
async def update_cdn_target(
    domain_id: int,
    target_id: int,
    data: DomainCDNTargetUpdate,
    db: AsyncSession = Depends(get_db),
):
    await get_domain_or_404(
        db,
        domain_id,
    )


    result = await db.execute(
        select(DomainCDNTarget)
        .where(
            DomainCDNTarget.id == target_id,
            DomainCDNTarget.domain_id == domain_id,
        )
    )

    target = result.scalar_one_or_none()


    if target is None:
        raise HTTPException(
            status_code=404,
            detail="CDN CNAME 配置不存在",
        )


    new_cdn = target.cdn

    if data.cdn is not None:
        new_cdn = normalize_cdn(
            data.cdn
        )


    new_cname = target.cname

    if data.cname is not None:
        new_cname = normalize_cname(
            data.cname
        )


    if not new_cdn:
        raise HTTPException(
            status_code=400,
            detail="CDN 不能为空",
        )


    if not new_cname:
        raise HTTPException(
            status_code=400,
            detail="CNAME 不能为空",
        )

    # --------------------------------------------------------
    # 检查 CDN 是否和其他记录冲突
    # --------------------------------------------------------

    result = await db.execute(
        select(DomainCDNTarget.id)
        .where(
            DomainCDNTarget.domain_id == domain_id,
            DomainCDNTarget.cdn == new_cdn,
            DomainCDNTarget.id != target_id,
        )
        .limit(1)
    )

    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=400,
            detail=f"{new_cdn} 的 CNAME 已经配置",
        )


    target.cdn = new_cdn
    target.cname = new_cname
    target.proxied = data.proxied,


    await db.commit()

    await db.refresh(target)

    return target


# ============================================================
# Delete CDN Target
# ============================================================

@router.delete(
    "/api/domains/{domain_id}/cdn-targets/{target_id}",
)
async def delete_cdn_target(
    domain_id: int,
    target_id: int,
    db: AsyncSession = Depends(get_db),
):
    await get_domain_or_404(
        db,
        domain_id,
    )


    result = await db.execute(
        select(DomainCDNTarget)
        .where(
            DomainCDNTarget.id == target_id,
            DomainCDNTarget.domain_id == domain_id,
        )
    )

    target = result.scalar_one_or_none()


    if target is None:
        raise HTTPException(
            status_code=404,
            detail="CDN CNAME 配置不存在",
        )


    await db.delete(target)

    await db.commit()


    return {
        "success": True,
        "message": "CDN CNAME 删除成功",
    }


# ============================================================
# CDN Switch
# ============================================================

@router.post("/api/domains/{domain_id}/switch")
async def switch_domain_cdn(
    domain_id: int,
    data: DomainSwitchRequest,
    db: AsyncSession = Depends(get_db),
):
    # --------------------------------------------------------
    # 1. Domain
    # --------------------------------------------------------

    domain = await get_domain_or_404(
        db,
        domain_id,
    )


    # --------------------------------------------------------
    # 2. enabled 检查
    # --------------------------------------------------------

    if not domain.enabled:
        raise HTTPException(
            status_code=400,
            detail="该域名已停用，不能切换 CDN",
        )


    # --------------------------------------------------------
    # 3. Group
    # --------------------------------------------------------

    await get_group_or_404(
        db,
        domain.group_id,
    )


    # --------------------------------------------------------
    # 4. Cloudflare Account
    # --------------------------------------------------------

    account = await get_cdn_account_or_404(
        db,
        domain.cdn_account_id,
    )


    cdn = normalize_cdn(data.cdn)


    if not cdn:
        raise HTTPException(
            status_code=400,
            detail="CDN 不能为空",
        )


    # --------------------------------------------------------
    # 5. Cloudflare Service
    # --------------------------------------------------------
    cf = CloudflareService(account.api_token)


    # --------------------------------------------------------
    # 6. 获取当前 CNAME
    # --------------------------------------------------------
    # record = await cf.get_dns_record(domain.domain_zone_id, domain.domain)




    # --------------------------------------------------------
    # 7. 确定新的 CNAME
    # CF 模式 proxied = true; 外部 CDN proxied = false
    # --------------------------------------------------------



    result = await db.execute(
        select(DomainCDNTarget)
        .where(
            DomainCDNTarget.domain_id == domain.id,
            DomainCDNTarget.cdn == cdn,
        )
    )

    target = result.scalar_one_or_none()


    if target is None:
        raise HTTPException(
            status_code=400,
            detail=(
                f"域名 {domain.domain} "
                f"没有配置 CDN [{cdn}] 的 CNAME"
            ),
        )


    content = normalize_cname(target.cname)
    proxied = bool(target.proxied)


    # --------------------------------------------------------
    # 8. Cloudflare API 修改 DNS
    # --------------------------------------------------------

    try:

        cf.upsert_cname(
            domain.domain_zone_id,
            name=domain.domain,
            content=content,
            proxied=proxied,
        )

    except CloudflareError as exc:

        # ----------------------------------------------------
        # 非常重要：
        #
        # API 失败：
        # 不修改 desired_cdn
        # 不修改 switch_remark
        # ----------------------------------------------------

        raise HTTPException(
            status_code=400,
            detail=f"Cloudflare DNS 切换失败: {exc}",
        )


    # --------------------------------------------------------
    # 9. Cloudflare 成功
    #
    # 只有这里才修改数据库状态
    # --------------------------------------------------------

    domain.desired_cdn = cdn

    domain.switch_remark = data.remark


    await db.commit()

    await db.refresh(domain)


    # --------------------------------------------------------
    # 10. 返回结果
    # --------------------------------------------------------

    return {
        "success": True,
        "message": f"已切换到 {cdn}",
        "domain": domain.domain,
        "cdn": cdn,
        "content": content,
        "proxied": proxied,
        "remark": domain.switch_remark,
    }
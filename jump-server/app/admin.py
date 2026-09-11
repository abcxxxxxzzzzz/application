from math import ceil
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)
from sqlalchemy import (
    delete,
    func,
    select,
    update,
    or_,
    exists,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .database import get_db
from .models import (
    Domain,
    DomainPool,
    Group,
)
from .redis import (
    delete_all_domain_caches,
    delete_domain_cache,
    delete_domain_caches,
)
from .schemas import (
    BatchCreateCheckItem,
    BatchCreateCheckResponse,
    BatchEnabled,
    BatchGroup,
    BatchGroupParamsRequest,
    BatchIds,
    BatchReplaceTargetDomainRequest,
    BatchStatus,
    BatchTargetCreateRequest,
    BatchTargetUpdate,
    BatchTargetUpdateResponse,
    DomainCreate,
    DomainListResponse,
    DomainResponse,
    DomainUpdate,
    GroupCreate,
    GroupResponse,
    GroupUpdate,
    BatchDomainSearch,
    BatchDomainSearchResponse,
    BatchDomainCreate,
    BatchCreateResponse
)
from .auth import require_admin
from .url import replace_target_hostname

router = APIRouter(
    prefix="/api/admin",
    tags=["admin"],
    dependencies=[
        Depends(require_admin)
    ],
)



## 分组列表
# @router.get(
#     "/groups",
#     response_model=list[GroupResponse],
# )
# async def list_groups(
#     db: AsyncSession = Depends(get_db),
# ):
#     result = await db.execute(
#         select(Group)
#         .order_by(
#             Group.id.desc()
#         )
#     )

#     return result.scalars().all()
@router.get("/groups")
async def list_groups(
    db: AsyncSession = Depends(get_db),
):
    domain_counts = (
        select(
            Domain.group_id,
            func.count(Domain.id).label(
                "domain_count"
            ),
        )
        .group_by(
            Domain.group_id
        )
        .subquery()
    )

    result = await db.execute(
        select(
            Group.id,
            Group.name,
            Group.custom_params,
            func.coalesce(
                domain_counts.c.domain_count,
                0,
            ).label("domain_count"),
            Group.created_at,
            Group.updated_at,
        )
        .outerjoin(
            domain_counts,
            domain_counts.c.group_id
            == Group.id,
        )
        .order_by(
            Group.id.desc()
        )
    )

    items = [
        {
            "id": row.id,
            "name": row.name,
            "custom_params": row.custom_params,
            "domain_count": row.domain_count,
            "created_at": row.created_at,
            "updated_at": row.updated_at,
        }
        for row in result.all()
    ]

    return {
        "items": items
    }


## 创建分组
@router.post(
    "/groups",
    response_model=GroupResponse,
)
async def create_group(
    data: GroupCreate,
    db: AsyncSession = Depends(get_db),
):
    name = data.name.strip()
    custom_params = data.custom_params.strip()

    if not name:
        raise HTTPException(
            400,
            "分组名称不能为空",
        )

    exists = await db.scalar(
        select(Group).where(
            Group.name == name
        )
    )

    if exists:
        raise HTTPException(
            409,
            "分组名称已经存在",
        )

    group = Group(
        name=name,
        custom_params=custom_params
    )

    db.add(group)

    await db.commit()
    await db.refresh(group)

    return group


## 修改分组
@router.put(
    "/groups/{group_id}",
    response_model=GroupResponse,
)
async def update_group(
    group_id: int,
    data: GroupUpdate,
    db: AsyncSession = Depends(get_db),
):
    group = await db.get(
        Group,
        group_id,
    )

    if not group:
        raise HTTPException(
            404,
            "分组不存在",
        )

    name = data.name.strip()
    custom_params = data.custom_params.strip()

    exists = await db.scalar(
        select(Group).where(
            Group.name == name,
            Group.id != group_id,
        )
    )

    if exists:
        raise HTTPException(
            404,
            "分组名称已经存在",
        )

    # ==========================================
    # 获取当前分组下的所有域名
    # ==========================================

    result = await db.execute(
        select(Domain.domain).where(
            Domain.group_id == group_id
        )
    )

    domains = result.scalars().all()

    # ==========================================
    # 修改分组
    # ==========================================

    group.name = name
    group.custom_params = custom_params

    await db.commit()

    await db.refresh(group)

    # ==========================================
    # 清除该分组下所有域名的 Redis 缓存
    # ==========================================

    await delete_domain_caches(
        domains
    )

    return group


## 删除分组
@router.delete("/groups/{group_id}")
async def delete_group(
    group_id: int,
    db: AsyncSession = Depends(get_db),
):
    group = await db.get(Group, group_id)

    if not group:
        raise HTTPException(
            status_code=404,
            detail="分组不存在",
        )

    result = await db.execute(
        select(func.count(Domain.id))
        .where(Domain.group_id == group_id)
    )

    domain_count = result.scalar_one()

    if domain_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"该分组还有 {domain_count} 个域名，无法删除",
        )

    await db.delete(group)
    await db.commit()

    return {
        "success": True
    }


## 域名列表
@router.get(
    "/domains",
    response_model=DomainListResponse,
)
async def list_domains(
    page: int = Query(
        1,
        ge=1,
    ),
    page_size: int = Query(
        20,
        ge=1,
        le=2000,
    ),
    search: str | None = None,
    jump_type: str | None = None,
    enabled: bool | None = None,
    group_id: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    conditions = []

    # ==========================
    # 搜索
    # ==========================

    if search:
        keyword = search.strip()

        if keyword:
            search_pattern = f"%{keyword}%"

            conditions.append(
                or_(
                    # 域名
                    Domain.domain.ilike(
                        search_pattern
                    ),

                    # 直接跳转目标
                    Domain.target_domain.ilike(
                        search_pattern
                    ),

                    # 随机池目标
                    exists(
                        select(1)
                        .select_from(DomainPool)
                        .where(
                            DomainPool.domain_id
                            == Domain.id,

                            DomainPool.target_domain.ilike(
                                search_pattern
                            ),
                        )
                    ),
                )
            )

    # ==========================
    # 跳转类型
    # ==========================

    if jump_type:
        conditions.append(
            Domain.jump_type == jump_type
        )

    # ==========================
    # 启用状态
    # ==========================

    if enabled is not None:
        conditions.append(
            Domain.enabled == enabled
        )

    # ==========================
    # 分组
    # ==========================

    if group_id is not None:
        conditions.append(
            Domain.group_id == group_id
        )

    # ==========================
    # 总数
    # ==========================

    total = await db.scalar(
        select(
            func.count(Domain.id)
        ).where(
            *conditions
        )
    )

    total = total or 0

    pages = max(
        1,
        ceil(
            total / page_size
        ),
    )

    if page > pages:
        page = pages

    # ==========================
    # 查询
    # ==========================

    result = await db.execute(
        select(Domain)
        .options(
            # 随机池
            selectinload(
                Domain.pool
            ),

            # 分组
            selectinload(
                Domain.group
            ),
        )
        .where(
            *conditions
        )
        .order_by(
            Domain.id.desc()
        )
        .offset(
            (page - 1) * page_size
        )
        .limit(
            page_size
        )
    )

    items = result.scalars().all()

    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": pages,
    }


## 域名详情
@router.get(
    "/domains/{domain_id}",
    response_model=DomainResponse,
)
async def get_domain(
    domain_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Domain)
        .options(
            selectinload(
                Domain.pool
            )
        )
        .where(
            Domain.id == domain_id
        )
    )

    domain = (
        result
        .scalar_one_or_none()
    )

    if not domain:
        raise HTTPException(
            404,
            "域名不存在",
        )

    return domain


## 创建域名
@router.post(
    "/domains",
    response_model=DomainResponse,
)
async def create_domain(
    data: DomainCreate,
    db: AsyncSession = Depends(get_db),
):
    try:
        group = await db.get(
            Group,
            data.group_id,
        )

        if not group:
            raise HTTPException(
                status_code=400,
                detail="分组不存在",
            )

        result = await db.execute(
            select(Domain).where(
                Domain.domain == data.domain
            )
        )

        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail="域名已经存在",
            )

        validate_domain_data(
            data.jump_type,
            data.target_domain,
            data.pool,
        )

        domain = Domain(
            domain=data.domain,
            group_id=data.group_id,
            jump_type=data.jump_type,
            jump_method=data.jump_method,
            status_code=data.status_code,
            target_domain=data.target_domain,
            embedded_code=data.embedded_code,
            enabled=data.enabled,
            use_group_params=data.use_group_params,
        )

        db.add(domain)

        await db.flush()

        if data.jump_type == "random":

            for item in data.pool:

                db.add(
                    DomainPool(
                        domain_id=domain.id,
                        target_domain=item.target_domain,
                        weight=item.weight,
                        enabled=item.enabled,
                    )
                )

        await db.commit()

    except HTTPException:
        await db.rollback()
        raise

    except Exception:
        await db.rollback()
        raise

    result = await db.execute(
        select(Domain)
        .options(
            selectinload(Domain.pool)
        )
        .where(
            Domain.id == domain.id
        )
    )

    return result.scalar_one()

## 修改域名
@router.put(
    "/domains/{domain_id}",
    response_model=DomainResponse,
)
async def update_domain(
    domain_id: int,
    data: DomainUpdate,
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await db.execute(
            select(Domain).where(
                Domain.id == domain_id
            )
        )

        domain = result.scalar_one_or_none()

        if not domain:
            raise HTTPException(
                status_code=404,
                detail="域名不存在",
            )

        group = await db.get(
            Group,
            data.group_id,
        )

        if not group:
            raise HTTPException(
                status_code=400,
                detail="分组不存在",
            )

        exists = await db.scalar(
            select(Domain).where(
                Domain.domain == data.domain,
                Domain.id != domain_id,
            )
        )

        if exists:
            raise HTTPException(
                status_code=409,
                detail="域名已经存在",
            )

        validate_domain_data(
            data.jump_type,
            data.target_domain,
            data.pool,
        )

        old_domain = domain.domain

        domain.domain = data.domain
        domain.group_id = data.group_id
        domain.jump_type = data.jump_type
        domain.jump_method = data.jump_method
        domain.status_code = data.status_code
        domain.target_domain = data.target_domain
        domain.embedded_code = data.embedded_code
        domain.enabled = data.enabled
        domain.use_group_params = data.use_group_params

        await db.execute(
            delete(DomainPool).where(
                DomainPool.domain_id == domain_id
            )
        )

        if data.jump_type == "random":

            for item in data.pool:

                db.add(
                    DomainPool(
                        domain_id=domain_id,
                        target_domain=item.target_domain,
                        weight=item.weight,
                        enabled=item.enabled,
                    )
                )

        await db.commit()

    except HTTPException:
        await db.rollback()
        raise

    except Exception:
        await db.rollback()
        raise

    await delete_domain_caches(
        list(
            {
                old_domain,
                data.domain,
            }
        )
    )

    result = await db.execute(
        select(Domain)
        .options(
            selectinload(Domain.pool)
        )
        .where(
            Domain.id == domain_id
        )
    )

    return result.scalar_one()


## 删除域名
@router.delete(
    "/domains/{domain_id}"
)
async def delete_domain(
    domain_id: int,
    db: AsyncSession = Depends(get_db),
):
    domain = await db.get(
        Domain,
        domain_id,
    )

    if not domain:
        raise HTTPException(
            status_code=404,
            detail="域名不存在",
        )

    domain_name = domain.domain

    await db.delete(domain)

    await db.commit()

    # Redis 缓存失效
    await delete_domain_cache(
        domain_name
    )

    return {
        "success": True,
        "id": domain_id,
        "domain": domain_name,
    }


## 统一验证
def validate_domain_data(
    jump_type,
    target_domain,
    pool,
):
    if jump_type == "direct":

        if not target_domain:
            raise HTTPException(
                400,
                "直接跳转必须设置目标域名",
            )

    elif jump_type == "wildcard":

        if not target_domain:
            raise HTTPException(
                400,
                "泛域名跳转必须设置目标域名",
            )

        if "*" not in target_domain:
            raise HTTPException(
                400,
                "泛域名目标必须包含 *",
            )

    elif jump_type == "random":

        if not pool:
            raise HTTPException(
                400,
                "随机跳转至少需要一个随机池目标",
            )

        if not any(
            item.enabled
            for item in pool
        ):
            raise HTTPException(
                400,
                "随机池至少需要一个启用目标",
            )


## 批量接口
@router.post(
    "/domains/batch-enabled"
)
async def batch_enabled_domains(
    data: BatchEnabled,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Domain.id, Domain.domain).where(
            Domain.id.in_(data.ids)
        )
    )

    rows = result.all()

    if not rows:
        return {
            "success": True,
            "updated": 0,
        }

    names = [
        row.domain
        for row in rows
    ]

    try:
        result = await db.execute(
            update(Domain)
            .where(
                Domain.id.in_(data.ids)
            )
            .values(
                enabled=data.enabled
            )
        )

        await db.commit()

    except Exception:
        await db.rollback()
        raise

    await delete_domain_caches(names)

    return {
        "success": True,
        "updated": result.rowcount or 0,
        "enabled": data.enabled,
    }

## 批量修改分组
@router.post(
    "/domains/batch-group"
)
async def batch_group_domains(
    data: BatchGroup,
    db: AsyncSession = Depends(get_db),
):
    # 1. 检查分组
    group = await db.get(
        Group,
        data.group_id,
    )

    if not group:
        raise HTTPException(
            status_code=404,
            detail="分组不存在",
        )

    # 2. 获取实际存在的域名
    result = await db.execute(
        select(
            Domain.id,
            Domain.domain,
        ).where(
            Domain.id.in_(data.ids)
        )
    )

    rows = result.all()

    if not rows:
        return {
            "success": True,
            "updated": 0,
        }

    names = [
        row.domain
        for row in rows
    ]

    try:
        result = await db.execute(
            update(Domain)
            .where(
                Domain.id.in_(data.ids)
            )
            .values(
                group_id=data.group_id
            )
        )

        await db.commit()

    except Exception:
        await db.rollback()
        raise

    await delete_domain_caches(names)

    return {
        "success": True,
        "updated": result.rowcount or 0,
        "group_id": data.group_id,
    }



## 批量删除
@router.post(
    "/domains/batch-delete"
)
async def batch_delete_domains(
    data: BatchIds,
    db: AsyncSession = Depends(get_db),
):
    # 1. 先获取实际存在的域名
    result = await db.execute(
        select(
            Domain.id,
            Domain.domain,
        ).where(
            Domain.id.in_(data.ids)
        )
    )

    rows = result.all()

    if not rows:
        return {
            "success": True,
            "deleted": 0,
        }

    names = [
        row.domain
        for row in rows
    ]

    try:
        result = await db.execute(
            delete(Domain).where(
                Domain.id.in_(data.ids)
            )
        )

        await db.commit()

    except Exception:
        await db.rollback()
        raise

    await delete_domain_caches(names)

    return {
        "success": True,
        "deleted": result.rowcount or 0,
    }




## 批量搜索
@router.post(
    "/domains/search-batch",
    response_model=BatchDomainSearchResponse,
)
async def search_batch_domains(
    data: BatchDomainSearch,
    db: AsyncSession = Depends(get_db),
):
    if not data.domains:
        return {
            "items": [],
            "found": 0,
            "not_found": [],
        }

    result = await db.execute(
        select(Domain)
        .options(
            selectinload(Domain.pool)
        )
        .where(
            Domain.domain.in_(data.domains)
        )
        .order_by(
            Domain.id.desc()
        )
    )

    domains = result.scalars().all()

    domain_map = {
        item.domain: item
        for item in domains
    }

    items = []

    for name in data.domains:

        domain = domain_map.get(name)

        if domain:
            items.append(domain)

    not_found = [
        name
        for name in data.domains
        if name not in domain_map
    ]

    return {
        "items": items,
        "found": len(items),
        "not_found": not_found,
    }



## 批量创建+单目标
@router.post(
    "/domains/batch-create",
    response_model=BatchCreateResponse,
)
async def batch_create_domains(
    data: BatchDomainCreate,
    db: AsyncSession = Depends(get_db),
):
    # 1. 检查分组
    group = await db.get(
        Group,
        data.group_id,
    )

    if not group:
        raise HTTPException(
            status_code=404,
            detail="分组不存在",
        )

    # 2. 业务参数校验
    validate_domain_data(
        data.jump_type,
        data.target_domain,
        data.pool,
    )

    # 3. 随机跳转必须有随机池
    if data.jump_type == "random":

        if not data.pool:
            raise HTTPException(
                status_code=400,
                detail="随机跳转至少需要一个跳转域名",
            )

    # 4. 查询已经存在的域名
    result = await db.execute(
        select(Domain.domain).where(
            Domain.domain.in_(data.domains)
        )
    )

    exists = set(
        result.scalars().all()
    )

    # 5. 只创建不存在的
    create_names = [
        name
        for name in data.domains
        if name not in exists
    ]

    # 6. 全部已经存在
    if not create_names:

        return {
            "success": True,
            "total": len(data.domains),
            "created": 0,
            "skipped": len(exists),
            "items": [
                {
                    "domain": name,
                    "success": False,
                    "reason": "域名已经存在",
                }
                for name in data.domains
            ],
        }

    created_domains = []

    try:

        # 7. 创建 Domain
        for name in create_names:

            domain = Domain(
                domain=name,
                group_id=data.group_id,
                jump_type=data.jump_type,
                jump_method=data.jump_method,
                status_code=data.status_code,
                target_domain=(
                    data.target_domain
                    if data.jump_type != "random"
                    else None
                ),
                embedded_code=data.embedded_code,
                enabled=data.enabled,
                use_group_params=data.use_group_params,
            )

            db.add(domain)

            created_domains.append(domain)

        # 8. flush
        # 让所有 Domain 获得 ID
        await db.flush()

        # 9. 创建随机跳转池
        if data.jump_type == "random":

            pool_objects = []

            for domain in created_domains:

                for item in data.pool:

                    pool = DomainPool(
                        domain_id=domain.id,
                        target_domain=item.target_domain,
                        weight=item.weight,
                        enabled=item.enabled,
                    )

                    pool_objects.append(pool)

            if pool_objects:
                db.add_all(pool_objects)

        # 10. 提交
        await db.commit()

    except Exception:
        await db.rollback()
        raise

    # 11. 返回结果
    items = []

    for name in data.domains:

        if name in exists:

            items.append(
                {
                    "domain": name,
                    "success": False,
                    "reason": "域名已经存在",
                }
            )

        else:

            items.append(
                {
                    "domain": name,
                    "success": True,
                    "reason": None,
                }
            )

    return {
        "success": True,
        "total": len(data.domains),
        "created": len(create_names),
        "skipped": len(exists),
        "items": items,
    }


# 批量检查
@router.post(
    "/domains/batch-create/check",
    response_model=BatchCreateCheckResponse,
)
async def batch_create_check(
    data: BatchDomainCreate,
    db: AsyncSession = Depends(get_db),
):
    # =========================
    # 1. 检查分组
    # =========================

    group = await db.get(
        Group,
        data.group_id,
    )

    if not group:
        raise HTTPException(
            status_code=400,
            detail="分组不存在",
        )

    # =========================
    # 2. 检查域名
    # =========================

    domains = data.domains

    result = await db.execute(
        select(Domain.domain).where(
            Domain.domain.in_(domains)
        )
    )

    existing_domains = set(
        result.scalars().all()
    )

    # =========================
    # 3. 生成检查结果
    # =========================

    items = []

    can_create = 0
    exists = 0

    for domain in domains:

        if domain in existing_domains:

            items.append(
                BatchCreateCheckItem(
                    domain=domain,
                    can_create=False,
                    reason="域名已经存在",
                )
            )

            exists += 1

        else:

            items.append(
                BatchCreateCheckItem(
                    domain=domain,
                    can_create=True,
                )
            )

            can_create += 1

    return BatchCreateCheckResponse(
        total=len(domains),
        can_create=can_create,
        exists=exists,
        items=items,
    )




## 批量创建+多目标
@router.post("/domains/batch-target-create")
async def batch_target_create(
    data: BatchTargetCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    if not data.items:
        raise HTTPException(
            status_code=400,
            detail="没有可添加的数据",
        )

    # ==========================================
    # 1. 检查分组
    # ==========================================

    if data.group_id is not None:

        group = await db.scalar(
            select(Group).where(
                Group.id == data.group_id
            )
        )

        if not group:
            raise HTTPException(
                status_code=400,
                detail="指定的分组不存在",
            )

    # ==========================================
    # 2. 清理域名
    # ==========================================

    input_domains = []

    for item in data.items:

        domain = item.domain.strip().lower()

        if not domain:
            raise HTTPException(
                status_code=400,
                detail="存在空域名",
            )

        input_domains.append(domain)

    # ==========================================
    # 3. 检查本次提交内部重复
    # ==========================================

    seen = set()
    duplicate_domains = []

    for domain in input_domains:

        if domain in seen:
            duplicate_domains.append(domain)
        else:
            seen.add(domain)

    if duplicate_domains:

        duplicate_domains = list(
            dict.fromkeys(
                duplicate_domains
            )
        )

        raise HTTPException(
            status_code=400,
            detail={
                "message": "本次提交中存在重复域名",
                "domains": duplicate_domains,
            },
        )

    # ==========================================
    # 4. 查询数据库中已经存在的域名
    # ==========================================

    result = await db.execute(
        select(Domain.domain).where(
            Domain.domain.in_(input_domains)
        )
    )

    existing_domains = [
        row[0]
        for row in result.all()
    ]

    # ==========================================
    # 5. 存在任何重复，整批拒绝
    # ==========================================

    if existing_domains:

        raise HTTPException(
            status_code=409,
            detail={
                "message": "以下域名已经存在",
                "domains": existing_domains,
            },
        )

    # ==========================================
    # 6. 全部不存在，开始创建
    # ==========================================

    domains = []

    for item in data.items:

        domain = item.domain.strip().lower()

        domains.append(
            Domain(
                domain=domain,

                target_domain=
                    item.target_domain,

                jump_type=
                    item.jump_type,

                group_id=
                    data.group_id,

                jump_method=
                    data.jump_method,

                status_code=
                    data.status_code,

                enabled=
                    data.enabled,

                use_group_params=
                    data.use_group_params,

                embedded_code=
                    data.embedded_code,
            )
        )

    db.add_all(domains)

    await db.commit()

    return {
        "created": len(domains),
        "total": len(domains),
    }



# 批量更新目标地址
@router.post(
    "/domains/batch-update-target",
    response_model=BatchTargetUpdateResponse,
)
async def batch_update_target(
    data: BatchTargetUpdate,
    db: AsyncSession = Depends(get_db),
):

    old_target = data.old_target_domain

    new_target = data.new_target_domain


    if old_target == new_target:

        raise HTTPException(
            status_code=400,
            detail="新旧目标地址不能相同",
        )


    # 查询需要清理缓存的域名
    result = await db.execute(
        select(Domain.domain).where(
            Domain.target_domain
            == old_target,

            Domain.jump_type
            != "random",
        )
    )

    domain_names = list(
        result.scalars().all()
    )


    if not domain_names:

        return {
            "success": True,
            "updated": 0,
        }


    # 批量更新
    await db.execute(
        update(Domain)
        .where(
            Domain.target_domain
            == old_target,

            Domain.jump_type
            != "random",
        )
        .values(
            target_domain=new_target
        )
    )


    await db.commit()


    # 清理 Redis 缓存
    await delete_domain_caches(
        domain_names
    )


    return {
        "success": True,
        "updated": len(domain_names),
    }



# 批量更新状态码
@router.post(
    "/domains/batch-status"
)
async def batch_status_domains(
    data: BatchStatus,
    db: AsyncSession = Depends(get_db),
):

    result = await db.execute(
        select(Domain).where(
            Domain.id.in_(data.ids)
        )
    )

    domains = result.scalars().all()

    if not domains:

        return {
            "success": True,
            "updated": 0,
        }

    names = [
        item.domain
        for item in domains
    ]

    for domain in domains:

        domain.status_code = (
            data.status_code
        )

    await db.commit()

    await delete_domain_caches(
        names
    )

    return {
        "success": True,
        "updated": len(domains),
    }



##################################
# 批量更新目标顶级域名
##################################
@router.post("/domains/batch-replace-target-domain")
async def batch_replace_target_domain(
    data: BatchReplaceTargetDomainRequest,
    db: AsyncSession = Depends(get_db),
):

    if not data.domain_ids:
        raise HTTPException(
            status_code=400,
            detail="请选择需要处理的域名",
        )

    old_domain = data.old_domain.strip().lower()
    new_domain = data.new_domain.strip().lower()

    if not old_domain:
        raise HTTPException(
            status_code=400,
            detail="原顶级域名不能为空",
        )

    if not new_domain:
        raise HTTPException(
            status_code=400,
            detail="新顶级域名不能为空",
        )

    if old_domain == new_domain:
        raise HTTPException(
            status_code=400,
            detail="原域名和新域名不能相同",
        )

    result = await db.execute(
        select(Domain)
        .options(
            selectinload(Domain.pool)
        )
        .where(
            Domain.id.in_(data.domain_ids)
        )
    )

    domains = (
        result
        .scalars()
        .unique()
        .all()
    )

    if not domains:
        raise HTTPException(
            status_code=404,
            detail="没有找到对应域名",
        )

    updated_domains = 0
    updated_targets = 0

    # 需要清理 Redis 的域名
    domain_names = []


    for domain in domains:

        domain_changed = False

        # 普通目标地址
        if domain.target_domain:

            new_target = replace_target_hostname(
                domain.target_domain,
                old_domain,
                new_domain,
            )

            if (
                new_target
                and new_target != domain.target_domain
            ):

                domain.target_domain = new_target

                updated_targets += 1
                domain_changed = True

        # 随机目标池
        for pool in domain.pool:

            if not pool.target_domain:
                continue

            new_target = replace_target_hostname(
                pool.target_domain,
                old_domain,
                new_domain,
            )

            if (
                new_target
                and new_target != pool.target_domain
            ):

                pool.target_domain = new_target

                updated_targets += 1
                domain_changed = True


        if domain_changed:
            updated_domains += 1

            # 只要这个域名任意目标发生变化，就清理一次 Redis
            domain_names.append(domain.domain)    

    await db.commit()

    # 清理 Redis
    if domain_names:
        await delete_domain_caches(domain_names)

    return {
        "updated_domains": updated_domains,
        "updated_targets": updated_targets,
        "total_domains": len(domains),
    }



##################################
# 批量启用|禁用分组参数
##################################
@router.post("/domains/batch-group-params")
async def batch_group_params(
    data: BatchGroupParamsRequest,
    db: AsyncSession = Depends(get_db),
):
    if not data.domain_ids:
        raise HTTPException(
            status_code=400,
            detail="请选择需要处理的域名",
        )

    result = await db.execute(
        select(Domain).where(
            Domain.id.in_(data.domain_ids)
        )
    )

    domains = result.scalars().all()

    if not domains:
        raise HTTPException(
            status_code=404,
            detail="没有找到对应域名",
        )

    updated = 0

    for domain in domains:
        if (
            domain.use_group_params
            != data.use_group_params
        ):
            domain.use_group_params = (
                data.use_group_params
            )
            updated += 1

    await db.commit()

    # ==========================================
    # 清除选中域名的 Redis 缓存
    # ==========================================

    await delete_domain_caches(
        [
            domain.domain
            for domain in domains
        ]
    )

    return {
        "updated": updated,
        "total": len(domains),
        "use_group_params":
            data.use_group_params,
    }




##################################
# 批量清除所有域名Redis缓存
##################################
@router.delete("/domains/cache/all")
async def clear_all_domain_cache():

    deleted = await delete_all_domain_caches()

    return {
        "message": "所有域名缓存已清除",
        "deleted": deleted,
    }
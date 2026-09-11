from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.group import Group
from app.schemas.group import (
    GroupCreate,
    GroupResponse,
    GroupUpdate,
)
from fastapi import Depends

from app.core.auth import require_auth


router = APIRouter(
    prefix="/api/groups",
    tags=["Groups"],
    dependencies=[Depends(require_auth)],
)


@router.post(
    "",
    response_model=GroupResponse,
)
async def create_group(
    data: GroupCreate,
    db: AsyncSession = Depends(get_db),
):
    # 检查名称是否已经存在
    result = await db.execute(
        select(Group).where(
            Group.name == data.name
        )
    )

    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="Group 名称已存在",
        )

    group = Group(
        name=data.name,
        # origin_address=data.origin_address,
    )

    db.add(group)

    await db.commit()
    await db.refresh(group)

    return group


@router.get(
    "",
    response_model=list[GroupResponse],
)
async def list_groups(
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Group)
        .order_by(Group.id.desc())
    )

    return result.scalars().all()


@router.get(
    "/{group_id}",
    response_model=GroupResponse,
)
async def get_group(
    group_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Group).where(
            Group.id == group_id
        )
    )

    group = result.scalar_one_or_none()

    if group is None:
        raise HTTPException(
            status_code=404,
            detail="Group 不存在",
        )

    return group


@router.put(
    "/{group_id}",
    response_model=GroupResponse,
)
async def update_group(
    group_id: int,
    data: GroupUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Group).where(
            Group.id == group_id
        )
    )

    group = result.scalar_one_or_none()

    if group is None:
        raise HTTPException(
            status_code=404,
            detail="Group 不存在",
        )

    if data.name is not None:
        # 修改名称时检查重复
        result = await db.execute(
            select(Group).where(
                Group.name == data.name,
                Group.id != group_id,
            )
        )

        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail="Group 名称已存在",
            )

        group.name = data.name

    # if data.origin_address is not None:
    #     group.origin_address = data.origin_address

    await db.commit()
    await db.refresh(group)

    return group


@router.delete(
    "/{group_id}",
)
async def delete_group(
    group_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Group).where(
            Group.id == group_id
        )
    )

    group = result.scalar_one_or_none()

    if group is None:
        raise HTTPException(
            status_code=404,
            detail="Group 不存在",
        )

    await db.delete(group)
    await db.commit()

    return {
        "success": True,
        "message": "删除成功",
    }
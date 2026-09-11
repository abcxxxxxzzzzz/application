from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.cdn_account import CDNAccount
from app.schemas.cdn_account import (
    CDNAccountCreate,
    CDNAccountResponse,
    CDNAccountUpdate,
)

from app.models.domain import Domain
from app.core.auth import require_auth

router = APIRouter(
    prefix="/api/cdn-accounts",
    tags=["CDN Accounts"],
    dependencies=[Depends(require_auth)],
)


@router.post(
    "",
    response_model=CDNAccountResponse,
)
async def create_cdn_account(
    data: CDNAccountCreate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CDNAccount).where(
            CDNAccount.name == data.name
        )
    )

    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="CDN Account 名称已存在",
        )

    account = CDNAccount(
        name=data.name,
        account_id=data.account_id,
        api_token=data.api_token,
    )

    db.add(account)

    await db.commit()
    await db.refresh(account)

    return {
        "id": account.id,
        "name": account.name,
        "account_id": account.account_id,
        "token_configured": True,
    }


@router.get(
    "",
    response_model=list[CDNAccountResponse],
)
async def list_cdn_accounts(
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CDNAccount)
        .order_by(CDNAccount.id.desc())
    )

    accounts = result.scalars().all()

    return [
        {
            "id": account.id,
            "name": account.name,
            "account_id": account.account_id,
            "token_configured": bool(account.api_token),
        }
        for account in accounts
    ]


@router.get(
    "/{account_id}",
    response_model=CDNAccountResponse,
)
async def get_cdn_account(
    account_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CDNAccount).where(
            CDNAccount.id == account_id
        )
    )

    account = result.scalar_one_or_none()

    if account is None:
        raise HTTPException(
            status_code=404,
            detail="CDN Account 不存在",
        )

    return {
        "id": account.id,
        "name": account.name,
        "account_id": account.account_id,
        "token_configured": bool(account.api_token),
    }


@router.put(
    "/{account_id}",
    response_model=CDNAccountResponse,
)
async def update_cdn_account(
    account_id: int,
    data: CDNAccountUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CDNAccount).where(
            CDNAccount.id == account_id
        )
    )

    account = result.scalar_one_or_none()

    if account is None:
        raise HTTPException(
            status_code=404,
            detail="CDN Account 不存在",
        )

    if data.name is not None:
        result = await db.execute(
            select(CDNAccount).where(
                CDNAccount.name == data.name,
                CDNAccount.id != account_id,
            )
        )

        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail="CDN Account 名称已存在",
            )

        account.name = data.name

    if data.account_id is not None:
        account.account_id = data.account_id

    if data.api_token is not None:
        account.api_token = data.api_token

    await db.commit()
    await db.refresh(account)

    return {
        "id": account.id,
        "name": account.name,
        "account_id": account.account_id,
        "token_configured": bool(account.api_token),
    }


@router.delete(
    "/{account_id}",
)
async def delete_cdn_account(
    account_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Domain.id)
        .where(Domain.cdn_account_id == account_id)
        .limit(1)
    )

    account = result.scalar_one_or_none()

    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=400,
            detail="该 CDN Account 仍有域名使用，不能删除",
        )

    await db.delete(account)
    await db.commit()

    return {
        "success": True,
        "message": "删除成功",
    }




from app.services.cloudflare import (
    CloudflareError,
    CloudflareService,
)



@router.post(
    "/{account_id}/test",
)
async def test_cdn_account(
    account_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CDNAccount).where(
            CDNAccount.id == account_id
        )
    )

    account = result.scalar_one_or_none()

    if account is None:
        raise HTTPException(
            status_code=404,
            detail="CDN Account 不存在",
        )

    service = CloudflareService(
        api_token=account.api_token,
    )

    try:
        service.verify_token()

    except CloudflareError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Cloudflare Token 验证失败: {e}",
        )

    return {
        "success": True,
        "message": "Cloudflare Token 验证成功",
    }
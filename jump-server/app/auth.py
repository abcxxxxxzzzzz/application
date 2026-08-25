import secrets

from fastapi import (
    Cookie,
    HTTPException,
    status,
    Request,
    APIRouter,
    HTTPException,
    Response,
    Depends
)

from .config import settings
from .redis import redis



from .schemas import AdminLoginRequest

def verify_password(
    password: str,
) -> bool:

    return secrets.compare_digest(
        password,
        settings.admin_password,
    )


async def create_token() -> str:

    token = secrets.token_urlsafe(32)

    await redis.set(
        f"admin:auth:{token}",
        "1",
        ex=settings.admin_cookie_expire,
    )


    return token


async def require_admin(
    admin_auth: str | None = Cookie(
        default=None,
        alias=settings.admin_cookie_name,
    ),
):

    if not admin_auth:

        raise HTTPException(
            status_code=401,
            detail="未授权访问",
        )

    exists = await redis.exists(
        f"admin:auth:{admin_auth}"
    )

    if not exists:

        raise HTTPException(
            status_code=401,
            detail="登录已失效",
        )

    return True



# 



router = APIRouter(
    prefix="/api/admin/auth",
)


@router.post("/login")
async def admin_login(
    data: AdminLoginRequest,
    response: Response,
):

    if not verify_password(
        data.password
    ):
        raise HTTPException(
            401,
            "口令错误",
        )

    token = await create_token()

    response.set_cookie(
        key=settings.admin_cookie_name,
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.admin_cookie_expire,
        path="/",
    )

    return {
        "success": True,
    }

@router.post("/logout")
async def admin_logout(
    response: Response,
    admin_auth: str | None = Cookie(
        default=None,
        alias=settings.admin_cookie_name,
    ),
):

    if admin_auth:

        await redis.delete(
            f"admin:auth:{admin_auth}"
        )

    response.delete_cookie(
        key=settings.admin_cookie_name,
        path="/",
    )

    return {
        "success": True,
    }


@router.post("/check")
async def check_admin_auth(
    _: bool = Depends(require_admin),
):
    return {
        "authenticated": True,
    }
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel

from app.core.auth import (
    SESSION_COOKIE,
    create_session,
)
from app.core.config import settings


router = APIRouter(
    prefix="/api/auth",
    tags=["Auth"],
)


class LoginRequest(BaseModel):
    password: str


@router.post("/login")
async def login(
    data: LoginRequest,
    response: Response,
):
    if data.password != settings.admin_password:
        raise HTTPException(
            status_code=401,
            detail="口令错误",
        )

    session = create_session()

    response.set_cookie(
        key=SESSION_COOKIE,
        value=session,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=86400,
        path="/",
    )

    return {
        "success": True,
        "message": "登录成功",
    }


@router.post("/logout")
async def logout(
    response: Response,
):
    response.delete_cookie(
        key=SESSION_COOKIE,
        path="/",
    )

    return {
        "success": True,
        "message": "已退出登录",
    }
from fastapi import HTTPException, Request, status
from itsdangerous import BadSignature, URLSafeSerializer

from app.core.config import settings


SESSION_COOKIE = "cdn_manager_session"

serializer = URLSafeSerializer(
    settings.admin_password,
    salt="cdn-manager-auth",
)


def create_session() -> str:
    return serializer.dumps({"authenticated": True})


def verify_session(value: str | None) -> bool:
    if not value:
        return False

    try:
        data = serializer.loads(value)
    except BadSignature:
        return False

    return data.get("authenticated") is True


async def require_auth(request: Request):
    session = request.cookies.get(SESSION_COOKIE)

    if not verify_session(session):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录",
        )
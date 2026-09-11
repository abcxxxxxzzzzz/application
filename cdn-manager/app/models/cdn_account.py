from sqlalchemy import BigInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class CDNAccount(Base, TimestampMixin):
    __tablename__ = "cdn_accounts"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    # 后台显示名称
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    # Cloudflare Account ID
    account_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    # Cloudflare API Token
    api_token: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    domains: Mapped[list["Domain"]] = relationship(
        "Domain",
        back_populates="cdn_account",
    )
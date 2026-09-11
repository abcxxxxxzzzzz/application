from sqlalchemy import (
    BigInteger,
    ForeignKey,
    String,
    UniqueConstraint,
    Integer
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class DomainCDNTarget(Base, TimestampMixin):
    __tablename__ = "domain_cdn_targets"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    # 对应域名
    domain_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("domains.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    

    # CDN 名称
    # cf / aws / aliyun / tencent ...
    cdn: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )


    # 0 = 不启用 CF 代理
    # 1 = 启用 CF 代理
    proxied: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )


    # 该 CDN 对应的 CNAME
    cname: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    domain: Mapped["Domain"] = relationship(
        "Domain",
        back_populates="cdn_targets",
    )

    __table_args__ = (
        UniqueConstraint(
            "domain_id",
            "cdn",
            name="uk_domain_cdn",
        ),
    )
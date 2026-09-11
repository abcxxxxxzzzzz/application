from sqlalchemy import (
    BigInteger,
    Boolean,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Domain(Base, TimestampMixin):
    __tablename__ = "domains"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    # 所属分组
    group_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # 使用哪个 Cloudflare 账号
    cdn_account_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("cdn_accounts.id"),
        nullable=False,
        index=True,
    )

    # Cloudflare 顶级 Zone ID
    domain_zone_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )

    # 实际域名
    domain: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    # 当前目标 CDN
    # cf / aws / aliyun / ...
    desired_cdn: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
    )

    # 是否启用
    enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    # 最近一次成功切换备注
    switch_remark: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    group: Mapped["Group"] = relationship(
        "Group",
        back_populates="domains",
    )

    cdn_account: Mapped["CDNAccount"] = relationship(
        "CDNAccount",
        back_populates="domains",
    )

    cdn_targets: Mapped[list["DomainCDNTarget"]] = relationship(
        "DomainCDNTarget",
        back_populates="domain",
        cascade="all, delete-orphan",
    )
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from .database import Base


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    custom_params: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    domains: Mapped[list["Domain"]] = relationship(
        back_populates="group",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class Domain(Base):
    __tablename__ = "domains"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    domain: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    group_id: Mapped[int] = mapped_column(
        ForeignKey(
            "groups.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    # direct / wildcard / random
    jump_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="direct",
        index=True,
    )

    # redirect / js / html / iframe
    jump_method: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="redirect",
    )

    status_code: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=302,
    )

    target_domain: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        index=True,
    )


    use_group_params: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="0",
    )


    embedded_code: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    group: Mapped["Group"] = relationship(
        back_populates="domains",
        lazy="selectin",
    )

    pool: Mapped[list["DomainPool"]] = relationship(
        back_populates="domain_obj",
        cascade="all, delete-orphan",
        order_by="DomainPool.id",
        lazy="selectin",
    )


class DomainPool(Base):
    __tablename__ = "domain_pools"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    domain_id: Mapped[int] = mapped_column(
        ForeignKey(
            "domains.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    target_domain: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    weight: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    domain_obj: Mapped["Domain"] = relationship(
        back_populates="pool",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint(
            "domain_id",
            "target_domain",
            name="uq_domain_pool_target",
        ),
    )
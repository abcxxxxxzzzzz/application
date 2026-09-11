from sqlalchemy import BigInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Group(Base, TimestampMixin):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    # # 源站地址
    # origin_address: Mapped[str] = mapped_column(
    #     String(255),
    #     nullable=False,
    # )

    domains: Mapped[list["Domain"]] = relationship(
        "Domain",
        back_populates="group",
    )
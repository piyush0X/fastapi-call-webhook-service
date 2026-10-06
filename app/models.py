from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Call(Base):
    __tablename__ = "calls"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    call_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    duration_secs: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
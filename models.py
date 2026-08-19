from sqlalchemy import BigInteger, JSON
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class BaseModels(DeclarativeBase, AsyncAttrs):
    pass


class LastInfo(BaseModels):
    __tablename__ = "lastinfo"
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    chat_id: Mapped[int] = mapped_column(BigInteger)
    table_link: Mapped[str | None] = mapped_column(nullable=True)
    file_path: Mapped[str | None] = mapped_column(nullable=True)
    grade: Mapped[str | None] = mapped_column(nullable=True)
    last_schedule: Mapped[list[dict] | None] = mapped_column(JSON, nullable=True)

from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy import BigInteger, String, JSON
from sqlalchemy.ext.asyncio import AsyncAttrs


class BaseModels(DeclarativeBase, AsyncAttrs):
    pass


class LastInfo(BaseModels):
    __tablename__ = "lastinfo"
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    msg_id: Mapped[int] = mapped_column()
    chat_id: Mapped[int] = mapped_column()
    last_schedule: Mapped[list[dict] | None] = mapped_column(JSON, nullable=True) 

from sqlalchemy import BigInteger, JSON, text
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncConnection
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
    class_letter: Mapped[str | None] = mapped_column(nullable=True)
    last_schedule: Mapped[list[dict] | None] = mapped_column(JSON, nullable=True)


async def ensure_schema(conn: AsyncConnection) -> None:
    """create_all не трогает уже существующие таблицы — добираем новые колонки вручную,
    чтобы обновление кода не требовало сноса рабочей базы с данными пользователей."""
    await conn.run_sync(BaseModels.metadata.create_all)

    existing = {
        row[1] for row in (await conn.exec_driver_sql("PRAGMA table_info(lastinfo)")).fetchall()
    }
    for column in LastInfo.__table__.columns:
        if column.name not in existing:
            column_type = column.type.compile(dialect=conn.dialect)
            await conn.execute(text(f"ALTER TABLE lastinfo ADD COLUMN {column.name} {column_type}"))

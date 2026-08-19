from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

engine = create_async_engine("sqlite+aiosqlite:///msgdb.sqlite3")

async_session = async_sessionmaker(engine, expire_on_commit=False)

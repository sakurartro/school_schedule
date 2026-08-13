from tg.tg_bot_init import bot, dp
import asyncio
import logging
from tg.handlers import router, scheduler
from connection import engine, async_session
from models import BaseModels


async def main():
    dp.include_router(router)
    scheduler.start()
    async with engine.begin() as conn:
        await conn.run_sync(BaseModels.metadata.create_all)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Ошибка: {e}")
        
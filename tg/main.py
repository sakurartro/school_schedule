from tg.tg_bot_init import bot, dp
import asyncio
import logging
from tg.handlers import router

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Ошибка: {e}")
        
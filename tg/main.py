from aiogram.types import BotCommand

from tg.tg_bot_init import bot, dp
import asyncio
import logging
from tg.handlers import router
from tg.help_handlers import router as help_router
from tg.payement import router as payement_router
from tg.schedule_handlers import router as schedule_router, scheduler
from connection import engine, async_session
from models import BaseModels

BOT_COMMANDS = [
    BotCommand(command="start", description="Начать работу с ботом"),
    BotCommand(command="today", description="Расписание на сегодня"),
    BotCommand(command="week", description="Расписание на неделю"),
    BotCommand(command="help", description="Что умеет бот"),
    BotCommand(command="premium", description="Premium-подписка"),
]


async def main():
    dp.include_router(router)
    dp.include_router(help_router)
    dp.include_router(payement_router)
    dp.include_router(schedule_router)
    scheduler.start()
    async with engine.begin() as conn:
        await conn.run_sync(BaseModels.metadata.create_all)

    await bot.set_my_commands(BOT_COMMANDS)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Ошибка: {e}")

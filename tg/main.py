import asyncio
import logging

from aiogram.types import BotCommand

from connection import engine
from models import BaseModels
from tg.handlers import router
from tg.help_handlers import router as help_router
from tg.schedule_handlers import router as schedule_router
from tg.schedule_notifier import scheduler
from tg.tg_bot_init import bot, dp
from tg.user_handlers import router as user_router

BOT_COMMANDS = [
    BotCommand(command="start", description="Начать работу с ботом"),
    BotCommand(command="today", description="Расписание на сегодня"),
    BotCommand(command="tomorrow", description="Расписание на завтра"),
    BotCommand(command="week", description="Расписание на неделю"),
    BotCommand(command="profile", description="Мой профиль"),
    BotCommand(command="change_grade", description="Сменить класс"),
    BotCommand(command="change_schedule", description="Сменить таблицу"),
    BotCommand(command="help", description="Что умеет бот"),
    BotCommand(command="cancel", description="Отменить текущее действие"),
]


async def main():
    dp.include_router(router)
    dp.include_router(help_router)
    dp.include_router(schedule_router)
    dp.include_router(user_router)

    async with engine.begin() as conn:
        await conn.run_sync(BaseModels.metadata.create_all)

    scheduler.start()
    await bot.set_my_commands(BOT_COMMANDS)
    try:
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown(wait=False)
        await bot.session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен")

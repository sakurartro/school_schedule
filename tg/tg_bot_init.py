from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN: str = os.getenv("TG_API_KEY", "")

bot = Bot(token=TOKEN)

dp = Dispatcher()
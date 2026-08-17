from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN: str = os.getenv("TG_API_KEY", "")
TG_PROXY: str = os.getenv("TG_PROXY", "")

session = AiohttpSession(proxy=TG_PROXY) if TG_PROXY else AiohttpSession()
bot = Bot(token=TOKEN, session=session)

dp = Dispatcher()
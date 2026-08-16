from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN: str = os.getenv("TG_API_KEY", "")

session = AiohttpSession(proxy="socks5://127.0.0.1:1080")
bot = Bot(token=TOKEN, session=session)

dp = Dispatcher()
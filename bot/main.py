import asyncio
import logging
from os import getenv
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from dotenv import load_dotenv
from bot.handlers.profile import router as profile_router
from bot.handlers.start import router as start_router
from bot.handlers.chat import router as chat_router
from bot.handlers.recipes import router as recipes_router

load_dotenv()

logging.basicConfig(level=logging.INFO)

session = AiohttpSession(proxy=getenv("SOCKS5_PROXY"))
bot = Bot(token=getenv("BOT_TOKEN"), session=session)

dp = Dispatcher()
dp.include_router(profile_router)
dp.include_router(start_router)
dp.include_router(recipes_router)
dp.include_router(chat_router)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
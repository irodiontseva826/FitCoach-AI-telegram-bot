import asyncio
import logging
from os import getenv
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv
from bot.handlers.profile import router as profile_router
from bot.handlers.start import router as start_router
from bot.keyboards import main_menu_keyboard

load_dotenv() # для загрузки тонеков

logging.basicConfig(level=logging.INFO)

bot = Bot(token=getenv("BOT_TOKEN")) #создание бота
dp = Dispatcher()
dp.include_router(profile_router)
dp.include_router(start_router)

async def main(): #запуск бота
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
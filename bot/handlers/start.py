from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.keyboards import main_menu_keyboard  # ← добавим позже

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я <b>FitCoach AI</b> — твой персональный тренер и диетолог 🍎\n\n"
        "Готов составить тебе индивидуальный план питания и тренировок! Нажми кнопку ниже.",
        parse_mode="HTML",
        reply_markup=main_menu_keyboard()   # ← главная клавиатура с кнопкой
    )
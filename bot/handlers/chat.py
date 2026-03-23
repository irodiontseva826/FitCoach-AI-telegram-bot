from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from bot.utils import ask_llm
from bot.keyboards import plan_action_keyboard
from pathlib import Path
import json

router = Router()

@router.message(F.text)
async def free_chat_handler(message: Message):
    if message.text.startswith('/'):
        return

    STORAGE_DIR = Path("data")
    file = STORAGE_DIR / f"{message.from_user.id}.json"

    profile_text = "Профиль пока не собран"
    last_plan = "План пока не сгенерирован"

    if file.exists():
        try:
            user_data = json.loads(file.read_text(encoding="utf-8"))
            profile_text = "\n".join([f"{k}: {v}" for k,v in user_data.get("profile", {}).items()])
            last_plan = user_data.get("plan", "План пока пустой")
        except Exception as e:
            await message.answer(f"Ошибка чтения данных: {e}")
            return

    await message.answer("🤖 Думаю над твоим вопросом... ⏳")

    prompt = f"""
Ты — строгий, но добрый ИИ-тренер FitCoach AI.
У пользователя сейчас такие данные:
{profile_text}

Последний сгенерированный план:
{last_plan}

Пользователь написал:
"{message.text}"

Ответь по делу, используй эмодзи, сохраняй дружелюбный тон.
Если пользователь просит изменить план — предложи новую версию.
"""

    response = await ask_llm(prompt)
    await message.answer(response, parse_mode="HTML", reply_markup=plan_action_keyboard())

@router.callback_query(F.data.in_({"adjust_goal", "adjust_food", "adjust_training", "free_chat"}))
async def handle_plan_buttons(callback: CallbackQuery):
    if callback.data == "free_chat":
        await callback.message.answer("Напиши, что хочешь изменить или спросить:")
        await callback.answer()
        return

    texts = {
        "adjust_goal": "Что именно изменить в цели?",
        "adjust_food": "Какой продукт добавить/убрать?",
        "adjust_training": "Что изменить в тренировках (легче/тяжелее/заменить)?"
    }
    await callback.message.answer(texts.get(callback.data, "Что именно хочешь изменить?"))
    await callback.answer()
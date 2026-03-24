from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from bot.utils import ask_llm, send_plan_split
from bot.keyboards import plan_action_keyboard
from backend.llm import adjust_plan
from backend.storage import load_plan

router = Router()

@router.message(F.text)
async def free_chat_handler(message: Message):
    if message.text.startswith('/'):
        return

    record = load_plan(message.from_user.id)

    profile_text = "Профиль пока не собран"
    last_plan = "План пока не сгенерирован"

    if record:
        profile = record.get("profile", {})
        last_plan = record.get("plan", "")
        profile_text = "\n".join([f"{k}: {v}" for k, v in profile.items()])

    await message.answer("🤖 Думаю над твоим вопросом... ⏳")

    prompt = f"""
    Ты — ИИ-тренер FitCoach AI.

    Профиль пользователя:
    {profile_text}

    Текущий план:
    {last_plan}

    Запрос пользователя:
    "{message.text}"

    Если это вопрос — ответь кратко и по делу.

    Если это изменение плана — НЕ задавай вопросов, а сразу напиши, как именно изменится план.

    Будь конкретным, дружелюбным и используй эмодзи.
    """

    text = message.text.lower()

    trigger_words = [
        "убери", "убрать", "замени", "заменить",
        "добавь", "добавить", "измени", "изменить",
        "сделай", "сделать", "исключи", "исключить"
    ]

    if record and any(word in text for word in trigger_words):
        await message.answer("🔄 Обновляю план под твой запрос...")

        result = await adjust_plan(message.from_user.id, message.text)

        if not result["ok"]:
            await message.answer(
                result["data"],
                reply_markup=plan_action_keyboard()
            )
            return

        new_plan = result["data"]

        await send_plan_split(message, new_plan)

        await message.answer(
            "План обновлён ✅",
            reply_markup=plan_action_keyboard()
        )
        return

    else:
        response = await ask_llm(prompt)
        await message.answer(
            response,
            parse_mode="Markdown",
            reply_markup=plan_action_keyboard()
        )

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

    await callback.message.answer(
        texts.get(callback.data),
        parse_mode="Markdown",
        reply_markup=None
    )
    await callback.answer()
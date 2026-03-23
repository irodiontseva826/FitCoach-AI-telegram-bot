from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.states import ProfileForm
from bot.keyboards import (
    gender_keyboard, goal_keyboard, level_keyboard,
    cancel_and_restart_keyboard, remove_keyboard, plan_action_keyboard
)
import json
from pathlib import Path

STORAGE_DIR = Path("data")
STORAGE_DIR.mkdir(exist_ok=True)

router = Router()

async def save_user_data(user_id: int, data: dict, plan: str = ""):
    file = STORAGE_DIR / f"{user_id}.json"
    file.write_text(json.dumps({"profile": data, "plan": plan}, ensure_ascii=False, indent=2), encoding="utf-8")

@router.message(F.text == "Создать новый план")
async def start_profile(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Отлично! Давай соберём твои данные для персонального плана.\n\n"
        "Шаг 1/9\nКакой у тебя пол?",
        reply_markup=gender_keyboard()
    )
    await state.set_state(ProfileForm.gender)

@router.message(F.text.in_({"Отмена", "Начать заново"}))
async def handle_cancel_restart(message: Message, state: FSMContext):
    if message.text == "Отмена":
        await state.clear()
        await message.answer("Опрос отменён.", reply_markup=remove_keyboard())
    else:
        await state.clear()
        await start_profile(message, state)

@router.message(ProfileForm.gender)
async def process_gender(message: Message, state: FSMContext):
    if message.text in ("Отмена", "Начать заново"):
        await handle_cancel_restart(message, state)
        return
    await state.update_data(gender=message.text)
    await message.answer(
        "Шаг 2/9\nСколько тебе лет? (число)",
        reply_markup=cancel_and_restart_keyboard()
    )
    await state.set_state(ProfileForm.age)

@router.message(ProfileForm.age)
async def process_age(message: Message, state: FSMContext):
    if message.text in ("Отмена", "Начать заново"):
        await handle_cancel_restart(message, state)
        return
    try:
        age = int(message.text.strip())
        if age < 14 or age > 100:
            raise ValueError
        await state.update_data(age=age)
        await message.answer(
            "Шаг 3/9\nРост в см (число)",
            reply_markup=cancel_and_restart_keyboard()
        )
        await state.set_state(ProfileForm.height)
    except ValueError:
        await message.answer("Возраст — число от 14 до 100")

@router.message(ProfileForm.height)
async def process_height(message: Message, state: FSMContext):
    if message.text in ("Отмена", "Начать заново"):
        await handle_cancel_restart(message, state)
        return
    try:
        height = int(message.text.strip())
        if height < 100 or height > 250:
            raise ValueError
        await state.update_data(height=height)
        await message.answer("Шаг 4/9\nВес в кг (число, можно с десятичной частью)",
            reply_markup=cancel_and_restart_keyboard()
        )
        await state.set_state(ProfileForm.weight)
    except ValueError:
        await message.answer("Рост — число от 100 до 250")

@router.message(ProfileForm.weight)
async def process_weight(message: Message, state: FSMContext):
    if message.text in ("Отмена", "Начать заново"):
        await handle_cancel_restart(message, state)
        return
    try:
        weight = float(message.text.strip().replace(',', '.'))
        if weight < 30 or weight > 200:
            raise ValueError
        await state.update_data(weight=weight)
        await message.answer(
            "Шаг 5/9\nТвоя цель?",
            reply_markup=goal_keyboard()
        )
        await state.set_state(ProfileForm.goal)
    except ValueError:
        await message.answer("Вес — число (например 72.5 или 73)")

@router.message(ProfileForm.goal)
async def process_goal(message: Message, state: FSMContext):
    if message.text in ("Отмена", "Начать заново"):
        await handle_cancel_restart(message, state)
        return
    await state.update_data(goal=message.text)
    await message.answer(
        "Шаг 6/9\nКакой у тебя уровень подготовки?",
        reply_markup=level_keyboard()
    )
    await state.set_state(ProfileForm.level)

@router.message(ProfileForm.level)
async def process_level(message: Message, state: FSMContext):
    if message.text in ("Отмена", "Начать заново"):
        await handle_cancel_restart(message, state)
        return
    await state.update_data(level=message.text)
    await message.answer(
        "Шаг 7/9\nСколько дней в неделю ты можешь тренироваться? (число от 1 до 7)",
        reply_markup=cancel_and_restart_keyboard()
    )
    await state.set_state(ProfileForm.training_days)

@router.message(ProfileForm.training_days)
async def process_training_days(message: Message, state: FSMContext):
    if message.text in ("Отмена", "Начать заново"):
        await handle_cancel_restart(message, state)
        return
    try:
        days = int(message.text.strip())
        if not 1 <= days <= 7:
            raise ValueError
        await state.update_data(training_days=days)
        await message.answer(
            "Шаг 8/9\nКак ты будешь тренироваться? (в зале / дома / без оборудования / и т.д.)",
            reply_markup=cancel_and_restart_keyboard()
        )
        await state.set_state(ProfileForm.equipment)
    except ValueError:
        await message.answer("Введи число от 1 до 7")

@router.message(ProfileForm.equipment)
async def process_equipment(message: Message, state: FSMContext):
    if message.text in ("Отмена", "Начать заново"):
        await handle_cancel_restart(message, state)
        return
    await state.update_data(equipment=message.text.strip())
    await message.answer(
        "Шаг 9/9\nЕсть ли ограничения в питании?\n"
        "(вегетарианец, без лактозы, аллергия на орехи и т.д.)\n"
        "Если нет — просто напиши «нет» или оставь пустым",
        reply_markup=cancel_and_restart_keyboard()
    )
    await state.set_state(ProfileForm.restrictions)

@router.message(ProfileForm.restrictions)
async def finish_profile(message: Message, state: FSMContext):
    if message.text in ("Отмена", "Начать заново"):
        await handle_cancel_restart(message, state)
        return
    restrictions = message.text.strip() or "нет ограничений"
    await state.update_data(restrictions=restrictions)
    data = await state.get_data()

    summary = (
        "Данные собраны!\n\n"
        f"Пол: {data.get('gender')}\n"
        f"Возраст: {data.get('age')} лет\n"
        f"Рост: {data.get('height')} см\n"
        f"Вес: {data.get('weight')} кг\n"
        f"Цель: {data.get('goal')}\n"
        f"Уровень: {data.get('level')}\n"
        f"Дней тренировок в неделю: {data.get('training_days')}\n"
        f"Место тренировок: {data.get('equipment')}\n"
        f"Ограничения в еде: {data.get('restrictions')}\n\n"
        "Сейчас я бы отправил это на генерацию плана... (покажем заглушку)"
    )

    await save_user_data(message.from_user.id, data, plan="План пока не сгенерирован")
    await message.answer(summary, reply_markup=plan_action_keyboard())

    await state.clear()
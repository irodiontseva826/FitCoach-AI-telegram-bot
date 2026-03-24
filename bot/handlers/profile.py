from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from bot.states import ProfileForm
from bot.keyboards import (
    gender_keyboard, goal_keyboard, level_keyboard,
    cancel_and_restart_keyboard, remove_keyboard,
    main_menu_keyboard, plan_action_keyboard,
    use_profile_or_refill_keyboard
)
from backend.llm import generate_plan
from backend.storage import load_plan, save_plan
from bot.utils import send_plan_split

router = Router()

async def go_back(message: Message, state: FSMContext):
    current = await state.get_state()

    back_map = {
        ProfileForm.age.state: (
            ProfileForm.gender,
            "Шаг 1/9\nКакой у тебя пол?",
            gender_keyboard()
        ),
        ProfileForm.height.state: (
            ProfileForm.age,
            "Шаг 2/9\nСколько тебе лет? (число)",
            cancel_and_restart_keyboard()
        ),
        ProfileForm.weight.state: (
            ProfileForm.height,
            "Шаг 3/9\nРост в см (число)",
            cancel_and_restart_keyboard()
        ),
        ProfileForm.goal.state: (
            ProfileForm.weight,
            "Шаг 4/9\nВес в кг (число, можно с десятичной частью)",
            cancel_and_restart_keyboard()
        ),
        ProfileForm.level.state: (
            ProfileForm.goal,
            "Шаг 5/9\nТвоя цель?",
            goal_keyboard()
        ),
        ProfileForm.training_days.state: (
            ProfileForm.level,
            "Шаг 6/9\nКакой у тебя уровень подготовки?",
            level_keyboard()
        ),
        ProfileForm.equipment.state: (
            ProfileForm.training_days,
            "Шаг 7/9\nСколько дней в неделю ты можешь тренироваться? (число от 1 до 7)",
            cancel_and_restart_keyboard()
        ),
        ProfileForm.restrictions.state: (
            ProfileForm.equipment,
            "Шаг 8/9\nКак ты будешь тренироваться? (в зале / дома / без оборудования / и т.д.)",
            cancel_and_restart_keyboard()
        ),
    }

    if current in back_map:
        prev_state, question, keyboard = back_map[current]
        await state.set_state(prev_state)
        await message.answer(question, reply_markup=keyboard)
    else:
        await state.clear()
        await message.answer(
            "Опрос отменён. Возвращаю в главное меню.",
            reply_markup=main_menu_keyboard()
        )

@router.message(F.text == "Создать новый план")
async def handle_new_plan(message: Message, state: FSMContext):
    record = load_plan(message.from_user.id)
    if record and record.get("profile"):
        profile = record["profile"]
        profile_summary = (
            f"👤 *Твой текущий профиль:*\n"
            f"• Пол: {profile.get('gender')}\n"
            f"• Возраст: {profile.get('age')} лет\n"
            f"• Рост / вес: {profile.get('height')} см / {profile.get('weight')} кг\n"
            f"• Цель: {profile.get('goal')}\n"
            f"• Уровень: {profile.get('level')}\n"
            f"• Тренировок в неделю: {profile.get('training_days')}\n"
            f"• Место: {profile.get('equipment')}\n"
            f"• Ограничения: {profile.get('restrictions')}"
        )
        await message.answer(
            profile_summary + "\n\nЧто сделаем?",
            parse_mode="Markdown",
            reply_markup=use_profile_or_refill_keyboard()
        )
    else:
        await _start_questionnaire(message, state)

@router.callback_query(F.data == "use_existing_profile")
async def use_existing_profile(callback: CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=None)
    record = load_plan(callback.from_user.id)
    if not record or not record.get("profile"):
        await callback.message.answer(
            "Профиль не найден. Пожалуйста, заполни анкету.",
            reply_markup=main_menu_keyboard()
        )
        await callback.answer()
        return

    profile = record["profile"]
    await callback.message.answer("Генерирую новый план по твоему профилю... ⏳")
    plan = await generate_plan(callback.from_user.id, profile)
    await send_plan_split(callback.message, plan)
    await callback.message.answer(
        "Что хочешь сделать с планом?",
        reply_markup=plan_action_keyboard()
    )
    await callback.message.answer("Главное меню:", reply_markup=main_menu_keyboard())
    await callback.answer()

@router.callback_query(F.data == "refill_profile")
async def refill_profile_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await _start_questionnaire(callback.message, state)
    await callback.answer()

@router.message(F.text == "Редактировать профиль")
async def handle_edit_profile(message: Message, state: FSMContext):
    await message.answer(
        "Хорошо, давай обновим твои данные! "
        "После заполнения анкеты нажми «Создать новый план», чтобы сгенерировать план с новыми данными."
    )
    await _start_questionnaire(message, state)

async def _start_questionnaire(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Отлично! Давай соберём твои данные для персонального плана.\n\n"
        "Шаг 1/9\nКакой у тебя пол?",
        reply_markup=gender_keyboard()
    )
    await state.set_state(ProfileForm.gender)

@router.message(ProfileForm.gender)
async def process_gender(message: Message, state: FSMContext):
    if message.text == "Начать заново":
        await state.clear()
        await _start_questionnaire(message, state)
        return
    if message.text == "Отмена":
        await go_back(message, state)
        return
    await state.update_data(gender=message.text)
    await message.answer("Шаг 2/9\nСколько тебе лет? (число)", reply_markup=cancel_and_restart_keyboard())
    await state.set_state(ProfileForm.age)

@router.message(ProfileForm.age)
async def process_age(message: Message, state: FSMContext):
    if message.text == "Начать заново":
        await state.clear()
        await _start_questionnaire(message, state)
        return
    if message.text == "Отмена":
        await go_back(message, state)
        return
    try:
        age = int(message.text.strip())
        if age < 14 or age > 100:
            raise ValueError
        await state.update_data(age=age)
        await message.answer("Шаг 3/9\nРост в см (число)", reply_markup=cancel_and_restart_keyboard())
        await state.set_state(ProfileForm.height)
    except ValueError:
        await message.answer("Возраст — число от 14 до 100")

@router.message(ProfileForm.height)
async def process_height(message: Message, state: FSMContext):
    if message.text == "Начать заново":
        await state.clear()
        await _start_questionnaire(message, state)
        return
    if message.text == "Отмена":
        await go_back(message, state)
        return
    try:
        height = int(message.text.strip())
        if height < 100 or height > 250:
            raise ValueError
        await state.update_data(height=height)
        await message.answer(
            "Шаг 4/9\nВес в кг (число, можно с десятичной частью)",
            reply_markup=cancel_and_restart_keyboard()
        )
        await state.set_state(ProfileForm.weight)
    except ValueError:
        await message.answer("Рост — число от 100 до 250")

@router.message(ProfileForm.weight)
async def process_weight(message: Message, state: FSMContext):
    if message.text == "Начать заново":
        await state.clear()
        await _start_questionnaire(message, state)
        return
    if message.text == "Отмена":
        await go_back(message, state)
        return
    try:
        weight = float(message.text.strip().replace(',', '.'))
        if weight < 30 or weight > 200:
            raise ValueError
        await state.update_data(weight=weight)
        await message.answer("Шаг 5/9\nТвоя цель?", reply_markup=goal_keyboard())
        await state.set_state(ProfileForm.goal)
    except ValueError:
        await message.answer("Вес — число (например 72.5 или 73)")

@router.message(ProfileForm.goal)
async def process_goal(message: Message, state: FSMContext):
    if message.text == "Начать заново":
        await state.clear()
        await _start_questionnaire(message, state)
        return
    if message.text == "Отмена":
        await go_back(message, state)
        return
    await state.update_data(goal=message.text)
    await message.answer(
        "Шаг 6/9\nКакой у тебя уровень подготовки?",
        reply_markup=level_keyboard()
    )
    await state.set_state(ProfileForm.level)

@router.message(ProfileForm.level)
async def process_level(message: Message, state: FSMContext):
    if message.text == "Начать заново":
        await state.clear()
        await _start_questionnaire(message, state)
        return
    if message.text == "Отмена":
        await go_back(message, state)
        return
    await state.update_data(level=message.text)
    await message.answer(
        "Шаг 7/9\nСколько дней в неделю ты можешь тренироваться? (число от 1 до 7)",
        reply_markup=cancel_and_restart_keyboard()
    )
    await state.set_state(ProfileForm.training_days)

@router.message(ProfileForm.training_days)
async def process_training_days(message: Message, state: FSMContext):
    if message.text == "Начать заново":
        await state.clear()
        await _start_questionnaire(message, state)
        return
    if message.text == "Отмена":
        await go_back(message, state)
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
    if message.text == "Начать заново":
        await state.clear()
        await _start_questionnaire(message, state)
        return
    if message.text == "Отмена":
        await go_back(message, state)
        return
    await state.update_data(equipment=message.text.strip())
    await message.answer(
        "Шаг 9/9\nЕсть ли ограничения в питании?\n"
        "(вегетарианец, без лактозы, аллергия на орехи и т.д.)\n"
        "Если нет — просто напиши «нет»",
        reply_markup=cancel_and_restart_keyboard()
    )
    await state.set_state(ProfileForm.restrictions)

@router.message(ProfileForm.restrictions)
async def finish_profile(message: Message, state: FSMContext):
    if message.text == "Начать заново":
        await state.clear()
        await _start_questionnaire(message, state)
        return
    if message.text == "Отмена":
        await go_back(message, state)
        return
    restrictions = message.text.strip() or "нет ограничений"
    await state.update_data(restrictions=restrictions)
    data = await state.get_data()
    await state.clear()

    await message.answer("Генерирую план, подожди немного... ⏳", reply_markup=remove_keyboard())
    plan = await generate_plan(message.from_user.id, data)
    await send_plan_split(message, plan)

    await message.answer("Что хочешь сделать с планом?", reply_markup=plan_action_keyboard())
    await message.answer("Главное меню:", reply_markup=main_menu_keyboard())

@router.message(Command("myplan"))
async def cmd_myplan(message: Message) -> None:
    user_id = message.from_user.id
    record = load_plan(user_id)

    if record is None:
        await message.answer(
            "У тебя пока нет сохранённого плана.\n"
            "Нажми «Создать новый план» в главном меню, чтобы сгенерировать его."
        )
        return

    generated_at = record.get("generated_at", "неизвестно")
    plan_text = record.get("plan", "")
    profile = record.get("profile", {})

    header = (
        f"📋 *Твой план* (создан {generated_at})\n\n"
        f"*Профиль:*\n"
        f"• Пол: {profile.get('gender')}\n"
        f"• Возраст: {profile.get('age')} лет\n"
        f"• Рост / вес: {profile.get('height')} см / {profile.get('weight')} кг\n"
        f"• Цель: {profile.get('goal')}\n"
        f"• Уровень: {profile.get('level')}\n"
        f"• Тренировок в неделю: {profile.get('training_days')}\n"
        f"• Место: {profile.get('equipment')}\n"
        f"• Ограничения: {profile.get('restrictions')}\n\n"
        "─────────────────────\n"
    )

    await message.answer(header, parse_mode="Markdown")
    await send_plan_split(message, plan_text)
    await message.answer("Что хочешь изменить?", reply_markup=plan_action_keyboard())

@router.message(F.text == "Мой текущий план")
async def handle_myplan_button(message: Message):
    await cmd_myplan(message)
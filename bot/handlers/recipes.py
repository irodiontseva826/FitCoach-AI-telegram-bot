from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from bot.states import RecipeSearch
from backend.recipe_search import find_recipe_candidates, get_recipe_by_id
from backend.storage import load_plan
from bot.keyboards import main_menu_keyboard

router = Router()

@router.message(F.text == "Найти рецепт")
async def start_recipe_search(message: Message, state: FSMContext):
    await state.set_state(RecipeSearch.waiting_for_query)
    await message.answer(
        "🍽 *Поиск рецепта*\n\n"
        "Напиши, что хочешь приготовить — я найду подходящие варианты "
        "с учётом твоего профиля и ограничений.\n\n"
        "_Примеры:_\n"
        "• блюда из курицы\n"
        "• лёгкий завтрак с яйцами\n"
        "• суп без мяса\n"
        "• быстрый высокобелковый ужин",
        parse_mode="Markdown"
    )

@router.message(RecipeSearch.waiting_for_query)
async def handle_recipe_query(message: Message, state: FSMContext):
    await state.clear()

    record = load_plan(message.from_user.id)
    profile = record.get("profile", {}) if record else {}

    await message.answer("🔍 Ищу подходящие рецепты...")

    try:
        candidates = find_recipe_candidates(user_query=message.text, user_profile=profile)
    except Exception as e:
        print(f"[recipes] search error: {e}")
        await message.answer(
            "⚠️ Не удалось выполнить поиск. Попробуй чуть позже.",
            reply_markup=main_menu_keyboard()
        )
        return

    if not candidates:
        await message.answer(
            "😔 По запросу *«" + message.text + "»* ничего не нашлось в базе рецептов.\n\n"
            "Попробуй уточнить запрос — например, назови конкретный продукт:\n"
            "«курица», «творог», «рыба», «овсянка» и т.д.",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )
        return

    if len(candidates) == 1:
        await message.answer(_format_recipe(candidates[0]), parse_mode="Markdown")
        await _show_search_again(message)
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"🍽 {r['name']}",
            callback_data=f"recipe:{r['id']}"
        )]
        for r in candidates
    ])

    await message.answer(
        f"Нашёл *{len(candidates)} варианта* — выбери, какой показать подробнее:",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("recipe:"))
async def handle_recipe_pick(callback: CallbackQuery):
    recipe_id = int(callback.data.split(":")[1])
    recipe = get_recipe_by_id(recipe_id)

    await callback.message.edit_reply_markup(reply_markup=None)

    if not recipe:
        await callback.message.answer("⚠️ Рецепт не найден. Попробуй снова.")
        await callback.answer()
        return

    await callback.message.answer(_format_recipe(recipe), parse_mode="Markdown")
    await _show_search_again(callback.message)
    await callback.answer()

async def _show_search_again(message: Message):
    await message.answer(
        "Хочешь найти ещё рецепт? Нажми «Найти рецепт»",
        reply_markup=main_menu_keyboard()
    )

def _format_recipe(recipe: dict) -> str:
    lines = [
        f"🍽 *{recipe['name']}*",
        "",
        (
            f"📊 *На порцию:* ~{recipe['calories_per_serving']} ккал  "
            f"| Б {recipe['protein']}г  Ж {recipe['fat']}г  У {recipe['carbs']}г"
        ),
        "",
        "🛒 *Ингредиенты:*",
    ]

    ingredients = recipe.get("ingredients_with_amount") or recipe.get("ingredients", [])
    for item in ingredients:
        lines.append(f"  • {item}")

    lines += ["", "👨‍🍳 *Приготовление:*"]
    for i, step in enumerate(recipe.get("steps", []), start=1):
        lines.append(f"  {i}. {step}")

    if recipe.get("tips"):
        lines += ["", f"💡 *Совет:* {recipe['tips']}"]

    return "\n".join(lines)
from aiogram.fsm.state import State, StatesGroup

class ProfileForm(StatesGroup):
    gender = State()
    age = State()
    height = State()
    weight = State()
    goal = State()
    level = State()
    training_days = State()
    equipment = State()
    restrictions = State()

class RecipeSearch(StatesGroup):
    waiting_for_query = State()
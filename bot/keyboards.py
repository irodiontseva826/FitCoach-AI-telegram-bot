from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

def cancel_and_restart_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Отмена"), KeyboardButton(text="Начать заново")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )

def gender_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Мужской"), KeyboardButton(text="Женский")],
            [KeyboardButton(text="Отмена"), KeyboardButton(text="Начать заново")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Выбери пол"
    )

def goal_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Похудение")],
            [KeyboardButton(text="Набор массы")],
            [KeyboardButton(text="Поддержание формы")],
            [KeyboardButton(text="Сила / выносливость")],
            [KeyboardButton(text="Отмена"), KeyboardButton(text="Начать заново")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )

def level_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Новичок")],
            [KeyboardButton(text="Средний")],
            [KeyboardButton(text="Продвинутый")],
            [KeyboardButton(text="Отмена"), KeyboardButton(text="Начать заново")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )

def remove_keyboard():
    return ReplyKeyboardRemove()

def main_menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Создать новый план")],
            [KeyboardButton(text="Мой текущий план")],
            [KeyboardButton(text="Задать вопрос коучу")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
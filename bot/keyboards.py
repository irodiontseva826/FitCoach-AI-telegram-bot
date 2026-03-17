from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

def gender_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Мужской"), KeyboardButton(text="Женский")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Выбери пол"
    )

def goal_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Похудение")],
            [KeyboardButton(text="Набор массы")],
            [KeyboardButton(text="Поддержание формы")],
            [KeyboardButton(text="Сила / выносливость")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def level_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Новичок")],
            [KeyboardButton(text="Средний")],
            [KeyboardButton(text="Продвинутый")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def cancel_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Отмена")]],
        resize_keyboard=True,
        one_time_keyboard=False
    )

def remove_keyboard():
    return ReplyKeyboardRemove()

def main_menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Создать новый план ️")],
            [KeyboardButton(text="Мой текущий план")],          # пока заглушка
            [KeyboardButton(text="Задать вопрос коучу")],       # пока заглушка
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
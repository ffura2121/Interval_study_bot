from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from func.classes import list_themes as lt


def inline_kb_builder(prefix: str = "theme"):

    builder = InlineKeyboardBuilder()

    for index,theme in enumerate(lt):
        builder.button(
            text=theme.name, 
            callback_data=f"{prefix}_{index}"
            )
    return builder.as_markup()


def remember_or_no_remember():
    reply_kb = [
            [KeyboardButton(text="Пам'ятаю✅"), KeyboardButton(text="Не пам'ятаю❌")]
        ]
    kb = ReplyKeyboardMarkup(keyboard = reply_kb,resize_keyboard=True)
    return kb


def yes_or_no():
    reply_kb = [
            [KeyboardButton(text="Так✅"), KeyboardButton(text="Ні❌")]
        ]
    kb = ReplyKeyboardMarkup(keyboard = reply_kb,resize_keyboard=True)
    return kb
    



from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import database.connect as db
from database.db import db_select_all_themes_for_kb, db_select_id_user



async def inline_kb_builder(tg_user_id, prefix: str = "theme"):
    user_id = await db_select_id_user(db.pool, tg_user_id)
    lt = await db_select_all_themes_for_kb(db.pool, user_id)
    builder = InlineKeyboardBuilder()

    for theme in (lt):
        builder.button(
            text=theme["name"], 
            callback_data=f"{prefix}_{theme['id']}"
            )
    return builder.adjust(3).as_markup()


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

def main_menu():
    reply_kb = [
        [KeyboardButton(text="Створити нову тему📝"), KeyboardButton(text="Перегляд існуючих тем📂")],
        [KeyboardButton(text="Додавання слів до теми🖋"), KeyboardButton(text="Перегляд слів у темі📖")],
        [KeyboardButton(text="Видалення теми🗑"), KeyboardButton(text="Видалення слів із теми🗑")],
        [KeyboardButton(text="Повторення слів🔥"), KeyboardButton(text="Допомога⚙️")]
    ]
    kb = ReplyKeyboardMarkup(keyboard = reply_kb,resize_keyboard=True)
    return kb




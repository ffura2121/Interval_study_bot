from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from func.classes import list_themes as lt


def inline_kb_builder():

    builder = InlineKeyboardBuilder()

    for theme in lt:
        builder.button(text=theme.name, url="https://www.youtube.com/") #замість callback постав url як тимчасова міра, щоб не було помилок

    builder.adjust(5)
    return builder.as_markup()



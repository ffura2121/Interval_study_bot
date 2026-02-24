from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from func.classes import list_themes as lt


def inline_kb_builder():

    builder = InlineKeyboardBuilder()

    for index,theme in enumerate(lt):
        builder.button(
            text=theme.name, 
            callback_data=f"theme_{index}"
            )
    return builder.as_markup()



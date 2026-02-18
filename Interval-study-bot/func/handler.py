from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from func.classes import CreateTheme, Theme, list_themes
import func.keyboard as kb

router = Router()



#============ Старт ============

@router.message(CommandStart())
async def cmd_start(message:Message):
    await message.answer(f"Привіт {message.from_user.full_name}!")
    await message.answer(f"Я бот, який допомагає вивчати слова, завдяки методу інтервально повторення")
    await message.answer(f"Натисни /help, щоб побачити весь мій функціонал")

#============ Створення теми ============

@router.message(Command("create_new_theme"))
async def create_new_theme(message: Message, state: FSMContext):
    await message.answer("напиши назву теми: ") 
    await state.set_state(CreateTheme.waiting_name)


@router.message(CreateTheme.waiting_name)
async def process_theme_name(message: Message, state: FSMContext):
    title_name = message.text

    exists = False

    for theme_class in list_themes:
        if theme_class.name == title_name:
            exists = True
            break

    if exists:
        await message.answer("Вибачте, тема з такою назвою вже створенна")
        await state.clear()
    else:

        title_class = Theme(title_name)
        list_themes.append(title_class)
        await message.answer(f"Тема '{title_class.name}' створена!")
        await state.clear()

#============ Перегляд існуючих тем ============

@router.message(Command("theme"))
async def look_theme(message: Message):

    await message.answer("Список ваших тем:\n" + " ,".join(theme.name for theme in list_themes))

#============ Додавання слів у існуючі теми ============

@router.message(Command("add_word"))
async def add_word(message: Message):
    await message.answer("До якої теми ти хочеш додати нові слова?", reply_markup=kb.inline_kb_builder())

#============ команда help ============

@router.message(Command("help"))
async def help(message: Message):
    await message.answer("""/start - початок бота
/theme - перегляд існуючих тем зі словами
/create_new_theme - створення нової теми
/add_word - додавання слів до існуючих тем
/guide - інструкція по використання бота
/help - список всіх існуючих команд
/study - ===
/remind - ===
                         """)
    





# class CreateTheme(StatesGroup):
#     waiting_name = State()

# class Theme():

#     def __init__(self, name):
#         self.name = name
#         self.word_dict = {}


# @router.message(Command("create_new_theme"))
# async def create_new_theme(message: Message, state: FSMContext):
#     await message.answer("напиши назву теми: ") 
#     await state.set_state(CreateTheme.waiting_name)


# @router.message(CreateTheme.waiting_name)
# async def process_theme_name(message: Message, state: FSMContext):
#     theme_name = message.text

#     if theme_name in list_themes:
#         await message.answer("Вибачте, тема з такою назвою вже створенна")
#         await state.clear()
#     else:
#         new_theme = Theme(theme_name)
#         list_themes.append(new_theme)

#         await message.answer(f"Тема '{theme_name}' створена!")
#         await state.clear()

from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

router = Router()

class CreateTheme(StatesGroup):
    waiting_name = State()

class Theme():

    def __init__(self, name):
        self.name = name
        self.word_dict = {}

all_name_themes = []

@router.message(CommandStart())
async def cmd_start(message:Message):
    await message.answer(f"Привіт {Message.from_user.full_name}!")
    await message.answer(f"Я бот, який допомагає вивчати слова, завдяки методу інтервально повторення")
    await message.answer(f"Натисни /help, щоб побачити весь мій функціонал")

@router.message(Command("create_new_theme"))
async def create_new_theme(message: Message, state: FSMContext):
    await message.answer("напиши назву теми: ") 
    await state.set_state(CreateTheme.waiting_name)

@router.message(CreateTheme.waiting_name)
async def process_theme_name(message: Message, state: FSMContext):
    theme_name = message.text

    if theme_name in all_name_themes:
        await message.answer("Вибачте, тема з такою назвою вже створенна")
        await state.clear()
    else:
        new_theme = Theme(theme_name)
        all_name_themes.append(new_theme)

        await message.answer(f"Тема '{theme_name}' створена!")
        await state.clear()




@router.message(Command("help"))
async def help(message: Message):
    await message.answer("""/start - початок бота
                         /theme - перегляд існуючих тем зі словами
                         /create_new_theme - створення нової теми
                         /guide - інструкція по використання бота
                         /help - список всіх існуючих команд
                         /study - ===
                         /remind - ===
                         """)
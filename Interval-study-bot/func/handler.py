from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from func.classes import CreateTheme, AddWord, Theme, list_themes
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

#============ Callback ============

@router.callback_query(F.data.startswith("theme_"))
async def add_word(callback: CallbackQuery, state: FSMContext):
    index = int(callback.data.split("_")[1])

    await state.update_data(theme_index = index)
    await state.set_state(AddWord.word)
    await callback.answer("напиши слово яке ти хочеш додати: ")


@router.message(AddWord.word)
async def process_first_word(message: Message, state: FSMContext):
    
    await state.update_data(word = message.text)
    await state.set_state(AddWord.translate)
    await message.answer("Напишіть переклад")

@router.message(AddWord.translate)
async def process_second_word(message: Message, state: FSMContext):
    
    await state.update_data(translate = message.text)
    
    data = await state.get_data()
    theme_index = data["theme_index"]
    word = data["word"]
    translate = data["translate"]

    # Додаємо у словник потрібної теми
    list_themes[theme_index].dict_words[word] = translate

    await message.answer(f"Слово '{word}' з перекладом '{translate}' додано ✅")
    await state.clear()

@router.message(Command("show_words"))
async def show_words(message: Message):
    if not list_themes:
        await message.answer("Тем ще немає 😅")
        return

    text = ""
    for i, theme in enumerate(list_themes):
        text += f"Тема {i+1}: {theme.name}\n"
        if theme.dict_words:
            for word, translate in theme.dict_words.items():
                text += f"  {word} → {translate}\n"
        else:
            text += "  Слів ще немає\n"
        text += "\n"

    await message.answer(text)






    

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
/show_words - перегляд слів у темі
                         """)

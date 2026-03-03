from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from func.classes import CreateTheme, AddWord, RemindWord, Theme, list_themes
import func.keyboard as kb

#Імпорт бд
from database.connect import create_pool
from database.db import add_user

router = Router()

#Створення пул для бд
pool = None

async def setup_pool():
    global pool
    if pool is None:
        pool = await create_pool()

#============ Старт ============

@router.message(CommandStart())
async def cmd_start(message:Message):
    await setup_pool()
    await add_user(pool, message.from_user.id, message.from_user.full_name)

    await message.answer(f"Привіт {message.from_user.full_name}!")
    await message.answer(f"Я бот, який допомагає вивчати слова, завдяки методу інтервально повторення")
    await message.answer(f"Натисни /help, щоб побачити весь мій функціонал")

#============ Створення теми ============

@router.message(Command("create_new_theme"))
async def create_new_theme(message: Message, state: FSMContext):
    await message.answer("напиши назву теми: ")
    await state.set_state(CreateTheme.waiting_name)


@router.message(CreateTheme.waiting_name)
async def process_create_theme(message: Message, state: FSMContext):
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
        

#============ Додавання слова до теми ============

    index_theme = int(len(list_themes) - 1)
    await state.update_data(
        name = title_class.name,
        index_theme = index_theme
        )
    await message.answer("Тепер давай додамо твоє перше слово для цієї теми!\n\nНапиши спочатку слово, яке ти хочеш повторювати")
    await state.set_state(CreateTheme.word)

@router.message(CreateTheme.word)
async def process_add_word(message: Message, state: FSMContext):
    
    await state.update_data(word = message.text)
    await state.set_state(CreateTheme.translate)
    await message.answer("Напишіть переклад")

@router.message(CreateTheme.translate)
async def process_add_translate(message: Message, state: FSMContext):

    await state.update_data(translate = message.text)

    data = await state.get_data()
    index_theme = data["index_theme"]
    word = data["word"]
    translate = data["translate"]

    list_themes[index_theme].dict_words[word] = translate
    await message.answer(f"Слово '{word}' з перекладом '{translate}' додано ✅")
    

    await message.answer("Бажаєш додати наступне слово?", reply_markup=kb.yes_or_no())
    await state.set_state(CreateTheme.continue_process)

#============ Запит на продовження додавання слів до теми ============

@router.message(CreateTheme.continue_process)
async def process_continue_process(message: Message, state: FSMContext):

    await state.update_data(answer = message.text)

    data = await state.get_data()
    answer = data["answer"]
    name = data["name"]

    if answer == "Так✅":
        await state.set_state(CreateTheme.word)
        await message.answer("Напиши слово, яке ти хочеш повторювати")
    else:
        await message.answer(f"Додавання слів до створеної теми {name} завершено✅")
        await state.clear()
        
#============ Перегляд існуючих тем ============

@router.message(Command("theme"))
async def look_theme(message: Message):

    await message.answer("Список ваших тем:\n" + " ,".join(theme.name for theme in list_themes))

#============ Додавання слів у існуючі теми ============

@router.message(Command("add_word"))
async def add_word(message: Message):
    await message.answer("До якої теми ти хочеш додати нові слова?", reply_markup=kb.inline_kb_builder(prefix="add"))

#============ Callback (Додавання слів) ============

@router.callback_query(F.data.startswith("add_"))
async def add_word(callback: CallbackQuery, state: FSMContext):
    index = int(callback.data.split("_")[1])

    await state.update_data(theme_index = index)
    await state.set_state(AddWord.word)
    await callback.message.answer("напиши слово яке ти хочеш додати: ")
    await callback.answer()


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

#============ Додавання слова до теми ============

    list_themes[theme_index].dict_words[word] = translate

    await message.answer(f"Слово '{word}' з перекладом '{translate}' додано ✅")
    await state.clear()

#============ Показ всіх слів у темах ============

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

#============ Початок повторення ============

@router.message(Command("remind"))
async def add_word(message: Message):
    await message.answer("Обери тему для повторення слів", reply_markup=kb.inline_kb_builder(prefix="remind"))

#============ Callback (Повторення слів) ============

@router.callback_query(F.data.startswith("remind_"))
async def process_remind_word(callback: CallbackQuery, state: FSMContext):
    index = int(callback.data.split("_")[1])
    selected_theme = list_themes[index - 1]

    await callback.message.answer(f"Ви обрали тему: {selected_theme.name}")
    await callback.message.answer(f"Розпочнемо!")

    words = list(selected_theme.dict_words.items())
    
    first_key, _ = words[0]
    await callback.message.answer(first_key, reply_markup=kb.remember_or_no_remember()())

    await state.update_data(
        theme_index = index - 1,
        words = words,
        i = 0
    )
    await state.set_state(RemindWord.waiting_answer)


@router.message(RemindWord.waiting_answer)
async def process_continue(message: Message, state: FSMContext):
    data = await state.get_data()

    words = data["words"]
    i = data["i"]

    key, translate = words[i]

    if message.text == "Пам'ятаю✅":
        await message.answer(f"Молодець!\nПереклад: {translate}")
    else:
        await message.answer(f"Нічого страшного\nПереклад: {translate}")

    i += 1
    if i >= len(words):
        await message.answer("Повторення завершено✅")
        await state.clear()
        return
    
    await state.update_data(i=i)

    next_key, _ = words[i]
    await message.answer(next_key, reply_markup=kb.yes_or_no())

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
/remind - розпочати повторення слів
/show_words - перегляд слів у темі
                         """)

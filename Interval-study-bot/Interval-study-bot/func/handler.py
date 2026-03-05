from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from func.classes import CreateTheme, AddWord, RemindWord, Theme, list_themes
import func.keyboard as kb

#Імпорт бд
import database.connect as db
from database.db import db_add_user,db_add_theme, db_add_word
from database.db import db_select_id_user, db_select_all_themes,db_select_all_word_in_theme, db_select_name_themes, db_select_id_new_theme

router = Router()

#============ Старт ============

@router.message(CommandStart())
async def cmd_start(message:Message):
    await db_add_user(db.pool, message.from_user.id, message.from_user.full_name)

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
    lt = await db_select_name_themes(db.pool)
    for theme in lt:
        if theme[0] == title_name:
            exists = True
            break

    if exists:
        await message.answer("Вибачте, тема з такою назвою вже створенна")
        await state.clear()
    else:
        tg_user_id = message.from_user.id
        user_id = await db_select_id_user(db.pool, tg_user_id)
        await db_add_theme(db.pool, user_id, title_name)

        await message.answer(f"Тема '{title_name}' створена!")
        

#============ Додавання слова до теми ============
    new_theme_id = await db_select_id_new_theme(db.pool, title_name)

    await state.update_data(
        name = title_name,
        new_theme_id = new_theme_id
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
    new_theme_id = data["new_theme_id"]
    word = data["word"]
    translate = data["translate"]

    await db_add_word(db.pool, new_theme_id, word, translate)
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

    tg_user_id = message.from_user.id
    user_id = await db_select_id_user(db.pool,tg_user_id)
    await message.answer(await db_select_all_themes(db.pool, user_id))

#============ Додавання слів у існуючі теми ============

@router.message(Command("add_word"))
async def add_word(message: Message):
    tg_user_id = message.from_user.id

    await message.answer("До якої теми ти хочеш додати нові слова?", reply_markup= await kb.inline_kb_builder(tg_user_id, prefix="add"))



#============ Callback (Додавання слів) ============

@router.callback_query(F.data.startswith("add_"))
async def add_word(callback: CallbackQuery, state: FSMContext):
    theme_id = int(callback.data.split("_")[1])

    await state.update_data(theme_id = theme_id)
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
    theme_id = data["theme_id"]
    word = data["word"]
    translate = data["translate"]

#============ Додавання слова до теми ============

    await db_add_word(db.pool, theme_id, word, translate)

    await message.answer(f"Слово '{word}' з перекладом '{translate}' додано ✅")
    await state.clear()

#============ Показ всіх слів у темах ============

@router.message(Command("show_words"))
async def show_words(message: Message):
    tg_user_id = message.from_user.id
    await message.answer("Обери тему для перегляду слів", reply_markup= await kb.inline_kb_builder(tg_user_id, prefix="show"))

@router.callback_query(F.data.startswith("show_"))
async def process_show_word(callback: CallbackQuery):
    theme_id = int(callback.data.split("_")[1])
    word_list = await db_select_all_word_in_theme(db.pool, theme_id)

    if word_list:
        result = "\n".join(word_list)
        await callback.message.answer(f"Список всіх слів у темі:\n{result}")
        await callback.answer()
    else:
        await callback.message.answer("У даній темі наразі немає слів")
        await callback.answer()

#============ Початок повторення ============

@router.message(Command("remind"))
async def add_word(message: Message):
    tg_user_id = message.from_user.id
    await message.answer("Обери тему для повторення слів", reply_markup= await kb.inline_kb_builder(tg_user_id, prefix="remind"))

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
    await message.answer(""" Що вже реалізовано:
/start - початок бота
/theme - перегляд існуючих тем зі словами
/create_new_theme - створення нової теми
/add_word - додавання слів до існуючих тем
/remind - розпочати повторення слів
/show_words - перегляд слів у темі
/help - список всіх існуючих команд

                         
Що ще треба зробити (можливо):              
/guide - інструкція по використання бота
""")

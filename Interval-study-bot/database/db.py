

async def execute_query(pool, sql, params = None): #Для змін у бд, CREATE, INSERT, UPDATE, DELETE
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql, params)
            await conn.commit()

async def fetch_query(pool, sql, params = None): # Для SELECT
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql, params)
            return await cur.fetchall()

#Створення бд

create_db = "CREATE DATABASE IF NOT EXISTS tg_bot"

#Створення таблиці "users"

create_table_users = """
CREATE TABLE IF NOT EXISTS tg_bot.users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    telegram_id VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(50) NOT NULL
)
"""

#Створення таблиці "themes"

create_table_themes = """
CREATE TABLE IF NOT EXISTS tg_bot.themes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(50) NOT NULL UNIQUE,
    FOREIGN KEY (user_id) REFERENCES tg_bot.users(id) ON DELETE CASCADE
)
"""

#Створення таблиці "words"

create_table_words = """
CREATE TABLE IF NOT EXISTS tg_bot.words (
    id INT AUTO_INCREMENT PRIMARY KEY,
    theme_id INT NOT NULL,
    word VARCHAR(100) NOT NULL,
    translation VARCHAR(100) NOT NULL,
    FOREIGN KEY (theme_id) REFERENCES tg_bot.themes(id) ON DELETE CASCADE
)
"""

#Створення таблиці "interval"

create_table_words_interval = """
CREATE TABLE IF NOT EXISTS tg_bot.words_interval (
    id INT AUTO_INCREMENT PRIMARY KEY,
    word_id INT NOT NULL,
    user_id INT NOT NULL,
    interval_stage INT DEFAULT 0,
    next_review DATETIME DEFAULT NOW(),
    FOREIGN KEY (word_id) REFERENCES tg_bot.words(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES tg_bot.users(id) ON DELETE CASCADE
)
"""

#Додавання
async def db_add_user(pool, telegram_id, name):
    sql = "INSERT IGNORE INTO users (telegram_id, name) VALUES (%s, %s)"
    await execute_query(pool, sql, (telegram_id, name))

async def db_add_theme(pool, user_id, name):
    sql = "INSERT IGNORE INTO themes (user_id, name) VALUES (%s, %s)"
    await execute_query(pool, sql, (user_id, name))

async def db_add_word(pool, index_theme, word, translate, user_id):
    # 1. Додаємо слово в words
    sql = "INSERT INTO words (theme_id, word, translation) VALUES (%s, %s, %s)"
    await execute_query(pool, sql, (index_theme, word, translate))

    # 2. Дістаємо id нового слова
    sql_get_id = "SELECT id FROM words WHERE word = %s AND translation = %s"
    result = await fetch_query(pool, sql_get_id, (word, translate))
    word_id = result[0][0]

    # 3. Додаємо запис у words_interval
    sql_interval = """
    INSERT INTO words_interval (word_id, user_id, interval_stage, next_review)
    VALUES (%s, %s, 0, NOW())
    """
    await execute_query(pool, sql_interval, (word_id, user_id))


#Виведення
async def db_select_id_new_theme(pool, title_name):
    sql="SELECT id FROM themes WHERE name = %s"
    result = await fetch_query(pool, sql, (title_name,))
    return result[0][0]

async def db_select_id_user(pool, name):
    sql = "SELECT id FROM users WHERE telegram_id = %s"
    result = await fetch_query(pool, sql, (name,))
    return result[0][0]

async def db_select_all_themes(pool, user_id):
    sql = "SELECT name FROM themes WHERE user_id = %s"
    result = await fetch_query(pool, sql, (user_id,))
    str_themes = "Список існуючих тем: "
    for theme in result:
        title = theme[0]
        str_themes += "\n- " + title
    
    return str_themes

async def db_select_all_themes_for_kb(pool, user_id):
    sql = "SELECT id,name FROM themes WHERE user_id = %s"
    result = await fetch_query(pool, sql, (user_id,))
    list_themes = []
    for id,theme in result:
        list_themes.append({"id": id, "name": theme})
    
    return list_themes

async def db_select_id_theme(pool, name):
    sql = "SELECT id FROM themes WHERE name = %s"
    result = await fetch_query(pool, sql, (name,))
    return result[0][0]

async def db_select_all_word_in_theme(pool, theme_id):
    sql = "SELECT word, translation FROM words WHERE theme_id = %s"
    result = await fetch_query(pool, sql, (theme_id,))
    if not result:
        return []
    list_word = []
    count = 1
    for word, translation in result:
        list_word.append(f"{count}) {word} => {translation}")
        count += 1
    return list_word

async def db_select_name_themes(pool):
    sql = "SELECT name FROM themes"
    result = await fetch_query(pool, sql)
    return result

async def db_select_all_word_from_theme_in_list_tuple(pool, theme_id):
    sql = "SELECT word, translation FROM words WHERE theme_id = %s"
    result = await fetch_query(pool, sql, (theme_id,))
    if not result:
        return []
    list_word = []
    for word, translation in result:
        wt = (word, translation)
        list_word.append(wt)
    return list_word

async def db_select_words_repetition_now_1(pool, time):
    sql = "SELECT word_id FROM words_interval WHERE next_review <= %s"
    result = await fetch_query(pool, sql, (time,))
    word_id = []
    for row in result:
        word_id.append(row[0])
    return word_id

async def db_select_words_repetition_now_2(pool, word_id):

    word_list = []

    for id in word_id:
        sql_stage = "SELECT interval_stage FROM words_interval WHERE word_id = %s"
        result_stage = await fetch_query(pool, sql_stage, (id,))
        if result_stage:
            interval_stage = result_stage[0][0]
        else:
            interval_stage = 0

        sql_word = "SELECT word, translation FROM words WHERE id = %s"
        result = await fetch_query(pool, sql_word, (id,))
        for word, translation in result:
            word_list.append((word, translation, interval_stage))
    return word_list

async def db_select_update_next_review_1(pool, word, translation):
    sql = "SELECT id FROM words WHERE word = %s AND translation = %s"
    result = await fetch_query(pool, sql, (word, translation))
    return result[0][0]

#Оновлення
async def db_select_update_next_review_2(pool, interval_stage, next_review, id_word):
    sql = "UPDATE words_interval SET interval_stage = %s, next_review = %s WHERE word_id = %s"
    await execute_query(pool, sql, (interval_stage, next_review, id_word))

#Видалення

async def db_delete_word(pool, word):
    sql = "DELETE FROM words WHERE word = %s"
    await execute_query(pool, sql, (word,))

async def db_delete_theme(pool, id):
    sql = "DELETE FROM themes WHERE id = %s"
    await execute_query(pool, sql, (id,))
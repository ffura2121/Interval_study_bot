

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

#Додавання
async def db_add_user(pool, telegram_id, name):
    sql = "INSERT IGNORE INTO users (telegram_id, name) VALUES (%s, %s)"
    await execute_query(pool, sql, (telegram_id, name))

async def db_add_theme(pool, user_id, name):
    sql = "INSERT IGNORE INTO themes (user_id, name) VALUES (%s, %s)"
    await execute_query(pool, sql, (user_id, name))

async def db_add_word(pool, index_theme, word, translate):
    sql = "INSERT INTO words (theme_id, word, translation) VALUES (%s, %s, %s)"
    await execute_query(pool, sql, (index_theme, word, translate))

#Виведення
async def db_select_id_user(pool, name):
    sql = "SELECT id FROM users WHERE telegram_id = '%s'"
    result = await fetch_query(pool, sql, (name,))
    return result[0][0]

async def db_select_all_themes(pool, user_id):
    sql = "SELECT name FROM themes WHERE user_id = '%s'"
    result = await fetch_query(pool, sql, (user_id,))
    str_themes = "Список існуючих тем: "
    for theme in result:
        title = theme[0]
        str_themes += "\n- " + title
    
    return str_themes

async def db_select_all_themes_for_kb(pool, user_id):
    sql = "SELECT id,name FROM themes WHERE user_id = '%s'"
    result = await fetch_query(pool, sql, (user_id,))
    list_themes = []
    for id,theme in result:
        list_themes.append({"id": id, "name": theme})
    
    return list_themes

async def db_select_id_theme(pool, name):
    sql = "SELECT id FROM themes WHERE name = '%s'"
    result = await fetch_query(pool, sql, (name))
    return result[0][0]

async def db_select_all_word_in_theme(pool, theme_id):
    sql = "SELECT word, translation FROM words WHERE theme_id = '%s'"
    result = await fetch_query(pool, sql, (theme_id,))
    if not result:
        return []
    list_word = []
    count = 1
    for word, translation in result:
        list_word.append(f"{count}) {word} => {translation}")
        count += 1
    return list_word



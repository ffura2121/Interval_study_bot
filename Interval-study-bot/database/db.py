from connect import create_pool

async def execute_query(pool, sql): #Для змін у бд, CREATE, INSERT, UPDATE, DELETE
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql)
            await conn.commit()

async def fetch_query(pool, sql): # Для SELECT
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql)
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

async def add_user(pool, telegram_id, name):
    sql = "INSERT IGNORE INTO users (telegram_id, name) VALUES (%s, %s)"
    await execute_query(pool, sql, (telegram_id, name))


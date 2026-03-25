import asyncio
import connect as db
from db import (
    execute_query, fetch_query,
    create_db, create_table_users, create_table_themes, create_table_words, create_table_words_interval
)

async def init():
    await db.setup_pool()

    # await execute_query(db.pool, "DROP DATABASE tg_bot")


    #Створення бд
    # await execute_query(db.pool, create_db)

    #Створення таблиць
    # await execute_query(db.pool, create_table_users)
    # await execute_query(db.pool, create_table_themes)
    # await execute_query(db.pool, create_table_words)
    # await execute_query(db.pool, create_table_words_interval)


    users_index = await fetch_query(db.pool, "SHOW INDEX FROM users")
    themes_index = await fetch_query(db.pool, "SHOW INDEX FROM themes")
    words_index = await fetch_query(db.pool, "SHOW INDEX FROM words")
    words_interval_index = await fetch_query(db.pool, "SHOW INDEX FROM words_interval")

    print("Users index:", users_index)
    print("Themes index:", themes_index)
    print("Words index:", words_index)
    print("Words_interval:", words_interval_index)


    db.pool.close()
    await db.pool.wait_closed()
    print("База даних та таблиці створені")

if __name__ == "__main__":
    asyncio.run(init())








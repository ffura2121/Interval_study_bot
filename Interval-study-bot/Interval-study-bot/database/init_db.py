import asyncio
from connect import create_pool
from db import (
    execute_query, fetch_query,
    create_db, create_table_users, create_table_themes, create_table_words
)

async def init():
    pool = await create_pool()

    # await execute_query(pool, "DROP DATABASE db_for_tg_bot")


    #Створення бд
    # await execute_query(pool, create_db)

    #Створення таблиць
    # await execute_query(pool, create_table_users)
    # await execute_query(pool, create_table_themes)
    # await execute_query(pool, create_table_words)

    users_index = await fetch_query(pool, "SHOW INDEX FROM users")
    themes_index = await fetch_query(pool, "SHOW INDEX FROM themes")
    words_index = await fetch_query(pool, "SHOW INDEX FROM words")

    print("Users index:", users_index)
    print("Themes index:", themes_index)
    print("Words index:", words_index)


    pool.close()
    await pool.wait_closed()
    print("База даних та таблиці створені")

if __name__ == "__main__":
    asyncio.run(init())








from database.connect import create_pool
import aiomysql


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


create_db = "CREATE DATABASE db_for_yg_bot"

create_table = """
CREATE TABLE db_for_yg_bot.users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50)
)
"""

insert_user = "INSERT INTO my_db.users (name) VALUES ('Ivan')"

select_users = "SELECT * FROM my_db.users"

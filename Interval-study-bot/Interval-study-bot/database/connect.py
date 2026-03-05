import aiomysql

pool: aiomysql.Pool | None = None  # явна типізація

async def setup_pool():
    global pool
    if pool is None:
        pool = await aiomysql.create_pool(
            host="localhost",
            port=3306,
            user="root",
            password="root",
            db="tg_bot"
        )
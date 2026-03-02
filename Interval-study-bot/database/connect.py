import aiomysql

async def create_pool():
    return await aiomysql.create_pool(
        host="localhost",
        port=3306,
        user="root",
        password="root"
    )
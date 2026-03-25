import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import TOKEN
from func.handler import router
import database.connect as db
from database.db import db_select_reminder_1, db_select_reminder_2, db_select_reminder_3


bot = Bot(token=TOKEN)
dp = Dispatcher()

#============ Нагадувач ============

async def remainder():
    while True:
        try:
            theme_id = await db_select_reminder_1(db.pool)
            name = await db_select_reminder_2(db.pool, theme_id)
            telegram_id = await db_select_reminder_3(db.pool, theme_id)


            if theme_id:
                await bot.send_message(chat_id = telegram_id, text = f"Час повторювати слова з теми {name}")
        except Exception as e:
            print(f"Помилка: {e}")
        await asyncio.sleep(60)

async def main():
    await db.setup_pool()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
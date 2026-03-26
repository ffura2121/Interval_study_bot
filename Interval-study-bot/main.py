import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import TOKEN
from func.handler import router
import database.connect as db
import time
from database.db import db_select_reminder


bot = Bot(token=TOKEN)
dp = Dispatcher()

#============ Нагадувач ============
sent = {}

COOLDOWN = 8 * 60 * 60 # 8 годин


async def remainder():
    while True:
        try:
            telegram_id_theme_name = await db_select_reminder(db.pool)
            now = time.time()

            for telegram_id, names in telegram_id_theme_name.items():

                new_names = []

                for n in names:
                    key = (telegram_id, n)

                    # якщо ще ніколи не відправляли або пройшло 8 годин
                    if key not in sent or now - sent[key] >= COOLDOWN:
                        new_names.append(n)
                        sent[key] = now

                if not new_names:
                    continue

                text = f"Час повторювати слова у темах: {', '.join(new_names)}"
                await bot.send_message(chat_id=telegram_id, text=text)

        except Exception as e:
            print(f"Помилка: {e}")

        await asyncio.sleep(10)


async def main():
    await db.setup_pool()
    asyncio.create_task(remainder())
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
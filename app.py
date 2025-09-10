# app.py  (запускать именно его на Render)
import os
import asyncio
from flask import Flask, render_template
from aiogram import Bot, Dispatcher
from aiogram.types import Message

# --- настройки ---
API_TOKEN = os.getenv("BOT_TOKEN")  # обязательно добавь BOT_TOKEN в Render -> Environment
PORT = int(os.getenv("PORT", 5000))

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- Flask (фронт) ---
flask_app = Flask(__name__)

@flask_app.route("/")
def index():
    return render_template("index.html")

# --- aiogram (бот) ---
@dp.message()
async def echo_handler(message: Message):
    await message.answer("Привет! Бот работает через Render 🚀")

# --- запуск ---
async def start_telegram():
    await dp.start_polling(bot)

def start_flask():
    flask_app.run(host="0.0.0.0", port=PORT)

async def main():
    loop = asyncio.get_event_loop()
    # Flask нужно вынести в отдельный поток, он синхронный
    from concurrent.futures import ThreadPoolExecutor
    executor = ThreadPoolExecutor(1)
    loop.run_in_executor(executor, start_flask)

    # Параллельно запускаем бота
    await start_telegram()

if __name__ == "__main__":
    asyncio.run(main())

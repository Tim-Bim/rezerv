import asyncio
from flask import Flask
from threading import Thread
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

API_TOKEN = "7974895632:AAGB3h8gzFPS0paoowUELBZIaM3X4MekWWs"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# ---------- Flask ----------
app = Flask(__name__)

@app.route("/")
def index():
    return "Мини-апп работает!"

# ---------- aiogram ----------
@dp.message(CommandStart())
async def start_handler(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Открыть мини-апп", web_app=WebAppInfo(url="https://rezerv-jsnp.onrender.com/"))]],
        resize_keyboard=True
    )
    await message.answer("Нажми кнопку ниже, чтобы открыть мини-апп:", reply_markup=keyboard)

# ---------- Запуск aiogram в отдельном потоке ----------
def start_bot():
    asyncio.run(dp.start_polling(bot))

if __name__ == "__main__":
    # Старт бота в фоне
    Thread(target=start_bot).start()
    # Старт Flask для Render
    app.run(host="0.0.0.0", port=10000)

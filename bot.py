import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import WebAppInfo
from aiogram.filters import Command
from flask import Flask, render_template, send_from_directory
import threading

# ---------------------------
# Telegram Bot
# ---------------------------
API_TOKEN = "7974895632:AAGB3h8gzFPS0paoowUELBZIaM3X4MekWWs"  # вставляем напрямую

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot=bot)

@dp.message(Command("start"))
async def start_command(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(
                text="Открыть мини-апп",
                web_app=WebAppInfo(url="https://rezerv-jsnp.onrender.com/")  # сброс кеша
            )]
        ],
        resize_keyboard=True
    )
    await message.answer("Нажми кнопку ниже, чтобы открыть мини-апп:", reply_markup=keyboard)

async def run_bot():
    print("Бот запускается...")
    await dp.start_polling()

# ---------------------------
# Flask Web App
# ---------------------------
app = Flask(__name__, template_folder="templates", static_folder="static")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/static/<path:path>")
def send_static(path):
    return send_from_directory("static", path)

def run_flask():
    print("Веб-сервер запускается...")
    app.run(host="0.0.0.0", port=10000)

# ---------------------------
# Запуск обоих сервисов
# ---------------------------
if __name__ == "__main__":
    # Flask в отдельном потоке
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Telegram бот в asyncio
    asyncio.run(run_bot())

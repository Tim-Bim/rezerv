import os
import json
import threading
import asyncio
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from aiogram import Bot, Dispatcher, types
from aiogram.types import WebAppInfo
from aiogram.filters import Command


# ---------------------------
# Пути и настройки
# ---------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
DATA_FILE = os.path.join(BASE_DIR, "data.json")

for path in (TEMPLATE_DIR, STATIC_DIR, UPLOADS_DIR):
    if not os.path.exists(path):
        os.makedirs(path)


# ---------------------------
# Flask Web App
# ---------------------------
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

def load_candidates():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f) if f.read().strip() else []
    except:
        return []

def save_candidates(candidates):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(candidates, f, ensure_ascii=False, indent=2)

def new_id():
    return int(datetime.now().timestamp() * 1000)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/candidates", methods=["GET"])
def get_candidates():
    return jsonify(load_candidates())

@app.route("/api/candidates", methods=["POST"])
def add_candidate():
    payload = request.json
    if not payload or "candidate" not in payload:
        return jsonify({"error": "bad request"}), 400

    candidates = load_candidates()
    cand = payload["candidate"]

    if "id" in cand:  # обновление
        for i, c in enumerate(candidates):
            if c.get("id") == cand["id"]:
                candidates[i].update(cand)
                save_candidates(candidates)
                return jsonify({"status": "updated", "candidate": candidates[i]})

    # новый
    cand["id"] = new_id()
    cand.setdefault("created_at", datetime.now().isoformat())
    candidates.append(cand)
    save_candidates(candidates)
    return jsonify({"status": "created", "candidate": cand})

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOADS_DIR, filename)


# ---------------------------
# Telegram Bot (Aiogram)
# ---------------------------
API_TOKEN = "7974895632:AAGB3h8gzFPS0paoowUELBZIaM3X4MekWWs"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_command(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(
                text="Открыть мини-апп",
                web_app=WebAppInfo(url="https://rezerv-jsnp.onrender.com/")
            )]
        ],
        resize_keyboard=True
    )
    await message.answer("Нажми кнопку ниже, чтобы открыть мини-апп:", reply_markup=keyboard)


async def run_bot():
    print("[BOT] Бот запускается...")
    await dp.start_polling(bot)


def run_flask():
    port = int(os.environ.get("PORT", 5000))
    print(f"[FLASK] Сервер запущен на порту {port}")
    app.run(host="0.0.0.0", port=port, debug=True)


# ---------------------------
# Запуск обоих сервисов
# ---------------------------
if __name__ == "__main__":
    # Flask в отдельном потоке
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Telegram бот
    asyncio.run(run_bot())

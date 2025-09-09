import os
import json
import asyncio
import threading
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from aiogram import Bot, Dispatcher, types
from aiogram.types import WebAppInfo
from aiogram.filters import Command

# ---------------------------
# ЛОГИРОВАНИЕ
# ---------------------------
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# ---------------------------
# ПУТИ И ФАЙЛЫ
# ---------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
DATA_FILE = os.path.join(BASE_DIR, "data.json")

for path in (TEMPLATE_DIR, STATIC_DIR, UPLOADS_DIR):
    os.makedirs(path, exist_ok=True)

# ---------------------------
# FLASK Web App
# ---------------------------
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
CORS(app)  # Разрешаем кросс-доменные запросы

def load_candidates():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = f.read().strip()
            return json.loads(data) if data else []
    except Exception as e:
        logger.error(f"Ошибка при загрузке кандидатов: {e}")
        return []

def save_candidates(candidates):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(candidates, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Ошибка при сохранении кандидатов: {e}")

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
# TELEGRAM BOT (Aiogram 3.x)
# ---------------------------
API_TOKEN = os.environ.get("TG_API_TOKEN", "7974895632:AAGB3h8gzFPS0paoowUELBZIaM3X4MekWWs")

if not API_TOKEN or API_TOKEN == "PUT-YOUR-TOKEN-HERE":
    raise RuntimeError("❌ Не задан токен Telegram-бота! Укажи его в переменной окружения TG_API_TOKEN")

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

# ---------------------------
# ЗАПУСК
# ---------------------------
async def start_bot():
    logger.info("[BOT] Бот запускается...")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка в работе бота: {e}")

def start_flask():
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"[FLASK] Сервер запущен на порту {port}")
    app.run(host="0.0.0.0", port=port, debug=False)

if __name__ == "__main__":
    # Flask в отдельном потоке
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()

    # Запуск Telegram-бота (основной поток)
    asyncio.run(start_bot())

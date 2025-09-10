import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import WebAppInfo

# -----------------------------
# Настройки
# -----------------------------
API_TOKEN = "7974895632:AAGB3h8gzFPS0paoowUELBZIaM3X4MekWWs"  # <--- вставь свой токен
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"https://rezerv-jsnp.onrender.com{WEBHOOK_PATH}"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
DATA_FILE = os.path.join(BASE_DIR, "data.json")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")

# -----------------------------
# Проверка директорий
# -----------------------------
for folder in [TEMPLATE_DIR, STATIC_DIR, UPLOADS_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f"[INFO] Создана папка: {folder}")

# -----------------------------
# Flask App
# -----------------------------
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

def load_candidates():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except Exception as e:
        print(f"[ERROR] load_candidates: {e}")
        return []

def save_candidates(candidates):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(candidates, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[ERROR] save_candidates: {e}")

def new_id():
    return int(datetime.now().timestamp() * 1000)

# -----------------------------
# Flask Routes для мини-аппа
# -----------------------------
@app.route("/")
def index():
    template_name = "index.html"
    template_path = os.path.join(TEMPLATE_DIR, template_name)
    if not os.path.exists(template_path):
        return f"Template {template_name} not found!", 500
    return render_template(template_name)

@app.route("/api/candidates", methods=["GET"])
def get_candidates():
    return jsonify(load_candidates())

@app.route("/api/candidates", methods=["POST"])
def add_or_update_candidate():
    payload = request.json
    if not payload:
        return jsonify({"error": "no json"}), 400

    candidates = load_candidates()
    cand = payload.get("candidate")
    if not cand:
        return jsonify({"error": "candidate missing"}), 400

    cid = cand.get("id")
    if cid:
        for i, c in enumerate(candidates):
            if c.get("id") == cid:
                cand.setdefault("created_at", c.get("created_at"))
                candidates[i] = cand
                save_candidates(candidates)
                return jsonify({"status": "updated", "candidate": cand})

    cand["id"] = new_id()
    cand.setdefault("created_at", datetime.now().isoformat())
    cand.setdefault("status", "normal")
    cand.setdefault("reserved", True)
    cand.setdefault("notCalled", True)
    cand.setdefault("called", False)
    cand.setdefault("interning", False)
    cand.setdefault("hired", False)
    cand.setdefault("rejected", False)
    cand.setdefault("callback_date", None)
    cand.setdefault("intern_days", 0)
    cand.setdefault("intern_place", "")
    cand.setdefault("work_time", "permanent")

    candidates.append(cand)
    save_candidates(candidates)
    return jsonify({"status": "created", "candidate": cand})

@app.route("/api/candidates/<int:cand_id>", methods=["DELETE"])
def delete_candidate(cand_id):
    candidates = load_candidates()
    new = [c for c in candidates if c.get("id") != cand_id]
    save_candidates(new)
    return jsonify({"status": "deleted"})

@app.route("/api/candidates/<int:cand_id>/patch", methods=["POST"])
def patch_candidate(cand_id):
    payload = request.json or {}
    candidates = load_candidates()
    for i, c in enumerate(candidates):
        if c.get("id") == cand_id:
            c.update(payload)
            candidates[i] = c
            save_candidates(candidates)
            return jsonify({"status": "ok", "candidate": c})
    return jsonify({"error": "not found"}), 404

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOADS_DIR, filename)

# -----------------------------
# Telegram Bot через Webhook
# -----------------------------
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

# -----------------------------
# Webhook для Telegram
# -----------------------------
@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    update = types.Update(**request.json)
    asyncio.run(dp.process_update(update))
    return "ok"

# -----------------------------
# Создание webhook
# -----------------------------
@app.route("/set_webhook")
def set_webhook():
    import asyncio
    async def main():
        await bot.set_webhook(WEBHOOK_URL)
    asyncio.run(main())
    return f"Webhook установлен на {WEBHOOK_URL}"

# -----------------------------
# Запуск
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🌐 Flask запущен на порту {port}")
    app.run(host="0.0.0.0", port=port, debug=False)

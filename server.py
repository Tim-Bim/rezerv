from flask import Flask, render_template, request, jsonify, send_from_directory
import json
import os
from datetime import datetime

# ----------------- Пути -----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
DATA_FILE = os.path.join(BASE_DIR, "data.json")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")

# ----------------- Проверка директорий -----------------
if not os.path.exists(TEMPLATE_DIR):
    os.makedirs(TEMPLATE_DIR)
    print(f"[INFO] Создана папка templates: {TEMPLATE_DIR}")
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)
    print(f"[INFO] Создана папка static: {STATIC_DIR}")
if not os.path.exists(UPLOADS_DIR):
    os.makedirs(UPLOADS_DIR)
    print(f"[INFO] Создана папка uploads: {UPLOADS_DIR}")

# ----------------- Создаём app -----------------
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

# ----------------- Работа с кандидатами -----------------
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

# ----------------- Маршруты -----------------
@app.route("/")
def index():
    try:
        return render_template("index.html")
    except Exception as e:
        return f"Template error: {e}", 500

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
    if cid:  # 🔄 update
        for i, c in enumerate(candidates):
            if c.get("id") == cid:
                cand.setdefault("created_at", c.get("created_at"))
                candidates[i] = cand
                save_candidates(candidates)
                return jsonify({"status": "updated", "candidate": cand})

    # 🆕 new candidate
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

# ----------------- Загрузка файлов -----------------
@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOADS_DIR, filename)

# ----------------- Запуск -----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"[INFO] Flask запущен на порту {port}")
    app.run(host="0.0.0.0", port=port, debug=True)

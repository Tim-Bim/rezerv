from flask import Flask, render_template, request, jsonify
import json, os
from datetime import datetime

app = Flask(__name__, static_folder="static", template_folder="templates")
DATA_FILE = "data.json"


def load_candidates():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except Exception:
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

    # default values
    cand.setdefault("status", "normal")
    cand.setdefault("reserved", True)
    cand.setdefault("notCalled", True)     # не обдзвонений
    cand.setdefault("called", False)
    cand.setdefault("interning", False)
    cand.setdefault("hired", False)
    cand.setdefault("rejected", False)

    # нові поля
    cand.setdefault("callback_date", None)   # нагадування (дата)
    cand.setdefault("intern_days", 0)        # кількість днів стажування
    cand.setdefault("intern_place", "")      # текстове поле для стажування
    cand.setdefault("work_time", "permanent")  # постійно/тимчасово

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


if __name__ == "__main__":
    app.run(debug=True)

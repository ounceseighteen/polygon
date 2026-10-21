import sqlite3
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)
app.secret_key = "super-secret-key-12345"  # плохо: секрет в коде
DB = "app.db"


def get_db():
    # плохо: новое соединение на каждый вызов, без WAL
    conn = sqlite3.connect(DB)
    return conn


@app.route("/")
def index():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM items")
    rows = cur.fetchall()
    items = []
    for r in rows:
        items.append({"id": r[0], "name": r[1], "price": r[2], "qty": r[3]})
    conn.close()
    return render_template("index.html", items=items)


@app.route("/api/items")
def api_items():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM items")
    rows = cur.fetchall()
    result = []
    for r in rows:
        # плохо: N+1
        cur2 = conn.cursor()
        cur2.execute(f"SELECT COUNT(*) FROM orders WHERE item_id = {r[0]}")
        cnt = cur2.fetchone()[0]
        result.append({"id": r[0], "name": r[1], "price": r[2],
                       "qty": r[3], "orders": cnt})
    conn.close()
    return jsonify(result)


@app.route("/api/orders", methods=["POST"])
def create_order():
    try:
        data = request.get_json()
        item_id = data["item_id"]
        qty = data["qty"]
        conn = get_db()
        cur = conn.cursor()
        # плохо: f-string SQL
        cur.execute(f"INSERT INTO orders (item_id, qty) VALUES ({item_id}, {qty})")
        conn.commit()
        conn.close()
        return jsonify({"ok": True}), 201
    except Exception:
        pass
    return jsonify({"ok": False}), 500


@app.route("/api/report")
def report():
    frm = request.args.get("from", "2000-01-01")
    to = request.args.get("to", "2100-01-01")
    conn = get_db()
    cur = conn.cursor()
    # плохо: нет индексов
    cur.execute(f"SELECT * FROM orders WHERE created_at BETWEEN '{frm}' AND '{to}'")
    orders = cur.fetchall()
    total = 0
    by_item = {}
    for o in orders:
        total += o[2]
        by_item[o[1]] = by_item.get(o[1], 0) + o[2]
    conn.close()
    return jsonify({"total": total, "by_item": by_item})


if __name__ == "__main__":
    import sys
    port = 5001
    if "--port" in sys.argv:
        port = int(sys.argv[sys.argv.index("--port") + 1])
    app.run(host="127.0.0.1", port=port, debug=True, threaded=False)
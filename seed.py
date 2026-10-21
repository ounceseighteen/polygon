import sqlite3, random, datetime

conn = sqlite3.connect("app.db")
cur = conn.cursor()
cur.executescript("""
DROP TABLE IF EXISTS items;
DROP TABLE IF EXISTS orders;
CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT, price REAL, qty INTEGER);
CREATE TABLE orders (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     item_id INTEGER, qty INTEGER, created_at TEXT);
""")

items = [("Товар %d" % i, round(random.uniform(10, 1000), 2),
          random.randint(0, 500)) for i in range(1, 501)]
cur.executemany("INSERT INTO items (name, price, qty) VALUES (?, ?, ?)", items)

start = datetime.date(2024, 1, 1)
orders = []
for _ in range(5000):
    d = start + datetime.timedelta(days=random.randint(0, 700))
    orders.append((random.randint(1, 500), random.randint(1, 10), d.isoformat()))
cur.executemany(
    "INSERT INTO orders (item_id, qty, created_at) VALUES (?, ?, ?)", orders)

conn.commit()
conn.close()
print("seeded: 500 items, 5000 orders")
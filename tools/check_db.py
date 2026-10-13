import os
import sqlite3

db_path = "data/jarvis.db"
if not os.path.exists(db_path):
    print("Database not found!")
    exit(0)

conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [r[0] for r in cur.fetchall()]
print("Tables in jarvis.db:")
for t in tables:
    cur.execute(f"SELECT COUNT(*) FROM {t};")
    count = cur.fetchone()[0]
    print(f"  - {t}: {count} records")

conn.close()

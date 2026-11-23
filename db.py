import sqlite3
from datetime import datetime

DB_FILE = "radar.db"

def get_connection():
    return sqlite3.connect(DB_FILE)

def init_db():
    conn = get_connection()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS vacancies (
    id INTEGER PRIMARY KEY,
    company TEXT,
    title TEXT,
    link TEXT UNIQUE,
    first_seen TEXT)
    """)
    conn.commit()
    conn.close()

def add_vacancy(company, title, link):
    conn = get_connection()
    cur = conn.execute(
        "INSERT OR IGNORE INTO vacancies (company, title, link, first_seen) VALUES (?, ?, ?, ?)",
        (company, title, link, datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()
    is_new = cur.rowcount == 1
    conn.close()
    return is_new

def get_all_vacancies():
    conn = get_connection()
    rows = conn.execute("SELECT company, title, link FROM vacancies ORDER BY company").fetchall()
    conn.close()
    return rows
if __name__ == "__main__":
    init_db()
    print(add_vacancy("test", "Test job", "https://example.com/test"))
    print(add_vacancy("test", "Test job", "https://example.com/test"))
    for row in get_all_vacancies():
        print(row)
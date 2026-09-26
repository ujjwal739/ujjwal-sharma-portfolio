import sqlite3
import os

DB_PATH = os.path.join('instance', 'portfolio.db')

def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS certifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            issuer TEXT,
            date_earned TEXT,
            file_name TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def init_projects_table():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            file_name TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


def init_about_table():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS about (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            bio TEXT
        )
    ''')
    row = conn.execute('SELECT * FROM about WHERE id = 1').fetchone()
    if row is None:
        default_bio = "Cybersecurity Student | Social Engineering Analyst & Penetration Tester | Digital Forensics & CTF Player | Python + Linux.\\n\\nThat's the short version. The longer one: I spend my time finding vulnerabilities before the bad guys do, digging through digital evidence, and solving CTF challenges for fun — all powered by Python and a terminal that never closes."
        conn.execute('INSERT INTO about (id, bio) VALUES (1, ?)', (default_bio,))
    conn.commit()
    conn.close()


def init_skills_table():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

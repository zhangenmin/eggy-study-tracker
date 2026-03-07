import sqlite3
from app.config import DB_PATH

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    # 学习记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS study_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            duration INTEGER NOT NULL,
            study_date TEXT NOT NULL
        )
    ''')
    # 用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    # 预置用户
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('root', 'Jschrj83130911!', 'admin')")
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('eggy', '123456', 'child')")
    
    conn.commit()
    conn.close()

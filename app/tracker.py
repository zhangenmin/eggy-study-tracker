from app.database import get_db_connection
from datetime import date

def add_session(subject, duration):
    today = date.today().isoformat()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO study_sessions (subject, duration, study_date) VALUES (?, ?, ?)",
        (subject, duration, today)
    )
    conn.commit()
    conn.close()

def get_today_sessions():
    today = date.today().isoformat()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM study_sessions WHERE study_date = ?", (today,))
    rows = cursor.fetchall()
    conn.close()
    return rows

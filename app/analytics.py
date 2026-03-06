from app.database import get_db_connection
from datetime import date

def get_today_total_minutes():
    today = date.today().isoformat()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(duration) as total FROM study_sessions WHERE study_date = ?", (today,))
    result = cursor.fetchone()
    conn.close()
    return result['total'] if result['total'] else 0

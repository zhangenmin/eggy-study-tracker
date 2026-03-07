from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.database import init_db, get_db_connection
from app import tracker, analytics
import sqlite3
from datetime import date

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    username: str
    password: str

class TaskCreate(BaseModel):
    title: str
    points: int = 10
    duration: int = 20

class TaskComplete(BaseModel):
    task_id: int
    points: int
    title: str

class PointsAdjust(BaseModel):
    amount: int
    reason: str

@app.on_event("startup")
def startup():
    init_db()

@app.post("/api/login")
def login(data: LoginRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (data.username, data.password))
    user = cursor.fetchone()
    conn.close()
    if user:
        return {"success": True, "user": dict(user)}
    raise HTTPException(status_code=401)

@app.get("/api/status")
def get_status():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(duration) FROM study_sessions WHERE is_template = 0")
    total = cursor.fetchone()[0] or 0
    conn.close()
    return {"total_points": total}

@app.get("/api/tasks")
def get_tasks():
    today = date.today().isoformat()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 强制标记：查询模板
    cursor.execute("SELECT id, subject, duration FROM study_sessions WHERE is_template = 1")
    templates = cursor.fetchall()
    
    result = []
    for t in templates:
        t_id, t_subject, t_duration = t
        # 核心：检查今天是否已完成该模板任务
        cursor.execute("SELECT id FROM study_sessions WHERE is_template = 0 AND subject = ? AND study_date = ?", (f"完成: {t_subject}", today))
        completed_record = cursor.fetchone()
        
        result.append({
            "id": t_id,
            "title": t_subject,
            "duration": t_duration,
            "points": 10,
            "completed": completed_record is not None
        })
    conn.close()
    return result

@app.post("/api/tasks")
def create_task(task: TaskCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO study_sessions (subject, duration, study_date, is_template) VALUES (?, ?, date('now'), 1)", 
                   (task.title, task.duration))
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.post("/api/tasks/delete/{task_id}")
def delete_task_post(task_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM study_sessions WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.post("/api/tasks/complete")
def complete_task_api(data: TaskComplete):
    today = date.today().isoformat()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO study_sessions (subject, duration, study_date, is_template) VALUES (?, ?, ?, 0)", 
                   (f"完成: {data.title}", data.points, today))
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.get("/api/milestones")
def get_milestones():
    return [
        {"id": 1, "name": "冒险蛋", "icon_url": "http://23.95.119.227:9000/eggy-assets/1772799362-file_52---b825b10e-8f38-41ed-9c0c-57827bb57a1d.jpg"},
        {"id": 2, "name": "大魔王", "icon_url": "http://23.95.119.227:9000/eggy-assets/1772799362-file_53---5a73cc39-39af-4cb5-8826-802c0ddefbc1.jpg"},
        {"id": 3, "name": "超级蛋仔", "icon_url": "http://23.95.119.227:9000/eggy-assets/1772799362-file_59---fefe8feb-2214-4c5d-987d-6aaca606ca41.jpg"}
    ]

@app.post("/api/status/adjust")
def adjust_points(data: PointsAdjust):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO study_sessions (subject, duration, study_date, is_template) VALUES (?, ?, date('now'), 0)", 
                   (f"管理员调整: {data.reason}", data.amount))
    conn.commit()
    conn.close()
    return {"message": "Success"}

def run():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

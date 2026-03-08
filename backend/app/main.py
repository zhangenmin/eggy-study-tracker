from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mysql.connector
from minio import Minio
import redis
import json
import os
import time
import io
from datetime import datetime
from typing import List, Optional

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Config
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Jschrj83130911!",
    "database": "study_tracker",
    "charset": "utf8mb4"
}

MINIO_CONFIG = {
    "endpoint": "localhost:9000",
    "access_key": "admin",
    "secret_key": "Jschrj83130911!",
    "secure": False
}

# Redis Setup
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

minio_client = Minio(**MINIO_CONFIG)
BUCKET_NAME = "eggy-assets"

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

# --- Schemas ---
class PointsAdjust(BaseModel):
    amount: int
    reason: str

class LoginRequest(BaseModel):
    username: str
    password: str

class TaskComplete(BaseModel):
    task_id: int
    points: int
    title: str

class TaskCreate(BaseModel):
    title: str
    description: str
    type: str
    duration: int
    points: int
    icon_color: str

# --- API Endpoints ---

@app.post("/api/login")
def login(data: LoginRequest):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, username, role FROM users WHERE username = %s AND password = %s", (data.username, data.password))
    user = cursor.fetchone()
    db.close()
    if user:
        return {"success": True, "user": user}
    else:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

@app.get("/api/status")
def get_status():
    # 尝试从 Redis 获取缓存
    cached_status = redis_client.get("study_status")
    if cached_status:
        return json.loads(cached_status)
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT total_points FROM points LIMIT 1")
    res = cursor.fetchone() or {"total_points": 0}
    db.close()
    
    # 写入缓存 (有效期 60 秒)
    redis_client.setex("study_status", 60, json.dumps(res))
    return res

@app.post("/api/status/adjust")
def adjust_points(data: PointsAdjust):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE points SET total_points = total_points + %s", (data.amount,))
    cursor.execute("INSERT INTO study_logs (type, content, duration, points_earned) VALUES (%s, %s, %s, %s)", 
                   ('手动调整', data.reason, 0, data.amount))
    db.commit()
    db.close()
    
    # 清除受影响的缓存
    redis_client.delete("study_status")
    return {"message": "Success"}

@app.get("/api/tasks")
def get_tasks():
    cached_tasks = redis_client.get("study_tasks")
    if cached_tasks:
        return json.loads(cached_tasks)

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SET NAMES utf8mb4")
    cursor.execute("SELECT * FROM tasks")
    res = cursor.fetchall()
    db.close()
    
    redis_client.setex("study_tasks", 300, json.dumps(res))
    return res

@app.post("/api/tasks/complete")
def complete_task(data: TaskComplete):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE points SET total_points = total_points + %s", (data.points,))
    cursor.execute("INSERT INTO study_logs (type, content, duration, points_earned) VALUES (%s, %s, %s, %s)", 
                   ('任务完成', f"完成了任务: {data.title}", 0, data.points))
    db.commit()
    db.close()
    
    # 积分变动，清除状态缓存
    redis_client.delete("study_status")
    return {"message": "Points added"}

@app.get("/api/milestones")
def get_milestones():
    cached_medals = redis_client.get("study_medals")
    if cached_medals:
        return json.loads(cached_medals)

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SET NAMES utf8mb4")
    cursor.execute("SELECT * FROM milestones")
    res = cursor.fetchall()
    db.close()
    
    redis_client.setex("study_medals", 3600, json.dumps(res))
    return res

@app.post("/api/tasks")
def create_task(task: TaskCreate):
    db = get_db()
    cursor = db.cursor()
    query = "INSERT INTO tasks (title, description, type, duration, points, icon_color) VALUES (%s, %s, %s, %s, %s, %s)"
    cursor.execute(query, (task.title, task.description, task.type, task.duration, task.points, task.icon_color))
    db.commit()
    db.close()
    
    # 任务变更，清除任务列表缓存
    redis_client.delete("study_tasks")
    return {"message": "Created"}

@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM tasks WHERE id=%s", (task_id,))
    db.commit()
    db.close()
    
    redis_client.delete("study_tasks")
    return {"message": "Deleted"}

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    file_name = f"{int(time.time())}-{file.filename}"
    file_data = await file.read()
    minio_client.put_object(
        BUCKET_NAME, file_name, data=io.BytesIO(file_data), length=len(file_data), content_type=file.content_type
    )
    return {"url": f"http://23.95.119.227:9000/{BUCKET_NAME}/{file_name}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

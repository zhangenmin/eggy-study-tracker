# 蛋仔成长基地 v6.0 (Vue + Python Edition)

基于 Vue 3 + FastAPI + MySQL + Redis + MinIO 的全栈学习追踪系统。

## 技术栈
- **前端**: Vue 3 (CDN), Tailwind CSS, Animate.css
- **后端**: Python 3.12, FastAPI, Uvicorn
- **存储**: MySQL (数据), MinIO (图片素材), Redis (缓存)

## 快速启动
1. 后端: `pip install fastapi uvicorn mysql-connector-python minio redis python-multipart`
2. 启动后端: `python app/main.py`
3. 启动前端: `python -m http.server 80`

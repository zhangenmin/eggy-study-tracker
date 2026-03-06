from app.database import init_db
from app.cli import main_menu

def run():
    # 确保数据库初始化
    init_db()
    # 启动 CLI 界面
    main_menu()

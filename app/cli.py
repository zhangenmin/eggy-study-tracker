from app import tracker, analytics

def main_menu():
    while True:
        print("\n--- 🥚 蛋仔学习追踪器 CLI ---")
        print("1. Add Study (添加学习记录)")
        print("2. View Today (查看今日记录)")
        print("3. Today Total (今日总时长)")
        print("4. Exit (退出)")
        
        choice = input("\n请选择功能 (1-4): ")
        
        if choice == '1':
            subject = input("请输入学科: ")
            try:
                duration = int(input("请输入学习时长 (分钟): "))
                tracker.add_session(subject, duration)
                print("✅ 记录添加成功！")
            except ValueError:
                print("❌ 时长必须是数字哦！")
                
        elif choice == '2':
            sessions = tracker.get_today_sessions()
            print("\n📅 今日学习明细:")
            for s in sessions:
                print(f"- {s['subject']}: {s['duration']} 分钟")
            if not sessions:
                print("今天还没有记录，加油哦！")
                
        elif choice == '3':
            total = analytics.get_today_total_minutes()
            print(f"\n🔥 今日累计学习时长: {total} 分钟")
            
        elif choice == '4':
            print("再见，蛋仔！下课啦~")
            break
        else:
            print("❌ 选错啦，请重新输入 1-4 之间的数字。")

import os
import sys
import subprocess
import webbrowser
import time

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def main():
    print("=" * 60)
    print("🌟 FASHION STORE & AI STYLIST CHATBOT SYSTEM")
    print("=" * 60)
    print("Khởi động hệ thống Đồ án / BTL Chatbot Tư Vấn Thời Trang...")
    
    # 1. Seed database nếu chưa có dữ liệu
    db_file = os.path.join(os.path.dirname(__file__), "fashion_store.db")
    if not os.path.exists(db_file):
        print("⚡ Khởi tạo cơ sở dữ liệu và nạp dữ liệu mẫu ban đầu...")
        subprocess.run([sys.executable, os.path.join("backend", "seed_data.py")], check=True)
    
    print("\n🚀 Server đang khởi chạy tại: http://127.0.0.1:8000")
    print("📌 Trang chủ Cửa hàng: http://127.0.0.1:8000")
    print("🤖 Studio Tư Vấn AI: http://127.0.0.1:8000/stylist")
    print("📚 Tài liệu API Docs (Swagger): http://127.0.0.1:8000/docs")
    print("=" * 60)
    print("Nhấn Ctrl + C để dừng server.\n")

    # Khởi chạy uvicorn
    try:
        import uvicorn
        uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
    except KeyboardInterrupt:
        print("\n🛑 Đã dừng máy chủ thành công.")

if __name__ == "__main__":
    main()

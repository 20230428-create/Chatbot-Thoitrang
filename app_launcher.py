import os
import sys
import io
import threading
import time
import webbrowser

# Ensure UTF-8 output on Windows console safely
if sys.stdout and hasattr(sys.stdout, 'buffer'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, 'buffer'):
    try:
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

# Ensure backend directory is in sys.path
if getattr(sys, 'frozen', False):
    current_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
else:
    current_dir = os.path.dirname(os.path.abspath(__file__))

backend_dir = os.path.join(current_dir, "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from backend.database import init_db, DB_PATH
from backend.main import app
import backend.seed_data as seed_data
import uvicorn

def open_browser():
    time.sleep(1.8)
    url = "http://127.0.0.1:8000"
    print(f"\n[+] Dang tu dong mo trinh duyet tai: {url}")
    webbrowser.open(url)

def main():
    print("=" * 65)
    print("[*] FASHION AI STYLIST - CHATBOT TU VAN THOI TRANG THONG MINH")
    print("=" * 65)
    print("[*] Dang khoi dong may chu ung dung...")
    
    # Check and init database with guaranteed data
    from backend.database import ensure_database_ready
    ensure_database_ready()
        
    print("[+] Co so du lieu SQLite da san sang.")
    print("[+] Dia chi truy cap: http://127.0.0.1:8000")
    print("=" * 65)
    print("[!] De tat ung dung, ban chi can dong cua so nay lai (hoac nhan Ctrl + C).")
    print("=" * 65 + "\n")

    # Launch browser automatically in background
    threading.Thread(target=open_browser, daemon=True).start()

    # Run Uvicorn directly with app instance
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

if __name__ == "__main__":
    main()

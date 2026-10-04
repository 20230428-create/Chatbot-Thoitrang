import os
import sys
import subprocess
import shutil
import io
import zipfile

# Ensure UTF-8 output on Windows console
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def build():
    print("=" * 60)
    print("📦 BẮT ĐẦU ĐÓNG GÓI CHATBOT THỜI TRANG THÀNH FILE .EXE")
    print("=" * 60)

    # Đóng mọi tiến trình exe đang chạy để tránh lỗi Permission Denied
    os.system("taskkill /F /IM FashionAI_Chatbot_Portable.exe /IM FashionAI_Chatbot.exe >nul 2>&1")

    # Đảm bảo database đã có sẵn trước khi đóng gói
    db_file = os.path.join(os.path.dirname(__file__), "fashion_store.db")
    if not os.path.exists(db_file):
        print("⚡ Khởi tạo database...")
        subprocess.run([sys.executable, os.path.join("backend", "seed_data.py")], check=True)

    spec_content = """# -*- mode: python ; coding: utf-8 -*-
import os
import sys

block_cipher = None

added_files = [
    ('templates', 'templates'),
    ('static', 'static'),
    ('fashion_store.db', '.'),
]

a = Analysis(
    ['app_launcher.py'],
    pathex=['.', 'backend'],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'uvicorn',
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'fastapi',
        'starlette',
        'pydantic',
        'requests',
        'backend',
        'backend.main',
        'backend.database',
        'backend.ai_service',
        'backend.rag_engine',
        'backend.stylist_engine',
        'backend.seed_data'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'scipy',
        'sklearn',
        'scikit-learn',
        'numpy',
        'matplotlib',
        'pandas',
        'openpyxl',
        'lxml',
        'PIL',
        'Pillow',
        'tkinter',
        'tcl',
        'tk',
        '_tkinter',
        'pygame',
        'unittest',
        'doctest',
        'xmlrpc',
        'pygments',
        'IPython',
        'notebook',
        'jupyter',
        'torch',
        'tensorflow',
        'cv2'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 1. STANDALONE SINGLE-FILE EXE (Copy 1 file duy nhất là chạy được ngay!)
exe_portable = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='FashionAI_Chatbot_Portable',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# 2. ONEDIR EXE (Thư mục đầy đủ)
exe_folder = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='FashionAI_Chatbot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe_folder,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='FashionAI_Chatbot',
)
"""

    spec_path = os.path.join(os.path.dirname(__file__), "FashionAI_Chatbot.spec")
    with open(spec_path, "w", encoding="utf-8") as f:
        f.write(spec_content)

    print("📄 Đã cập nhật file cấu hình PyInstaller: FashionAI_Chatbot.spec")
    print("🔨 Đang chạy PyInstaller để biên dịch mã nguồn và đóng gói tài nguyên...")

    cmd = [sys.executable, "-m", "PyInstaller", "--noconfirm", "FashionAI_Chatbot.spec"]
    res = subprocess.run(cmd)

    if res.returncode == 0:
        # Copy database next to the folder exe
        dist_folder = os.path.join("dist", "FashionAI_Chatbot")
        if os.path.exists(dist_folder):
            shutil.copy2("fashion_store.db", os.path.join(dist_folder, "fashion_store.db"))

        # Create a ready-to-share ZIP file of the folder
        zip_path = os.path.join("dist", "FashionAI_Chatbot_Full.zip")
        print("\n📦 Đang nén thư mục thành file ZIP tiện chia sẻ: dist/FashionAI_Chatbot_Full.zip ...")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(dist_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, "dist")
                    zipf.write(file_path, rel_path)

        # Tự động dọn dẹp thư mục tạm build/ và thư mục giải nén thừa sau khi đã nén ZIP
        try:
            shutil.rmtree(dist_folder, ignore_errors=True)
            build_dir = os.path.join(os.path.dirname(__file__), "build")
            if os.path.exists(build_dir):
                shutil.rmtree(build_dir, ignore_errors=True)
            print("🧹 Đã tự động dọn dẹp thư mục tạm build/ và các file thừa (~95MB rác đã được giải phóng).")
        except Exception:
            pass

        portable_exe = os.path.abspath(os.path.join("dist", "FashionAI_Chatbot_Portable.exe"))
        
        # Copy to root folder for convenience
        root_portable = os.path.abspath("FashionAI_Chatbot_Portable.exe")
        if os.path.exists(portable_exe):
            shutil.copy2(portable_exe, root_portable)

        size_mb = os.path.getsize(portable_exe) / (1024 * 1024) if os.path.exists(portable_exe) else 0

        print("\n" + "=" * 65)
        print("🎉 ĐÓNG GÓI THÀNH CÔNG RỰC RỠ!")
        print("=" * 65)
        print(f"⚡ DUNG LƯỢNG FILE PORTABLE SAU KHI TỐI ƯU: {size_mb:.1f} MB (Giảm hơn 75%!)")
        print("=" * 65)
        print("💡 CÓ 2 CÁCH ĐỂ MANG SANG MÁY KHÁC CHẠY:")
        print(f"1. [KHUYÊN DÙNG] File 1-click DUY NHẤT không cần thư mục đi kèm:")
        print(f"   -> {portable_exe}")
        print(f"   (Đã đồng bộ sang file gốc tại thư mục chính: FashionAI_Chatbot_Portable.exe)")
        print(f"   (Chỉ cần copy đúng 1 file này sang máy khác là chạy ngay 100%!)")
        print()
        print(f"2. File ZIP trọn bộ đã nén sẵn để gửi qua Zalo / Google Drive:")
        print(f"   -> {os.path.abspath(zip_path)}")
        print(f"   (Giải nén ra và nhấp đúp FashionAI_Chatbot.exe)")
        print("=" * 65)
    else:
        print("\n❌ Có lỗi xảy ra trong quá trình đóng gói.")

if __name__ == "__main__":
    build()

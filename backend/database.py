import sqlite3
import json
import os
import sys
import shutil
from typing import List, Dict, Any, Optional

if getattr(sys, 'frozen', False):
    DB_DIR = os.path.dirname(sys.executable)
else:
    DB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_PATH = os.path.join(DB_DIR, "fashion_store.db")

# If running frozen and DB doesn't exist yet, copy from bundle if present
if getattr(sys, 'frozen', False) and not os.path.exists(DB_PATH):
    bundled_db = os.path.join(getattr(sys, '_MEIPASS', ''), "fashion_store.db")
    if os.path.exists(bundled_db):
        try:
            shutil.copy2(bundled_db, DB_PATH)
        except Exception:
            pass

def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=20.0)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Categories
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        slug TEXT NOT NULL UNIQUE,
        description TEXT
    );
    """)
    
    # 2. Products
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER,
        category_name TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        price INTEGER NOT NULL,
        original_price INTEGER,
        color TEXT NOT NULL,
        sizes_json TEXT NOT NULL, -- JSON list: ["S", "M", "L", "XL"]
        gender TEXT NOT NULL,     -- Nam, Nu, Unisex
        style TEXT NOT NULL,      -- Cong so, Casual, Streetwear, Du tiec, Han Quoc, v.v.
        material TEXT,
        season TEXT,
        occasion TEXT,           -- Di lam, Du tiec, Dao pho, Hen ho, Du lich, v.v.
        image TEXT NOT NULL,
        stock INTEGER DEFAULT 50,
        rating REAL DEFAULT 4.8,
        reviews_count INTEGER DEFAULT 12,
        FOREIGN KEY (category_id) REFERENCES categories (id)
    );
    """)
    
    # 3. Chat History
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        role TEXT NOT NULL, -- user / assistant
        message TEXT NOT NULL,
        recommended_products_json TEXT, -- JSON array of product IDs or objects
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # 4. Settings / Config
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    );
    """)
    
    conn.commit()
    conn.close()

def ensure_database_ready():
    init_db()
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products")
        count = cursor.fetchone()[0]
        conn.close()
        if count == 0:
            try:
                import backend.seed_data as seed_data
            except ImportError:
                import seed_data
            seed_data.seed()
    except Exception as e:
        print(f"[!] Warning checking database: {e}")

def get_all_categories() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categories ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_all_products() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    result = []
    for row in rows:
        item = dict(row)
        item["sizes"] = json.loads(item["sizes_json"]) if item.get("sizes_json") else []
        result.append(item)
    return result

def get_product_by_id(product_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    item = dict(row)
    item["sizes"] = json.loads(item["sizes_json"]) if item.get("sizes_json") else []
    return item

def filter_products(
    category_name: Optional[str] = None,
    gender: Optional[str] = None,
    color: Optional[str] = None,
    max_price: Optional[int] = None,
    min_price: Optional[int] = None,
    style: Optional[str] = None,
    occasion: Optional[str] = None,
    size: Optional[str] = None,
    query: Optional[str] = None,
    limit: int = 20
) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    
    sql = "SELECT * FROM products WHERE 1=1"
    params = []
    
    if category_name:
        sql += " AND (category_name LIKE ? OR name LIKE ?)"
        params.extend([f"%{category_name}%", f"%{category_name}%"])
        
    if gender and gender.lower() != "tất cả":
        if gender.lower() in ["nam", "men"]:
            sql += " AND (gender = 'Nam' OR gender = 'Unisex')"
        elif gender.lower() in ["nữ", "nu", "women"]:
            sql += " AND (gender = 'Nữ' OR gender = 'Unisex')"
        elif gender.lower() == "unisex":
            sql += " AND gender = 'Unisex'"
            
    if color:
        sql += " AND color LIKE ?"
        params.append(f"%{color}%")
        
    if max_price is not None and max_price > 0:
        sql += " AND price <= ?"
        params.append(max_price)
        
    if min_price is not None and min_price > 0:
        sql += " AND price >= ?"
        params.append(min_price)
        
    if style:
        sql += " AND style LIKE ?"
        params.append(f"%{style}%")
        
    if occasion:
        sql += " AND occasion LIKE ?"
        params.append(f"%{occasion}%")
        
    if size:
        sql += " AND sizes_json LIKE ?"
        params.append(f"%\"{size.upper()}\"%")
        
    if query:
        sql += " AND (name LIKE ? OR description LIKE ? OR style LIKE ? OR occasion LIKE ?)"
        params.extend([f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"])
        
    sql += " ORDER BY id ASC LIMIT ?"
    params.append(limit)
    
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for row in rows:
        item = dict(row)
        item["sizes"] = json.loads(item["sizes_json"]) if item.get("sizes_json") else []
        result.append(item)
    return result

def save_chat_message(session_id: str, role: str, message: str, recommended_products: Optional[List[Dict[str, Any]]] = None):
    conn = get_connection()
    cursor = conn.cursor()
    rec_json = json.dumps(recommended_products, ensure_ascii=False) if recommended_products else None
    cursor.execute(
        "INSERT INTO chat_history (session_id, role, message, recommended_products_json) VALUES (?, ?, ?, ?)",
        (session_id, role, message, rec_json)
    )
    conn.commit()
    conn.close()

def get_chat_history(session_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM chat_history WHERE session_id = ? ORDER BY id ASC LIMIT ?",
        (session_id, limit)
    )
    rows = cursor.fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        if d.get("recommended_products_json"):
            d["recommended_products"] = json.loads(d["recommended_products_json"])
        else:
            d["recommended_products"] = []
        result.append(d)
    return result

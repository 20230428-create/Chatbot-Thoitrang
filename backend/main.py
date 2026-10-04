import os
# Trigger reload
import sys
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add backend directory to sys.path
sys.path.append(os.path.dirname(__file__))

from database import (
    init_db, ensure_database_ready, get_all_categories, get_all_products,
    get_product_by_id, filter_products, get_chat_history
)
from ai_service import process_chat_message
from stylist_engine import calculate_size_recommendation, get_outfit_recommendation
from rag_engine import rag_engine

# Initialize and ensure DB is ready with products
ensure_database_ready()

app = FastAPI(
    title="Fashion AI Chatbot Store",
    description="Hệ thống Cửa hàng Thời trang & AI Chatbot Tư vấn Đồ án BTL",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths (supports both standard Python run and PyInstaller bundle)
if getattr(sys, 'frozen', False):
    EXE_DIR = os.path.dirname(sys.executable)
    if os.path.exists(os.path.join(EXE_DIR, "static")):
        STATIC_DIR = os.path.join(EXE_DIR, "static")
    else:
        STATIC_DIR = os.path.join(getattr(sys, '_MEIPASS', ''), "static")
        
    if os.path.exists(os.path.join(EXE_DIR, "templates")):
        TEMPLATES_DIR = os.path.join(EXE_DIR, "templates")
    else:
        TEMPLATES_DIR = os.path.join(getattr(sys, '_MEIPASS', ''), "templates")
else:
    BUNDLE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    STATIC_DIR = os.path.join(BUNDLE_DIR, "static")
    TEMPLATES_DIR = os.path.join(BUNDLE_DIR, "templates")

# Mount Static Files
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Request Models
class ChatRequest(BaseModel):
    session_id: str = "guest_default"
    message: str

class SizeAdvisorRequest(BaseModel):
    height_cm: float
    weight_kg: float
    gender: str = "Nam"
    fit_pref: str = "vừa vặn"

class OutfitAdvisorRequest(BaseModel):
    occasion: Optional[str] = "Đi làm"
    gender: str = "Nam"
    style: Optional[str] = "Thanh lịch"

class LLMConfigRequest(BaseModel):
    api_key: str
    model: Optional[str] = "google/gemini-2.0-flash-001"

# --- HTML Routes ---
@app.get("/", response_class=HTMLResponse)
async def serve_home():
    index_path = os.path.join(TEMPLATES_DIR, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>Fashion Store is starting up...</h1>")

@app.get("/stylist", response_class=HTMLResponse)
async def serve_stylist_page():
    stylist_path = os.path.join(TEMPLATES_DIR, "stylist.html")
    if os.path.exists(stylist_path):
        with open(stylist_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>AI Stylist Studio is loading...</h1>")

# --- API Endpoints ---
@app.get("/api/categories")
async def api_get_categories():
    return {"categories": get_all_categories()}

@app.get("/api/products")
async def api_get_products(
    category: Optional[str] = None,
    gender: Optional[str] = None,
    color: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    style: Optional[str] = None,
    occasion: Optional[str] = None,
    size: Optional[str] = None,
    q: Optional[str] = None,
    limit: int = 24
):
    items = filter_products(
        category_name=category,
        gender=gender,
        color=color,
        min_price=min_price,
        max_price=max_price,
        style=style,
        occasion=occasion,
        size=size,
        query=q,
        limit=limit
    )
    return {
        "total": len(items),
        "products": items
    }

@app.get("/api/products/{product_id}")
async def api_get_product_detail(product_id: int):
    prod = get_product_by_id(product_id)
    if not prod:
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm")
        
    # Gợi ý phối đồ liên quan
    similar = rag_engine.search_similar(f"{prod['style']} {prod['occasion']} {prod['gender']}", top_k=4)
    similar_filtered = [p for p in similar if p["id"] != product_id][:3]
    
    return {
        "product": prod,
        "related_outfit_suggestions": similar_filtered
    }

@app.post("/api/chat")
async def api_chat(req: ChatRequest):
    try:
        if not req.message or not req.message.strip():
            raise HTTPException(status_code=400, detail="Nội dung câu hỏi không được để trống")
            
        result = process_chat_message(session_id=req.session_id, question=req.message)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        # Fallback graceful stylist response so client never receives 500 error
        prods = get_all_products()[:3]
        return {
            "reply": f"✨ Chào bạn! Stylist đã ghi nhận câu hỏi của bạn. Dưới đây là những thiết kế hot nhất hiện tại phù hợp với phong cách của bạn:",
            "recommended_products": prods,
            "quick_replies": [
                "Áo sơ mi nam công sở",
                "Cao 1m70 65kg mặc size gì?",
                "Tư vấn trang phục dự tiệc",
                "Gợi ý set đồ streetwear đi dạo phố"
            ],
            "intent": "general_chat",
            "entities": {},
            "ai_mode": "Offline AI Stylist (Safe Mode)"
        }

@app.get("/api/chat/history/{session_id}")
async def api_chat_history(session_id: str):
    history = get_chat_history(session_id, limit=30)
    return {"session_id": session_id, "messages": history}

@app.post("/api/stylist/size")
async def api_stylist_size(req: SizeAdvisorRequest):
    res = calculate_size_recommendation(
        height_cm=req.height_cm,
        weight_kg=req.weight_kg,
        gender=req.gender,
        fit_pref=req.fit_pref
    )
    # Lấy các sản phẩm có size đó
    products_with_size = filter_products(
        gender=req.gender,
        size=res["recommended_size"],
        limit=4
    )
    res["recommended_products"] = products_with_size
    return res

@app.post("/api/stylist/outfit")
async def api_stylist_outfit(req: OutfitAdvisorRequest):
    res = get_outfit_recommendation(
        occasion=req.occasion,
        gender=req.gender,
        style=req.style
    )
    return res

@app.post("/api/config/llm")
async def api_config_llm(req: LLMConfigRequest):
    import ai_service
    ai_service.OPENROUTER_API_KEY = req.api_key.strip()
    if req.model:
        ai_service.OPENROUTER_MODEL = req.model.strip()
    return {
        "status": "success",
        "message": "Đã cập nhật API Key OpenRouter!",
        "has_api_key": bool(ai_service.OPENROUTER_API_KEY)
    }

@app.get("/api/status")
async def api_status():
    import ai_service
    return {
        "status": "running",
        "database": "sqlite3",
        "products_count": len(get_all_products()),
        "has_llm_key": bool(ai_service.OPENROUTER_API_KEY),
        "ai_engine": "OpenRouter LLM + Intelligent Offline Stylist + RAG TF-IDF"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

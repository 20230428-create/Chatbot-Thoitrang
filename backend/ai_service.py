import os
import re
import json
import requests
from typing import Dict, Any, List, Optional, Tuple
from database import filter_products, get_all_products, save_chat_message
from rag_engine import rag_engine
from stylist_engine import calculate_size_recommendation, get_outfit_recommendation

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-001")

def extract_entities_from_text(text: str) -> Dict[str, Any]:
    text_lower = text.lower()
    entities: Dict[str, Any] = {
        "gender": None,
        "category": None,
        "color": None,
        "max_price": None,
        "min_price": None,
        "style": None,
        "occasion": None,
        "height_cm": None,
        "weight_kg": None,
        "fit_pref": "vừa vặn"
    }

    # 1. Giới tính
    if any(w in text_lower for w in ["nam", "đàn ông", "trai", "boy", "anh"]):
        entities["gender"] = "Nam"
    elif any(w in text_lower for w in ["nữ", "phụ nữ", "gái", "girl", "chị", "em gái"]):
        entities["gender"] = "Nữ"

    # 2. Loại trang phục
    categories_map = {
        "Áo sơ mi": ["sơ mi", "so mi", "shirt"],
        "Áo polo": ["polo"],
        "Áo thun": ["áo thun", "t-shirt", "ao thun", "áo phông"],
        "Áo len": ["áo len", "cổ lọ", "dệt kim"],
        "Quần tây": ["quần tây", "quần âu", "quan tay", "quan au"],
        "Quần jean": ["quần jean", "quần bò", "jean", "jeans"],
        "Quần kaki": ["kaki", "chinos"],
        "Quần ống rộng": ["ống rộng", "suông", "hack dáng"],
        "Váy": ["chân váy", "váy chữ a", "váy"],
        "Đầm": ["đầm", "váy dự tiệc", "đầm dạ hội", "váy xòe"],
        "Áo khoác": ["blazer", "khoác", "bomber", "vest"],
        "Giày": ["giày", "sneaker", "cao gót", "derby"]
    }
    for cat_name, keywords in categories_map.items():
        if any(kw in text_lower for kw in keywords):
            entities["category"] = cat_name
            break

    # 3. Màu sắc
    colors = ["đen", "trắng", "xanh navy", "xanh denim", "xanh", "be", "nâu", "hồng", "đỏ", "xám", "kem"]
    for c in colors:
        if c in text_lower:
            entities["color"] = c
            break

    # 4. Khoảng giá
    # Ví dụ: "dưới 500k", "dưới 500.000", "< 500000", "tầm 400k"
    price_match = re.search(r'(?:dưới|<|khoảng|tầm|tối đa)\s*(\d+)(?:\s*(?:k|nghìn|ngàn|000))?', text_lower)
    if price_match:
        val = int(price_match.group(1))
        if val < 1000:
            entities["max_price"] = val * 1000
        else:
            entities["max_price"] = val

    # 5. Dịp / Phong cách
    if any(w in text_lower for w in ["dự tiệc", "tiệc", "party", "đám cưới"]):
        entities["occasion"] = "Dự tiệc"
        entities["style"] = "Dự tiệc"
    elif any(w in text_lower for w in ["công sở", "đi làm", "phỏng vấn", "lịch sự", "văn phòng"]):
        entities["occasion"] = "Đi làm"
        entities["style"] = "Công sở"
    elif any(w in text_lower for w in ["streetwear", "đường phố", "bụi bặm", "cool", "ngầu"]):
        entities["style"] = "Streetwear"
    elif any(w in text_lower for w in ["đi chơi", "dạo phố", "cuối tuần", "cà phê"]):
        entities["occasion"] = "Dạo phố"
        entities["style"] = "Casual"
    elif any(w in text_lower for w in ["hàn quốc", "korea"]):
        entities["style"] = "Hàn Quốc"

    # 6. Chiều cao & Cân nặng (Tư vấn size)
    # Ví dụ: "1m70", "1m75", "170cm", "cao 1m68"
    height_match = re.search(r'(?:cao\s*)?(?:(\d)m(\d{1,2})|(\d{3})\s*cm)', text_lower)
    if height_match:
        if height_match.group(1) and height_match.group(2):
            m = int(height_match.group(1))
            cm_part = height_match.group(2)
            if len(cm_part) == 1:
                cm_part += "0"
            entities["height_cm"] = m * 100 + int(cm_part)
        elif height_match.group(3):
            entities["height_cm"] = int(height_match.group(3))

    # Ví dụ: "nặng 65kg", "65 kg", "65 ký"
    weight_match = re.search(r'(?:nặng\s*)?(\d{2,3})\s*(?:kg|kí|ký)', text_lower)
    if weight_match:
        entities["weight_kg"] = float(weight_match.group(1))

    if any(w in text_lower for w in ["ôm", "slim"]):
        entities["fit_pref"] = "ôm sát"
    elif any(w in text_lower for w in ["rộng", "thoải mái", "oversize"]):
        entities["fit_pref"] = "rộng rãi"

    return entities

def determine_intent(text: str, entities: Dict[str, Any]) -> str:
    text_lower = text.lower()
    
    # 1. Chào hỏi
    if re.search(r'^(xin chào|chào bạn|hello|hi|helo|alo|chào shop|hey)\b', text_lower):
        return "greeting"
        
    # 2. Tư vấn size
    if entities.get("height_cm") or entities.get("weight_kg") or any(kw in text_lower for kw in ["mặc size gì", "chọn size", "tư vấn size", "cỡ nào", "bảng size"]):
        return "ask_size"
        
    # 3. Tư vấn phối đồ (outfit / mix & match)
    if any(kw in text_lower for kw in ["phối với", "phối đồ", "mặc với", "kết hợp với", "set đồ", "outfit", "mặc gì đi", "hợp với quần gì", "hợp với áo gì"]):
        return "ask_outfit"
        
    # 4. Tư vấn màu sắc / phong cách chung
    if any(kw in text_lower for kw in ["hợp không", "có hợp với", "phong cách", "màu sắc nào", "thời trang gì"]):
        return "fashion_advice"
        
    # 5. Tìm kiếm sản phẩm
    if entities.get("category") or entities.get("color") or entities.get("max_price") or entities.get("style") or any(kw in text_lower for kw in ["tìm", "cần", "mua", "có áo", "có quần", "có váy", "sản phẩm"]):
        return "search_product"
        
    return "general_chat"

def call_openrouter_api(messages: List[Dict[str, str]], context_products: List[Dict[str, Any]]) -> Optional[str]:
    """Gọi LLM qua OpenRouter API nếu có cấu hình OPENROUTER_API_KEY"""
    if not OPENROUTER_API_KEY:
        return None
        
    # Format sản phẩm context
    prods_desc = "\n".join([
        f"- ID {p['id']}: {p['name']} | Giá: {p['price']:,}đ | Màu: {p['color']} | Phong cách: {p['style']} | Size: {', '.join(p.get('sizes', []))} | Mô tả: {p['description']}"
        for p in context_products[:6]
    ])
    
    system_prompt = (
        "Bạn là Chuyên gia Tư vấn Thời trang AI (Fashion Stylist) cao cấp và tận tâm của cửa hàng Fashion Store.\n"
        "Nhiệm vụ của bạn:\n"
        "1. Tư vấn trang phục, màu sắc, phong cách, kích cỡ (size) và cách phối đồ lịch thiệp, thời thượng cho khách hàng.\n"
        "2. ĐỀ XUẤT CÁC SẢN PHẨM PHÙ HỢP DỰA TRÊN DANH SÁCH DƯỚI ĐÂY. Tuyệt đối không tự bịa đặt sản phẩm hoặc mức giá không có thật.\n"
        "3. Trình bày sinh động bằng định dạng Markdown (gạch đầu dòng, in đậm tên và giá sản phẩm).\n"
        "4. Giữ giọng điệu ngọt ngào, tinh tế, chuyên nghiệp và truyền cảm hứng làm đẹp.\n\n"
        f"--- DANH SÁCH SẢN PHẨM KHẢ DỤNG TRONG CỬA HÀNG ---\n{prods_desc}\n---------------------------------"
    )
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "Fashion Store AI Stylist"
    }
    
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [{"role": "system", "content": system_prompt}] + messages,
        "temperature": 0.7,
        "max_tokens": 800
    }
    
    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=20)
        if res.status_code == 200:
            data = res.json()
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Lỗi gọi OpenRouter API: {e}")
        
    return None

def offline_ai_stylist_respond(
    question: str,
    intent: str,
    entities: Dict[str, Any],
    matched_products: List[Dict[str, Any]]
) -> Tuple[str, List[Dict[str, Any]], List[str]]:
    """
    Bộ não AI Stylist Offline cực kỳ thông minh:
    Tự động xử lý tư vấn size, phối đồ, tìm kiếm, tư vấn màu sắc mà không cần internet/API key.
    """
    quick_replies = [
        "Áo sơ mi nam công sở",
        "Cao 1m70 65kg mặc size gì?",
        "Tư vấn trang phục dự tiệc",
        "Đầm nữ thanh lịch dưới 500k",
        "Phong cách Streetwear cá tính"
    ]
    
    # 1. Chào hỏi
    if intent == "greeting":
        greeting_text = (
            "👋 **Xin chào bạn! Mình là AI Fashion Stylist của cửa hàng.**\n\n"
            "Mình có thể giúp bạn:\n"
            "✨ **Tìm trang phục:** Theo giới tính, màu sắc, loại áo quần và tầm giá.\n"
            "📏 **Tư vấn chọn size chuẩn:** Dựa trên chiều cao và cân nặng.\n"
            "👗 **Gợi ý phối đồ (Outfit):** Áo + Quần + Phụ kiện đi tiệc, đi làm, dạo phố.\n"
            "🎨 **Tư vấn gu thời trang:** Phối màu, phong cách công sở, streetwear hay Hàn Quốc.\n\n"
            "Hôm nay bạn đang muốn tìm trang phục cho dịp gì nè?"
        )
        return greeting_text, matched_products[:3], quick_replies

    # 2. Tư vấn Size
    if intent == "ask_size":
        h = entities.get("height_cm") or 170
        w = entities.get("weight_kg") or 65
        g = entities.get("gender") or "Nam"
        fit = entities.get("fit_pref") or "vừa vặn"
        
        size_info = calculate_size_recommendation(float(h), float(w), g, fit)
        
        # Lọc sản phẩm có size phù hợp
        rec_size = size_info["recommended_size"]
        prods_with_size = [p for p in matched_products if rec_size in p.get("sizes", [])]
        if not prods_with_size:
            prods_with_size = filter_products(gender=g, size=rec_size, limit=3)
            
        response_text = (
            f"{size_info['detail_message']}\n\n"
            f"✨ Dưới đây là những mẫu trang phục chuẩn form **Size {rec_size}** đang rất được yêu thích tại cửa hàng:"
        )
        return response_text, (prods_with_size or matched_products)[:3], [
            f"Sản phẩm Nam size {rec_size}",
            "Tư vấn phối đồ đi làm",
            "Xem áo sơ mi slim fit"
        ]

    # 3. Tư vấn Phối đồ (Outfit)
    if intent == "ask_outfit":
        occ = entities.get("occasion") or "Đi làm & Dự tiệc"
        g = entities.get("gender") or "Nam"
        style = entities.get("style") or "Thanh Lịch"
        
        try:
            outfit = get_outfit_recommendation(occ, g, style)
            items = outfit.get("items", [])
            total_price = outfit.get("total_price", 0)
            styling_tips = outfit.get("styling_tips", "")
        except Exception as e:
            items = matched_products[:3]
            total_price = sum(p.get("price", 0) for p in items)
            styling_tips = "✨ Gợi ý set đồ chuẩn gu dành cho bạn:"
        
        color_rules_tip = ""
        if "đen" in question.lower() and "jean" in question.lower():
            color_rules_tip = "💡 **Gợi ý phối màu:** Màu đen khi kết hợp cùng quần jean xanh là công thức kinh điển (Black & Blue Denim). Tạo cảm giác vừa nam tính, hiện đại lại trẻ trung không bao giờ lỗi mốt.\n\n"
        
        response_text = (
            f"{color_rules_tip}"
            f"{styling_tips}\n\n"
            f"💰 **Tổng set đồ:** **{total_price:,}đ** (Tiết kiệm trọn gói khi mua combo).\n"
            f"Bạn có thể bấm vào từng món đồ bên dưới để xem chi tiết kích cỡ nhé:"
        )
        return response_text, items, [
            "Set đồ dạo phố năng động",
            "Set đồ dự tiệc sang trọng",
            "Tư vấn size cho tôi"
        ]

    # 4. Tư vấn phong cách & Phối màu chung
    if intent == "fashion_advice":
        advice_text = (
            "🎨 **Góc tư vấn thời trang cùng Stylist:**\n\n"
            "- **Nguyên tắc phối màu chuẩn:** Áp dụng quy tắc bánh xe màu sắc và 60-30-10. Khi áo mang gam màu tối/trung tính (Đen, Trắng, Be), bạn có thể thoải mái phối cùng quần jean xanh hoặc quần âu xám/đen.\n"
            "- **Đi tiệc:** Ưu tiên chất liệu sang trọng như lụa satin, dạ tuyết, màu đen huyền bí hoặc đỏ rượu vang.\n"
            "- **Dạo phố / Cuối tuần:** Chọn phong cách Casual / Streetwear năng động với áo thun oversize, polo tổ ong kết hợp cùng sneaker trắng.\n\n"
            "Dưới đây là một số thiết kế phối đồ cực ăn ý dành cho bạn:"
        )
        return advice_text, matched_products[:3], quick_replies

    # 5. Tìm kiếm sản phẩm
    if matched_products:
        count = len(matched_products)
        response_text = (
            f"🎯 **Stylist tìm thấy {count} sản phẩm cực kỳ phù hợp với yêu cầu của bạn:**\n\n"
        )
        for i, p in enumerate(matched_products[:4], 1):
            response_text += f"{i}. **{p['name']}** - Giá: **{p['price']:,}đ** ({p['style']} - Màu {p['color']})\n"
            
        response_text += "\nBạn có thể click vào sản phẩm bên dưới để xem hình ảnh chi tiết và chọn size nha!"
        return response_text, matched_products[:4], [
            "Tư vấn size cho sản phẩm này",
            "Mẫu này phối với quần gì?",
            "Xem thêm sản phẩm cùng loại"
        ]
    else:
        # Nếu chưa tìm thấy chính xác bằng bộ lọc, dùng RAG vector search
        fallback_prods = rag_engine.search_similar(question, top_k=3)
        if fallback_prods:
            response_text = (
                "Stylist chưa tìm thấy sản phẩm trùng khớp 100% các tiêu chí khắt khe, "
                "nhưng mình đã chọn lọc được các mẫu có phong cách gần nhất với bạn nè:"
            )
            return response_text, fallback_prods, quick_replies
        else:
            all_fallback = get_all_products()[:3]
            return (
                "Rất tiếc hiện tại mình chưa có sản phẩm khớp hoàn toàn với mô tả của bạn. "
                "Bạn tham khảo qua các mẫu Best-Seller đang rất được ưa chuộng này nhé!",
                all_fallback,
                quick_replies
            )

def process_chat_message(session_id: str, question: str) -> Dict[str, Any]:
    """
    Quy trình xử lý hoàn chỉnh (Bước 5 + 6 + 7):
    Nhận câu hỏi -> Trích xuất thực thể -> Phân tích ý định -> Tìm kiếm SQL & RAG -> Sinh câu trả lời qua LLM hoặc Offline Stylist -> Lưu DB.
    """
    entities = extract_entities_from_text(question)
    intent = determine_intent(question, entities)
    
    # 1. Hybrid Search (SQL lọc chính xác + RAG Vector semantic)
    sql_matched = filter_products(
        category_name=entities.get("category"),
        gender=entities.get("gender"),
        color=entities.get("color"),
        max_price=entities.get("max_price"),
        style=entities.get("style"),
        occasion=entities.get("occasion"),
        limit=5
    )
    
    # RAG Vector Search
    rag_matched = rag_engine.search_similar(question, top_k=4)
    
    # Kết hợp kết quả (Ưu tiên SQL match nếu có, sau đó bổ sung RAG)
    matched_ids = set()
    combined_products = []
    
    for p in sql_matched:
        if p["id"] not in matched_ids:
            matched_ids.add(p["id"])
            combined_products.append(p)
            
    for p in rag_matched:
        if p["id"] not in matched_ids and len(combined_products) < 5:
            matched_ids.add(p["id"])
            combined_products.append(p)
            
    if not combined_products:
        combined_products = get_all_products()[:3]

    # 2. Sinh câu trả lời
    llm_answer = None
    if OPENROUTER_API_KEY:
        messages = [
            {"role": "user", "content": question}
        ]
        llm_answer = call_openrouter_api(messages, combined_products)
        
    if llm_answer:
        final_message = llm_answer
        mode = "OpenRouter LLM"
        quick_replies = [
            "Tư vấn size cho tôi",
            "Mẫu này phối với quần gì?",
            "Xem thêm sản phẩm khác"
        ]
    else:
        # Fallback to intelligent offline AI stylist
        final_message, combined_products, quick_replies = offline_ai_stylist_respond(
            question, intent, entities, combined_products
        )
        mode = "Offline AI Stylist (Rule + RAG)"

    # 3. Lưu lịch sử chat (an toàn, không crash nếu CSDL bận)
    try:
        save_chat_message(
            session_id=session_id,
            role="user",
            message=question
        )
        save_chat_message(
            session_id=session_id,
            role="assistant",
            message=final_message,
            recommended_products=[
                {"id": p["id"], "name": p["name"], "price": p["price"], "image": p["image"], "color": p["color"]}
                for p in combined_products
            ]
        )
    except Exception as e:
        print(f"[!] Warning saving chat history: {e}")

    return {
        "reply": final_message,
        "recommended_products": combined_products,
        "quick_replies": quick_replies,
        "intent": intent,
        "entities": entities,
        "ai_mode": mode
    }

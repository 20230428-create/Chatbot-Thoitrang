from typing import Dict, Any, List, Optional
from database import get_all_products, filter_products

def calculate_size_recommendation(height_cm: float, weight_kg: float, gender: str = "Nam", fit_pref: str = "vừa vặn") -> Dict[str, Any]:
    """
    Tính toán và tư vấn size chuẩn xác theo vóc dáng người Việt Nam.
    """
    bmi = weight_kg / ((height_cm / 100) ** 2) if height_cm > 0 else 21.0
    is_male = gender.lower() in ["nam", "men", "male"]
    
    recommended_size = "M"
    alternative_size = "L"
    explanation = ""
    
    if is_male:
        if height_cm < 162:
            if weight_kg < 55:
                recommended_size = "S"
                alternative_size = "M"
            else:
                recommended_size = "M"
                alternative_size = "L"
        elif 162 <= height_cm <= 168:
            if weight_kg < 58:
                recommended_size = "M"
                alternative_size = "S"
            elif weight_kg <= 66:
                recommended_size = "M"
                alternative_size = "L"
            else:
                recommended_size = "L"
                alternative_size = "XL"
        elif 169 <= height_cm <= 175:
            if weight_kg < 63:
                recommended_size = "M"
                alternative_size = "L"
            elif weight_kg <= 72:
                recommended_size = "L"
                alternative_size = "XL"
            else:
                recommended_size = "XL"
                alternative_size = "XXL"
        elif 176 <= height_cm <= 182:
            if weight_kg < 70:
                recommended_size = "L"
                alternative_size = "XL"
            elif weight_kg <= 80:
                recommended_size = "XL"
                alternative_size = "XXL"
            else:
                recommended_size = "XXL"
                alternative_size = "XL"
        else: # > 182 cm
            recommended_size = "XL" if weight_kg < 78 else "XXL"
            alternative_size = "XXL"
    else: # Nữ
        if height_cm < 152:
            recommended_size = "S" if weight_kg < 48 else "M"
            alternative_size = "M" if weight_kg < 48 else "L"
        elif 152 <= height_cm <= 158:
            if weight_kg < 47:
                recommended_size = "S"
                alternative_size = "M"
            elif weight_kg <= 53:
                recommended_size = "M"
                alternative_size = "L"
            else:
                recommended_size = "L"
                alternative_size = "XL"
        elif 159 <= height_cm <= 165:
            if weight_kg < 52:
                recommended_size = "M"
                alternative_size = "S"
            elif weight_kg <= 59:
                recommended_size = "M"
                alternative_size = "L"
            else:
                recommended_size = "L"
                alternative_size = "XL"
        else: # > 165 cm
            if weight_kg < 56:
                recommended_size = "M"
                alternative_size = "L"
            elif weight_kg <= 65:
                recommended_size = "L"
                alternative_size = "XL"
            else:
                recommended_size = "XL"
                alternative_size = "L"
                
    # Điều chỉnh theo sở thích form dáng
    if "ôm" in fit_pref.lower() or "slim" in fit_pref.lower():
        final_size = recommended_size
        tip = f"Vì bạn thích mặc tôn dáng ôm nhẹ (Slim-fit), size **{recommended_size}** là sự lựa chọn chuẩn từng đường kim mũi chỉ."
    elif "rộng" in fit_pref.lower() or "oversize" in fit_pref.lower():
        final_size = alternative_size
        tip = f"Vì bạn thích phong cách thoải mái / Oversize năng động, bạn nên chọn tăng 1 size lên **{alternative_size}**."
    else:
        final_size = recommended_size
        tip = f"Với form chuẩn thông thường, bạn mặc size **{recommended_size}** sẽ rất vừa vặn, thoải mái cử động."

    bmi_status = "cân đối"
    if bmi < 18.5:
        bmi_status = "hơi gầy"
    elif bmi > 24.9:
        bmi_status = "hơi đậm người"

    detail_message = (
        f"📊 **Kết quả phân tích vóc dáng:**\n"
        f"- Chiều cao: **{int(height_cm)} cm** | Cân nặng: **{int(weight_kg)} kg** (Chỉ số thể trạng: {bmi_status})\n"
        f"- Size khuyên dùng: **Size {final_size}** (Hoặc size {alternative_size} nếu muốn đổi phong cách)\n"
        f"- Lời khuyên stylist: {tip}"
    )

    return {
        "recommended_size": final_size,
        "alternative_size": alternative_size,
        "bmi": round(bmi, 1),
        "bmi_status": bmi_status,
        "detail_message": detail_message
    }

def get_outfit_recommendation(
    occasion: Optional[str] = None,
    gender: str = "Nam",
    style: Optional[str] = None,
    target_product_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Sinh gợi ý phối đồ (Outfit 3 món: Áo + Quần/Váy + Giày/Khoác)
    hài hòa về màu sắc, phong cách và mục đích sử dụng.
    """
    all_prods = get_all_products()
    gender_filter = "Nam" if gender.lower() in ["nam", "men"] else "Nữ"
    
    # Lọc sản phẩm phù hợp giới tính hoặc Unisex
    prods = [p for p in all_prods if p["gender"] in [gender_filter, "Unisex"]]
    
    top_item = None
    bottom_item = None
    accessory_or_outer = None
    
    # Phân loại
    tops = [p for p in prods if "Áo" in p["category_name"] and "Khoác" not in p["category_name"]]
    bottoms = [p for p in prods if "Quần" in p["category_name"] or "Váy" in p["category_name"]]
    outers = [p for p in prods if "Áo Khoác" in p["category_name"]]
    accessories = [p for p in prods if "Phụ Kiện" in p["category_name"] or "Giày" in p["category_name"]]
    
    # 1. Tìm kiếm theo dịp hoặc phong cách
    search_keyword = (occasion or style or "công sở").lower()
    
    # Chọn Top
    top_candidates = [p for p in tops if any(kw in (p["style"] + p["occasion"]).lower() for kw in [search_keyword, "casual", "thanh lịch"])]
    top_item = top_candidates[0] if top_candidates else (tops[0] if tops else None)
    
    # Chọn Bottom hài hòa
    bottom_candidates = [p for p in bottoms if any(kw in (p["style"] + p["occasion"]).lower() for kw in [search_keyword, "công sở", "streetwear"])]
    bottom_item = bottom_candidates[0] if bottom_candidates else (bottoms[0] if bottoms else None)
    
    # Chọn Outerwear hoặc Giày
    if "tiệc" in search_keyword or "công sở" in search_keyword:
        # Ưu tiên blazer hoặc giày da/cao gót
        match_outers = [p for p in outers if "Blazer" in p["name"]]
        accessory_or_outer = match_outers[0] if match_outers else (accessories[0] if accessories else None)
    else:
        # Ưu tiên sneaker hoặc bomber
        match_snk = [p for p in accessories if "Sneaker" in p["name"]]
        accessory_or_outer = match_snk[0] if match_snk else (outers[0] if outers else (accessories[0] if accessories else None))
        
    outfit_items = [item for item in [top_item, bottom_item, accessory_or_outer] if item is not None]
    total_price = sum(item["price"] for item in outfit_items) if outfit_items else 0
    
    top_name = top_item["name"] if top_item else "Áo phù hợp phong cách"
    top_color = top_item["color"] if top_item else "trang nhã"
    bot_name = bottom_item["name"] if bottom_item else "Quần / Chân váy tôn dáng"
    acc_name = accessory_or_outer["name"] if accessory_or_outer else "Giày / Phụ kiện thời trang"
    
    styling_tips = (
        f"✨ **Gợi ý Set Đồ Phù Hợp ({gender_filter} - Phong cách {style or occasion or 'Thời thượng'}):**\n"
        f"1. **{top_name}** - Màu {top_color} tạo điểm nhấn thanh lịch.\n"
        f"2. **{bot_name}** - Kết hợp cân bằng tỉ lệ cơ thể, tôn dáng và tiện di chuyển.\n"
        f"3. **{acc_name}** - Nâng tầm tổng thể outfit cực kỳ sang trọng và cuốn hút."
    )
    
    return {
        "outfit_title": f"Bộ Phối Chuẩn Gu: {style or occasion or 'Thanh Lịch Hiện Đại'}",
        "styling_tips": styling_tips,
        "items": outfit_items,
        "total_price": total_price
    }

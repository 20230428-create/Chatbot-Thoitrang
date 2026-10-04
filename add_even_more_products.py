import sqlite3
import json
import os
import random
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'fashion_store.db')
DIST_DB_PATH = os.path.join(BASE_DIR, 'dist', 'fashion_store.db')
IMAGES_DIR = os.path.join(BASE_DIR, 'static', 'images', 'products')

# Ensure we have a list of existing placeholder images
existing_images = [f for f in os.listdir(IMAGES_DIR) if f.startswith('prod_') and f.endswith('.jpg')]
if not existing_images:
    print("No base images found.")
    exit(1)

more_products = [
    {
        "category_id": 1, "category_name": "Áo Nam",
        "name": "Áo Khoác Denim Nam Tính Bụi Bặm",
        "description": "Áo khoác bò nam wash màu xanh bạc cực chất, phong cách đường phố cá tính.",
        "price": 450000, "original_price": 550000, "color": "Xanh Denim",
        "sizes": ["M", "L", "XL"], "gender": "Nam", "style": "Streetwear, Bụi bặm",
        "material": "Denim", "season": "Thu Đông", "occasion": "Dạo phố, Đi chơi"
    },
    {
        "category_id": 2, "category_name": "Quần Nam",
        "name": "Quần Kaki Nam Túi Hộp Safari",
        "description": "Quần kaki túi hộp hầm hố, kiểu dáng rộng rãi thoải mái cho các hoạt động dã ngoại.",
        "price": 350000, "original_price": 450000, "color": "Xanh Rêu",
        "sizes": ["30", "31", "32", "33"], "gender": "Nam", "style": "Năng động",
        "material": "Kaki Cotton", "season": "Bốn mùa", "occasion": "Đi phượt, Dã ngoại"
    },
    {
        "category_id": 3, "category_name": "Áo Nữ",
        "name": "Áo Vest Nữ Công Sở Thanh Lịch",
        "description": "Áo vest nữ dáng suông nhẹ nhàng, dễ dàng kết hợp cùng sơ mi hoặc áo thun lót trong.",
        "price": 550000, "original_price": 750000, "color": "Đen",
        "sizes": ["S", "M", "L"], "gender": "Nữ", "style": "Công sở, Thanh lịch",
        "material": "Tuyết mưa", "season": "Thu Đông", "occasion": "Đi làm, Họp hành"
    },
    {
        "category_id": 4, "category_name": "Váy & Đầm Nữ",
        "name": "Váy Hoa Nhí Dáng Xòe Điệu Đà",
        "description": "Váy hoa nhí phong cách vintage cổ điển, vô cùng nữ tính cho các buổi chiều dạo phố.",
        "price": 280000, "original_price": 380000, "color": "Vàng Cúc",
        "sizes": ["S", "M"], "gender": "Nữ", "style": "Vintage, Nữ tính",
        "material": "Voan lụa", "season": "Mùa Hè", "occasion": "Hẹn hò, Dạo phố"
    },
    {
        "category_id": 5, "category_name": "Quần Nữ",
        "name": "Quần Tây Ống Loe Nữ Hack Dáng",
        "description": "Quần tây nữ ống loe tôn vòng 3 và kéo dài đôi chân, phù hợp diện đi làm hoặc đi tiệc.",
        "price": 320000, "original_price": 420000, "color": "Đen",
        "sizes": ["S", "M", "L"], "gender": "Nữ", "style": "Quyến rũ, Công sở",
        "material": "Thun pha cotton", "season": "Bốn mùa", "occasion": "Đi làm, Dự tiệc"
    },
    {
        "category_id": 6, "category_name": "Áo Khoác & Blazer",
        "name": "Áo Măng Tô Kaki Dáng Dài Nam Nữ",
        "description": "Áo măng tô phong cách Hàn Quốc, form rộng unisex dễ mặc cho cả nam và nữ.",
        "price": 850000, "original_price": 1050000, "color": "Be",
        "sizes": ["M", "L", "XL"], "gender": "Unisex", "style": "Hàn Quốc, Thanh lịch",
        "material": "Kaki cao cấp", "season": "Mùa Đông", "occasion": "Du lịch, Dạo phố"
    },
    {
        "category_id": 7, "category_name": "Phụ Kiện & Giày",
        "name": "Giày Sneaker Thể Thao Đế Cao Tôn Dáng",
        "description": "Giày sneaker thể thao phong cách chunky, độn đế 5cm êm ái.",
        "price": 550000, "original_price": 750000, "color": "Trắng Đen",
        "sizes": ["36", "37", "38", "39", "40", "41", "42"], "gender": "Unisex", "style": "Thể thao, Năng động",
        "material": "Da tổng hợp", "season": "Bốn mùa", "occasion": "Đi học, Tập thể thao"
    },
    {
        "category_id": 16, "category_name": "Đồ Lót & Đồ Mặc Nhà",
        "name": "Set Áo Quần Mặc Nhà Cotton Thấm Hút",
        "description": "Bộ quần áo mặc nhà vải cotton co giãn 4 chiều mềm mịn, thoải mái tối đa.",
        "price": 180000, "original_price": 250000, "color": "Xanh Pastel",
        "sizes": ["M", "L", "XL"], "gender": "Nữ", "style": "Mặc nhà, Dễ thương",
        "material": "Cotton 100%", "season": "Bốn mùa", "occasion": "Mặc nhà"
    },
    {
        "category_id": 15, "category_name": "Đồ Bơi & Đi Biển",
        "name": "Kính Bơi Chống Chói Chống Tia UV Cao Cấp",
        "description": "Kính bơi chuyên nghiệp bảo vệ mắt, thiết kế ôm sát không rò rỉ nước.",
        "price": 120000, "original_price": 180000, "color": "Xanh Đen",
        "sizes": ["Freesize"], "gender": "Unisex", "style": "Thể thao",
        "material": "Silicon", "season": "Bốn mùa", "occasion": "Đi bơi"
    },
    {
        "category_id": 17, "category_name": "Nước Hoa & Mỹ Phẩm",
        "name": "Kem Chống Nắng Phổ Rộng SPF 50+ PA++++",
        "description": "Bảo vệ làn da tối ưu dưới nắng gắt mà không gây bết dính. An toàn cho da nhạy cảm.",
        "price": 350000, "original_price": 450000, "color": "Trắng",
        "sizes": ["50ml"], "gender": "Unisex", "style": "Bảo vệ, Chăm sóc",
        "material": "Mỹ phẩm", "season": "Bốn mùa", "occasion": "Hàng ngày, Đi biển"
    },
    {
        "category_id": 7, "category_name": "Phụ Kiện & Giày",
        "name": "Nón Len Beanie Dệt Kim Thời Trang Giữ Ấm",
        "description": "Nón len mũ beanie trẻ trung, giữ ấm tai vào mùa đông và tạo điểm nhấn cho trang phục.",
        "price": 95000, "original_price": 150000, "color": "Xám Ghi",
        "sizes": ["Freesize"], "gender": "Unisex", "style": "Hàn Quốc, Ấm áp",
        "material": "Len dệt kim", "season": "Mùa Đông", "occasion": "Du lịch, Đi dạo"
    },
    {
        "category_id": 1, "category_name": "Áo Nam",
        "name": "Áo Sơ Mi Nam Cổ Trụ Caro Mùa Thu",
        "description": "Sơ mi cổ trụ họa tiết caro đỏ đen nổi bật, dễ mặc khoác ngoài hoặc mặc trơn.",
        "price": 270000, "original_price": 350000, "color": "Caro Đỏ Đen",
        "sizes": ["M", "L", "XL"], "gender": "Nam", "style": "Trẻ trung, Bụi bặm",
        "material": "Flannel", "season": "Mùa Thu", "occasion": "Đi học, Dạo phố"
    }
]

def run():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Insert new products
    inserted_ids = []
    for p in more_products:
        cursor.execute(
            """
            INSERT INTO products (
                category_id, category_name, name, description, price, original_price,
                color, sizes_json, gender, style, material, season, occasion,
                image, stock, rating, reviews_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                p["category_id"], p["category_name"], p["name"], p["description"],
                p["price"], p["original_price"], p["color"], json.dumps(p["sizes"], ensure_ascii=False),
                p["gender"], p["style"], p["material"], p["season"], p["occasion"],
                "TEMP_IMAGE", p.get("stock", 50), p.get("rating", 4.8), p.get("reviews_count", 25)
            )
        )
        prod_id = cursor.lastrowid
        inserted_ids.append(prod_id)
        
        # Update image path properly
        img_name = f"prod_{prod_id}.jpg"
        img_path = f"/static/images/products/{img_name}"
        cursor.execute("UPDATE products SET image = ? WHERE id = ?", (img_path, prod_id))
        
    conn.commit()
    print(f"Inserted {len(inserted_ids)} new products.")
    
    # Now, check ALL products in DB to ensure their image file exists.
    cursor.execute("SELECT id, image FROM products")
    all_prods = cursor.fetchall()
    
    fixed_images_count = 0
    for pid, img_url in all_prods:
        img_filename = img_url.split('/')[-1]
        absolute_img_path = os.path.join(IMAGES_DIR, img_filename)
        
        if not os.path.exists(absolute_img_path):
            # Pick a random existing image
            source_img = random.choice(existing_images)
            source_path = os.path.join(IMAGES_DIR, source_img)
            
            # Copy it to the missing image name
            shutil.copy2(source_path, absolute_img_path)
            fixed_images_count += 1
            existing_images.append(img_filename) # make it available for others maybe
            
    print(f"Fixed {fixed_images_count} missing product images!")
    
    conn.close()
    
    # Copy DB to dist if dist exists
    if os.path.exists(DIST_DB_PATH):
        try:
            shutil.copy2(DB_PATH, DIST_DB_PATH)
            print("Successfully synced database to dist/")
        except Exception as e:
            print(f"Failed to sync db to dist: {e}")
            
    # Copy static images to dist/static if it exists
    dist_static_images = os.path.join(BASE_DIR, 'dist', 'static', 'images', 'products')
    if os.path.exists(dist_static_images):
        for img in os.listdir(IMAGES_DIR):
            try:
                shutil.copy2(os.path.join(IMAGES_DIR, img), os.path.join(dist_static_images, img))
            except:
                pass
        print("Synced images to dist/static/")

if __name__ == "__main__":
    run()

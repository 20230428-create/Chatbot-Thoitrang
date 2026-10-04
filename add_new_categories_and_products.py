import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fashion_store.db')

new_categories = [
    {"name": "Đồ Bơi & Đi Biển", "slug": "do-boi-di-bien", "description": "Bikini, áo tắm, quần bơi, áo choàng đi biển"},
    {"name": "Đồ Lót & Đồ Mặc Nhà", "slug": "do-lot-mac-nha", "description": "Đồ lót cao cấp, pijama, váy ngủ lụa"},
    {"name": "Nước Hoa & Mỹ Phẩm", "slug": "nuoc-hoa-my-pham", "description": "Nước hoa nam nữ, son môi, mỹ phẩm chăm sóc sắc đẹp"}
]

new_products_templates = [
    # Đồ Bơi & Đi Biển
    {
        "cat_slug": "do-boi-di-bien",
        "name": "Bikini 2 Mảnh Nữ Dây Chéo Sexy",
        "description": "Bộ bikini 2 mảnh chất liệu thun lạnh co giãn, thiết kế dây đan chéo eo gợi cảm, giúp nàng nổi bật trên bãi biển.",
        "price": 320000,
        "original_price": 450000,
        "color": "Đỏ đun",
        "sizes": ["S", "M", "L"],
        "gender": "Nữ",
        "style": "Gợi cảm, Đi biển",
        "material": "Thun lạnh Spandex",
        "season": "Mùa Hè",
        "occasion": "Đi biển, Hồ bơi, Resort",
        "image": "/static/images/products/prod_61.jpg",
        "stock": 40,
        "rating": 4.8,
        "reviews_count": 65
    },
    {
        "cat_slug": "do-boi-di-bien",
        "name": "Quần Bơi Nam Dáng Trunk Họa Tiết Nhiệt Đới",
        "description": "Quần bơi nam form dáng trunk ôm vừa vặn, họa tiết lá cây nhiệt đới nổi bật, chất vải khô nhanh chóng.",
        "price": 250000,
        "original_price": 350000,
        "color": "Xanh lá họa tiết",
        "sizes": ["M", "L", "XL", "XXL"],
        "gender": "Nam",
        "style": "Năng động, Mùa hè",
        "material": "Polyester nhanh khô",
        "season": "Mùa Hè",
        "occasion": "Đi biển, Hồ bơi",
        "image": "/static/images/products/prod_62.jpg",
        "stock": 50,
        "rating": 4.7,
        "reviews_count": 42
    },
    {
        "cat_slug": "do-boi-di-bien",
        "name": "Áo Choàng Đi Biển Voan Lưới Dáng Dài",
        "description": "Áo khoác đi biển chất liệu voan lưới xuyên thấu mỏng nhẹ, thiết kế form dài tua rua quyến rũ.",
        "price": 190000,
        "original_price": 280000,
        "color": "Trắng",
        "sizes": ["Freesize"],
        "gender": "Nữ",
        "style": "Dịu dàng, Quyến rũ",
        "material": "Voan lưới",
        "season": "Mùa Hè",
        "occasion": "Đi biển, Sống ảo",
        "image": "/static/images/products/prod_63.jpg",
        "stock": 35,
        "rating": 4.9,
        "reviews_count": 81
    },
    
    # Đồ Lót & Đồ Mặc Nhà
    {
        "cat_slug": "do-lot-mac-nha",
        "name": "Bộ Đồ Lụa Pijama Dài Tay Nữ Cao Cấp",
        "description": "Đồ bộ Pijama mặc nhà dài tay chất liệu lụa tơ tằm nhân tạo siêu mềm mát, không nhăn, phối viền sang trọng.",
        "price": 450000,
        "original_price": 600000,
        "color": "Hồng phấn",
        "sizes": ["S", "M", "L", "XL"],
        "gender": "Nữ",
        "style": "Sang trọng, Mặc nhà",
        "material": "Lụa French Silk",
        "season": "Bốn mùa",
        "occasion": "Mặc nhà, Ngủ",
        "image": "/static/images/products/prod_64.jpg",
        "stock": 80,
        "rating": 4.9,
        "reviews_count": 125
    },
    {
        "cat_slug": "do-lot-mac-nha",
        "name": "Combo 3 Quần Boxer Nam Cotton Kháng Khuẩn",
        "description": "Set 3 quần sịp nam dáng boxer cạp bản to ôm sát, chất liệu cotton organic kháng khuẩn, thoáng khí và thấm hút mồ hôi.",
        "price": 290000,
        "original_price": 450000,
        "color": "Đen/Xám/Xanh",
        "sizes": ["L", "XL", "XXL", "3XL"],
        "gender": "Nam",
        "style": "Cơ bản, Tiện dụng",
        "material": "95% Cotton, 5% Spandex",
        "season": "Bốn mùa",
        "occasion": "Mặc hàng ngày",
        "image": "/static/images/products/prod_65.jpg",
        "stock": 150,
        "rating": 4.8,
        "reviews_count": 310
    },
    {
        "cat_slug": "do-lot-mac-nha",
        "name": "Váy Ngủ Lụa Hai Dây Phối Ren",
        "description": "Váy ngủ hai dây gợi cảm xẻ đùi phối ren tinh tế. Lụa bóng mượt mang lại giấc ngủ ngon và vẻ đẹp kiêu sa.",
        "price": 280000,
        "original_price": 380000,
        "color": "Đen",
        "sizes": ["S", "M", "L"],
        "gender": "Nữ",
        "style": "Gợi cảm, Quyến rũ",
        "material": "Lụa phi bóng phối ren",
        "season": "Bốn mùa",
        "occasion": "Mặc nhà, Ngủ",
        "image": "/static/images/products/prod_66.jpg",
        "stock": 60,
        "rating": 4.8,
        "reviews_count": 92
    },
    
    # Nước Hoa & Mỹ Phẩm
    {
        "cat_slug": "nuoc-hoa-my-pham",
        "name": "Nước Hoa Nữ Dior Miss Dior EDP 50ml",
        "description": "Hương nước hoa nữ kinh điển mang đậm phong cách thanh lịch Pháp. Nốt hương hoa hồng tháng năm ngọt ngào đầy mê hoặc.",
        "price": 2850000,
        "original_price": 3200000,
        "color": "Hồng nhạt",
        "sizes": ["50ml"],
        "gender": "Nữ",
        "style": "Sang trọng, Ngọt ngào",
        "material": "Nước Hoa EDP",
        "season": "Bốn mùa",
        "occasion": "Dự tiệc, Hẹn hò, Đi làm",
        "image": "/static/images/products/prod_67.jpg",
        "stock": 20,
        "rating": 5.0,
        "reviews_count": 210
    },
    {
        "cat_slug": "nuoc-hoa-my-pham",
        "name": "Nước Hoa Nam Bleu de Chanel Parfum 100ml",
        "description": "Biểu tượng của sự nam tính, lịch lãm và bí ẩn. Hương gỗ thơm nồng nàn lưu giữ cực lâu trên da phái mạnh.",
        "price": 3950000,
        "original_price": 4500000,
        "color": "Xanh đen",
        "sizes": ["100ml"],
        "gender": "Nam",
        "style": "Lịch lãm, Bí ẩn, Nam tính",
        "material": "Nước Hoa Parfum",
        "season": "Thu Đông",
        "occasion": "Gặp đối tác, Dạ tiệc",
        "image": "/static/images/products/prod_68.jpg",
        "stock": 15,
        "rating": 5.0,
        "reviews_count": 340
    },
    {
        "cat_slug": "nuoc-hoa-my-pham",
        "name": "Son Môi MAC Matte Lipstick Màu Ruby Woo",
        "description": "Thỏi son đỏ huyền thoại không thể thiếu của mọi cô gái. Chất son lì mịn màng, lâu trôi và tôn mọi tông da.",
        "price": 550000,
        "original_price": 650000,
        "color": "Đỏ Ruby",
        "sizes": ["3g"],
        "gender": "Nữ",
        "style": "Quyền lực, Trẻ trung",
        "material": "Son thỏi lì",
        "season": "Bốn mùa",
        "occasion": "Đi làm, Tiệc tùng, Hẹn hò",
        "image": "/static/images/products/prod_69.jpg",
        "stock": 100,
        "rating": 4.9,
        "reviews_count": 520
    }
]

def add_categories_and_products():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cat_slug_to_id = {}
    cat_slug_to_name = {}
    
    print("Inserting new categories...")
    for cat in new_categories:
        # Check if category already exists
        cursor.execute("SELECT id, name FROM categories WHERE slug = ?", (cat["slug"],))
        row = cursor.fetchone()
        if row:
            cat_slug_to_id[cat["slug"]] = row[0]
            cat_slug_to_name[cat["slug"]] = row[1]
            print(f"Category '{cat['name']}' already exists.")
        else:
            cursor.execute(
                "INSERT INTO categories (name, slug, description) VALUES (?, ?, ?)",
                (cat["name"], cat["slug"], cat["description"])
            )
            cat_id = cursor.lastrowid
            cat_slug_to_id[cat["slug"]] = cat_id
            cat_slug_to_name[cat["slug"]] = cat["name"]
            print(f"Inserted category '{cat['name']}' with ID {cat_id}.")
            
    print("\nInserting new products for the new categories...")
    count = 0
    for p in new_products_templates:
        cat_id = cat_slug_to_id[p["cat_slug"]]
        cat_name = cat_slug_to_name[p["cat_slug"]]
        
        cursor.execute(
            """
            INSERT INTO products (
                category_id, category_name, name, description, price, original_price,
                color, sizes_json, gender, style, material, season, occasion,
                image, stock, rating, reviews_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                cat_id, cat_name, p["name"], p["description"],
                p["price"], p["original_price"], p["color"], json.dumps(p["sizes"], ensure_ascii=False),
                p["gender"], p["style"], p["material"], p["season"], p["occasion"],
                p["image"], p["stock"], p["rating"], p["reviews_count"]
            )
        )
        count += 1
        
    conn.commit()
    print(f"Successfully added {count} new products into the new categories!")
    conn.close()

if __name__ == "__main__":
    add_categories_and_products()

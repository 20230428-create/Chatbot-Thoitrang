import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fashion_store.db')

new_products = [
    {
        "category_id": 1,
        "category_name": "Áo Nam",
        "name": "Áo Thun Polo Thể Thao Nam Siêu Nhẹ",
        "description": "Áo thun thể thao siêu nhẹ, chất liệu spandex co giãn 4 chiều, thấm hút cực tốt. Dành cho các hoạt động thể thao ngoài trời hoặc đi dạo.",
        "price": 259000,
        "original_price": 350000,
        "color": "Đen",
        "sizes": ["M", "L", "XL", "XXL"],
        "gender": "Nam",
        "style": "Thể thao, Năng động",
        "material": "Spandex/Polyester",
        "season": "Xuân Hè",
        "occasion": "Chơi thể thao, Tập gym, Dạo phố",
        "image": "/static/images/products/prod_51.jpg",
        "stock": 50,
        "rating": 4.8,
        "reviews_count": 45
    },
    {
        "category_id": 2,
        "category_name": "Quần Nam",
        "name": "Quần Short Thể Thao Nam Túi Khóa Kéo",
        "description": "Quần đùi thể thao nam dài ngang gối, lưng chun có dây rút. Túi hai bên có khóa kéo an toàn. Mặc nhà, tập gym đều thoải mái.",
        "price": 199000,
        "original_price": 250000,
        "color": "Xám đậm",
        "sizes": ["M", "L", "XL", "XXL"],
        "gender": "Nam",
        "style": "Thể thao, Casual",
        "material": "Thun da cá",
        "season": "Mùa Hè",
        "occasion": "Tập gym, Chạy bộ, Mặc nhà",
        "image": "/static/images/products/prod_52.jpg",
        "stock": 40,
        "rating": 4.7,
        "reviews_count": 30
    },
    {
        "category_id": 3,
        "category_name": "Áo Nữ",
        "name": "Áo Thun Nữ Dài Tay Bodycon Cổ Vuông",
        "description": "Áo thun ôm body tay dài cổ vuông cổ điển tôn vòng 1 và xương quai xanh. Chất cotton borip co giãn cực tốt.",
        "price": 189000,
        "original_price": 250000,
        "color": "Trắng",
        "sizes": ["S", "M", "L"],
        "gender": "Nữ",
        "style": "Quyến rũ, Cơ bản",
        "material": "Cotton Borip",
        "season": "Thu Đông",
        "occasion": "Dạo phố, Cà phê, Hẹn hò",
        "image": "/static/images/products/prod_53.jpg",
        "stock": 60,
        "rating": 4.9,
        "reviews_count": 112
    },
    {
        "category_id": 4,
        "category_name": "Váy & Đầm Nữ",
        "name": "Chân Váy Jean Chữ A Dáng Ngắn Túi Vuông",
        "description": "Chân váy bò dáng chữ A ngắn cá tính, có 2 túi vuông to tạo điểm nhấn. Phối cùng áo thun phông rộng hoặc croptop siêu xinh.",
        "price": 229000,
        "original_price": 290000,
        "color": "Xanh nhạt",
        "sizes": ["S", "M", "L", "XL"],
        "gender": "Nữ",
        "style": "Năng động, Y2K",
        "material": "Denim",
        "season": "Bốn mùa",
        "occasion": "Đi chơi, Đi học, Dạo phố",
        "image": "/static/images/products/prod_54.jpg",
        "stock": 35,
        "rating": 4.8,
        "reviews_count": 48
    },
    {
        "category_id": 5,
        "category_name": "Quần Nữ",
        "name": "Quần Legging Nữ Tập Gym Nâng Mông",
        "description": "Legging tập gym nữ cạp cao gen bụng, đường may tôn mông quyến rũ. Chất vải thể thao chuyên dụng không lộ vùng nhạy cảm.",
        "price": 249000,
        "original_price": 320000,
        "color": "Đen",
        "sizes": ["S", "M", "L"],
        "gender": "Nữ",
        "style": "Thể thao, Gợi cảm",
        "material": "Nylon pha Spandex",
        "season": "Bốn mùa",
        "occasion": "Tập Yoga, Tập Gym, Chạy bộ",
        "image": "/static/images/products/prod_55.jpg",
        "stock": 55,
        "rating": 4.9,
        "reviews_count": 120
    },
    {
        "category_id": 6,
        "category_name": "Áo Khoác & Blazer",
        "name": "Áo Khoác Gió Nam Nữ Trượt Nước Chống Tia UV",
        "description": "Áo gió siêu nhẹ 1 lớp trượt nước tốt, chống tia UV 50+. Có túi đựng áo nhỏ gọn mang theo đi phượt tiện dụng.",
        "price": 289000,
        "original_price": 350000,
        "color": "Xanh dương",
        "sizes": ["M", "L", "XL", "XXL"],
        "gender": "Unisex",
        "style": "Năng động, Du lịch",
        "material": "Polyester trượt nước",
        "season": "Bốn mùa",
        "occasion": "Đi phượt, Chạy bộ ngoài trời, Du lịch",
        "image": "/static/images/products/prod_56.jpg",
        "stock": 100,
        "rating": 4.8,
        "reviews_count": 210
    },
    {
        "category_id": 7,
        "category_name": "Phụ Kiện & Giày",
        "name": "Balo Laptop Chống Nước Form Cứng Nam Nữ",
        "description": "Balo công sở kiểu dáng tối giản, chống nước tuyệt đối, ngăn chống sốc đựng vừa laptop 15.6 inch. Có cổng sạc USB tiện lợi.",
        "price": 450000,
        "original_price": 550000,
        "color": "Đen xám",
        "sizes": ["40x30x15cm"],
        "gender": "Unisex",
        "style": "Công sở, Tiện dụng",
        "material": "Vải Oxford trượt nước",
        "season": "Bốn mùa",
        "occasion": "Đi học, Đi làm văn phòng, Công tác",
        "image": "/static/images/products/prod_57.jpg",
        "stock": 40,
        "rating": 4.9,
        "reviews_count": 88
    },
    {
        "category_id": 1,
        "category_name": "Áo Nam",
        "name": "Áo Sơ Mi Cổ Tàu Nam Vải Đũi Mùa Hè",
        "description": "Sơ mi cổ tàu (cổ trụ) mộc mạc phong cách vintage. Vải đũi xước mềm mát thấm mồ hôi cực kỳ nhanh.",
        "price": 229000,
        "original_price": 290000,
        "color": "Be",
        "sizes": ["M", "L", "XL"],
        "gender": "Nam",
        "style": "Vintage, Casual",
        "material": "Vải đũi (Linen)",
        "season": "Xuân Hè",
        "occasion": "Đi du lịch, Đi biển, Cà phê",
        "image": "/static/images/products/prod_58.jpg",
        "stock": 60,
        "rating": 4.7,
        "reviews_count": 45
    },
    {
        "category_id": 3,
        "category_name": "Áo Nữ",
        "name": "Áo Len Cardigan Nữ Dáng Ngắn Mùa Thu",
        "description": "Áo khoác len cardigan mỏng nhẹ, khuy ngọc trai điệu đà, khoác ngoài cùng váy hai dây hoặc áo thun cho những ngày thu se lạnh.",
        "price": 269000,
        "original_price": 350000,
        "color": "Hồng nhạt",
        "sizes": ["Freesize"],
        "gender": "Nữ",
        "style": "Nữ tính, Nhẹ nhàng",
        "material": "Len dệt kim mỏng",
        "season": "Mùa Thu",
        "occasion": "Dạo phố, Cà phê, Đi học",
        "image": "/static/images/products/prod_59.jpg",
        "stock": 45,
        "rating": 4.8,
        "reviews_count": 67
    },
    {
        "category_id": 4,
        "category_name": "Váy & Đầm Nữ",
        "name": "Đầm Babydoll Bèo Nhún Che Khuyết Điểm",
        "description": "Đầm dáng babydoll rộng rãi thoải mái che nhẹm vòng hai, thiết kế bèo nhún siêu dễ thương nữ tính.",
        "price": 299000,
        "original_price": 380000,
        "color": "Vàng nhạt",
        "sizes": ["S", "M", "L"],
        "gender": "Nữ",
        "style": "Dễ thương, Năng động",
        "material": "Vải thô cotton",
        "season": "Mùa Hè",
        "occasion": "Đi du lịch, Đi chơi cuối tuần, Dạo phố",
        "image": "/static/images/products/prod_60.jpg",
        "stock": 50,
        "rating": 4.8,
        "reviews_count": 89
    }
]

def add_products():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    count = 0
    for p in new_products:
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
                p["image"], p["stock"], p["rating"], p["reviews_count"]
            )
        )
        count += 1
    
    conn.commit()
    print(f"Successfully added {count} new products to the database!")
    conn.close()

if __name__ == "__main__":
    add_products()

import sqlite3
import urllib.request
import os
import time

keyword_map = {
    51: "polo,shirt,sport,men",
    52: "shorts,sport,men",
    53: "women,longsleeve,top",
    54: "denim,skirt,women",
    55: "gym,leggings,women",
    56: "windbreaker,jacket",
    57: "laptop,backpack",
    58: "linen,shirt,men",
    59: "cardigan,women",
    60: "babydoll,dress",
    61: "bikini,sexy",
    62: "swim,trunks,men",
    63: "beach,coverup",
    64: "silk,pajamas,women",
    65: "boxer,briefs,men",
    66: "nightgown,silk",
    67: "perfume,dior",
    68: "perfume,chanel,men",
    69: "red,lipstick",
    70: "denim,jacket,men",
    71: "cargo,pants,men",
    72: "blazer,women",
    73: "floral,dress",
    74: "flared,pants,women",
    75: "trench,coat,khaki",
    76: "chunky,sneakers",
    77: "cotton,loungewear",
    78: "swimming,goggles",
    79: "sunscreen",
    80: "beanie,hat",
    81: "flannel,shirt,plaid"
}

# The latest added products might have IDs shifted if the DB wasn't exactly 50 at first.
# Wait, let's fetch by name instead of ID, or just map name to keywords directly.

name_to_keyword = {
    "Quần Short Thể Thao Nam Túi Khóa Kéo": "athletic,shorts",
    "Bikini 2 Mảnh Nữ Dây Chéo Sexy": "bikini",
    "Quần Bơi Nam Dáng Trunk Họa Tiết Nhiệt Đới": "swim,trunks",
    "Áo Choàng Đi Biển Voan Lưới Dáng Dài": "beach,coverup",
    "Bộ Đồ Lụa Pijama Dài Tay Nữ Cao Cấp": "pajamas",
    "Combo 3 Quần Boxer Nam Cotton Kháng Khuẩn": "boxer,briefs",
    "Váy Ngủ Lụa Hai Dây Phối Ren": "nightgown",
    "Nước Hoa Nữ Dior Miss Dior EDP 50ml": "perfume,bottle",
    "Nước Hoa Nam Bleu de Chanel Parfum 100ml": "cologne,bottle",
    "Son Môi MAC Matte Lipstick Màu Ruby Woo": "red,lipstick",
    "Áo Khoác Denim Nam Tính Bụi Bặm": "denim,jacket",
    "Quần Kaki Nam Túi Hộp Safari": "cargo,pants",
    "Áo Vest Nữ Công Sở Thanh Lịch": "suit,jacket",
    "Váy Hoa Nhí Dáng Xòe Điệu Đà": "dress,floral"
}

def download():
    conn = sqlite3.connect('fashion_store.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM products")
    products = cursor.fetchall()
    
    img_dir = os.path.join("static", "images", "products")
    os.makedirs(img_dir, exist_ok=True)
    
    import urllib.parse
    import json
    
    updated = 0
    for pid, name in products:
        if name in name_to_keyword:
            keywords = name_to_keyword[name]
            search_query = keywords.replace(',', ' ')
            encoded_query = urllib.parse.quote(search_query)
            wiki_url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&prop=pageimages&generator=search&gsrsearch={encoded_query}&gsrlimit=1&pithumbsize=800"
            
            img_name = f"prod_{pid}.jpg"
            img_path = os.path.join(img_dir, img_name)
            
            print(f"Downloading {img_name} for {name} ({search_query})...")
            try:
                # Query Wikipedia API for an image
                req = urllib.request.Request(wiki_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
                resp = urllib.request.urlopen(req).read()
                data = json.loads(resp)
                
                # Extract image URL
                pages = data.get('query', {}).get('pages', {})
                if not pages:
                    print(f"No image found on Wikipedia for {search_query}")
                    continue
                    
                page = list(pages.values())[0]
                img_url = page.get('thumbnail', {}).get('source')
                
                if not img_url:
                    print(f"No thumbnail found for {search_query}")
                    continue
                    
                # Download the actual image
                img_req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
                with urllib.request.urlopen(img_req) as response, open(img_path, 'wb') as out_file:
                    out_file.write(response.read())
                    
                cursor.execute("UPDATE products SET image = ? WHERE id = ?", (f"/static/images/products/{img_name}", pid))
                updated += 1
                import time
                time.sleep(2)
            except Exception as e:
                print(f"Failed to download {img_name}: {e}")
                
    conn.commit()
    conn.close()
    
    import shutil
    if os.path.exists('dist/fashion_store.db'):
        shutil.copy2('fashion_store.db', 'dist/fashion_store.db')
        
    dist_static = os.path.join('dist', 'static', 'images', 'products')
    if os.path.exists(dist_static):
        for pid, name in products:
            if name in name_to_keyword:
                img_name = f"prod_{pid}.jpg"
                src = os.path.join(img_dir, img_name)
                dst = os.path.join(dist_static, img_name)
                if os.path.exists(src):
                    shutil.copy2(src, dst)
                    
    print(f"Updated {updated} product images!")

if __name__ == "__main__":
    download()

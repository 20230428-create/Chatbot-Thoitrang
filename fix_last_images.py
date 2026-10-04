import sqlite3
import urllib.request
import urllib.parse
import json
import time
import os
import shutil

fix_list = {
    "Quần Short Thể Thao Nam Túi Khóa Kéo": "sports shorts men",
    "Nước Hoa Nữ Dior Miss Dior EDP 50ml": "perfume dior",
    "Nước Hoa Nam Bleu de Chanel Parfum 100ml": "men cologne",
    "Áo Khoác Denim Nam Tính Bụi Bặm": "denim jacket",
    "Quần Kaki Nam Túi Hộp Safari": "cargo pants",
    "Áo Vest Nữ Công Sở Thanh Lịch": "womens blazer",
    "Váy Hoa Nhí Dáng Xòe Điệu Đà": "floral dress"
}

def fix():
    conn = sqlite3.connect('fashion_store.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM products")
    products = cursor.fetchall()
    
    img_dir = os.path.join("static", "images", "products")
    
    for pid, name in products:
        if name in fix_list:
            search_query = fix_list[name]
            encoded_query = urllib.parse.quote(search_query)
            wiki_url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&prop=pageimages&generator=search&gsrsearch={encoded_query}&gsrlimit=1&pithumbsize=800"
            
            img_name = f"prod_{pid}.jpg"
            img_path = os.path.join(img_dir, img_name)
            
            print(f"Fixing {name} with query '{search_query}'...")
            try:
                req = urllib.request.Request(wiki_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
                resp = urllib.request.urlopen(req).read()
                data = json.loads(resp)
                
                pages = data.get('query', {}).get('pages', {})
                if not pages:
                    # Fallback generic query if specific one fails
                    print(f"No result for {search_query}, trying generic...")
                    fallback = "fashion"
                    wiki_url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&prop=pageimages&generator=search&gsrsearch={fallback}&gsrlimit=1&pithumbsize=800"
                    req = urllib.request.Request(wiki_url, headers={'User-Agent': 'Mozilla/5.0'})
                    resp = urllib.request.urlopen(req).read()
                    data = json.loads(resp)
                    pages = data.get('query', {}).get('pages', {})
                    
                if pages:
                    page = list(pages.values())[0]
                    img_url = page.get('thumbnail', {}).get('source')
                    if img_url:
                        img_req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
                        with urllib.request.urlopen(img_req) as response, open(img_path, 'wb') as out_file:
                            out_file.write(response.read())
                        print("Success!")
                        
                        # Copy to dist
                        dist_path = os.path.join("dist", img_path)
                        if os.path.exists(os.path.dirname(dist_path)):
                            shutil.copy2(img_path, dist_path)
            except Exception as e:
                print(f"Error: {e}")
                
            time.sleep(3) # safe delay
            
    conn.close()

if __name__ == "__main__":
    fix()

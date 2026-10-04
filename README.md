# 👔 FASHION AI STYLIST - CHATBOT TƯ VẤN THỜI TRANG THÔNG MINH
> **Đồ án / Bài tập lớn môn Trí Tuệ Nhân Tạo & Phát Triển Ứng Dụng Web**

Hệ thống được thiết kế theo kiến trúc **Chatbot-First** (Chatbot AI làm trung tâm trải nghiệm người dùng): Giao diện tương tác trò chuyện toàn diện với AI Stylist, tích hợp tủ đồ đề xuất động (Dynamic Wardrobe), máy tính đo size theo vóc dáng người Việt (BMI), và bộ máy phối đồ nguyên set (Mix & Match) tự động.

---

## 🌟 TÍNH NĂNG NỔI BẬT

### 1. 🤖 Chatbot AI Đa Phương Thức (Hybrid AI)
- **Tư vấn trang phục thông minh:** Trích xuất thực thể tự động (Giới tính, Loại áo quần, Màu sắc, Khoảng giá, Phong cách, Dịp sử dụng).
- **RAG Semantic Vector Search:** Ứng dụng mô hình vector hóa TF-IDF kết hợp Cosine Similarity để tìm sản phẩm có ngữ nghĩa tương đồng kể cả khi người dùng dùng câu hỏi tự nhiên (Ví dụ: *"Tôi muốn mặc đẹp đi chơi cuối tuần"*, *"Đồ đi phỏng vấn xin việc"*).
- **Hỗ trợ 2 chế độ hoạt động:**
  - **Chế độ OpenRouter LLM:** Tích hợp các mô hình ngôn ngữ lớn mạnh mẽ như `google/gemini-2.0-flash-001`, `meta-llama/llama-3.1-8b-instruct`.
  - **Chế độ Offline AI Stylist (Không cần API Key):** Bộ máy chuyên gia tích hợp sẵn thuật toán phân tích ý định, tư vấn size, phối đồ và tìm kiếm mà không phụ thuộc vào internet.

### 2. 📏 Tư Vấn Size Chuẩn Xác (Size Advisor Engine)
- Tính chỉ số khối cơ thể (BMI) và phân tích vóc dáng (cân đối, gầy, đậm người).
- Bảng kích thước chuẩn vóc dáng Việt Nam: Tự động điều chỉnh theo sở thích form dáng (Slim-fit tôn dáng, Regular vừa vặn, hoặc Oversize thoải mái).
- Lọc trực tiếp các sản phẩm trong cửa hàng đang còn đúng kích cỡ của khách hàng.

### 3. 👗 Tư Vấn Phối Đồ Nguyên Set (Outfit Coordination Engine)
- Thuật toán phối 3 món hài hòa: **Top (Áo) + Bottom (Quần/Chân váy) + Outerwear/Giày**.
- Tuân thủ quy tắc phối màu chuẩn stylist: Monochrome (đơn sắc), Contrast (tương phản), Earth-tones và Accent.
- Tính toán tổng giá trị set đồ và hỗ trợ thêm nguyên cây vào giỏ hàng chỉ với 1 click.

### 4. 🛍️ Cửa Hàng Thời Trang Cao Cấp (E-Commerce Storefront)
- Danh mục sản phẩm phong phú (Áo sơ mi, Polo, Quần tây, Quần jean, Đầm dạ hội, Blazer, Sneaker...).
- Bộ lọc đa chiều: Theo danh mục, giới tính (Nam / Nữ / Unisex), khoảng giá (slider), phong cách (Công sở, Streetwear, Dạ tiệc, Hàn Quốc...).
- Xem chi tiết sản phẩm, bảng chọn size, giỏ hàng và đặt hàng mô phỏng.
- Nút **"Tư vấn phối đồ món này cùng AI"** tích hợp trực tiếp trên từng thẻ sản phẩm.

---

## 🏗️ KIẾN TRÚC HỆ THỐNG

```
Người dùng
   │
   ▼
[ Giao diện Web / Chat Widget ] (HTML5, Modern CSS, Vanilla JS)
   │
   ▼
[ FastAPI Backend ] (backend/main.py)
   │
   ├── [ Bộ Phân Tích Ý Định & Thực Thể ] (NLP Entity Extraction)
   │
   ├── [ Hybrid Search ]
   │     ├── SQL Filter (SQLite3)
   │     └── RAG Vector Search (TF-IDF & Cosine Similarity)
   │
   ├── [ Stylist Engine ] (Tính Size BMI + Phối Đồ Outfit)
   │
   └── [ Sinh Phản Hồi ]
         ├── OpenRouter / Gemini LLM API (Khi có API Key)
         └── Built-in Offline Expert Stylist (Tự động fallback)
```

---

## 📁 CẤU TRÚC THƯ MỤC

```
Chatbot-Thoitrang/
├── backend/
│   ├── main.py              # FastAPI Web Server & API Endpoints
│   ├── database.py          # SQLite database schema & helper functions
│   ├── seed_data.py         # 22+ sản phẩm mẫu phong phú, ảnh chất lượng cao
│   ├── ai_service.py        # Logic xử lý câu hỏi, NLP extraction, LLM & Offline Stylist
│   ├── rag_engine.py        # RAG TF-IDF & Cosine Similarity Vector Search
│   └── stylist_engine.py    # Thuật toán tính size vóc dáng & phối đồ outfit
├── static/
│   ├── css/
│   │   ├── style.css        # Giao diện cửa hàng sang trọng, responsive
│   │   └── chat.css         # Widget chat nổi, thẻ sản phẩm trong chat
│   └── js/
│       ├── app.js           # Logic hiển thị sản phẩm, bộ lọc, giỏ hàng
│       └── chat.js          # Logic gửi tin nhắn, Markdown parser, sub-modals
├── templates/
│   ├── index.html           # Trang chủ cửa hàng & Floating AI Chatbot
│   └── stylist.html         # Studio Tư vấn Thời trang & Đo size chuyên sâu
├── run.py                   # Script khởi chạy 1-click
├── requirements.txt         # Danh sách thư viện Python
├── .env.example             # Mẫu cấu hình API Key (tùy chọn)
└── README.md                # Tài liệu hướng dẫn đồ án
```

---

## 🚀 HƯỚNG DẪN CÀI ĐẶT & CHẠY ỨNG DỤNG

### Cách 1: Chạy file .EXE PORTABLE (Dành cho máy khác, không cần cài Python!)
> 💡 **Khuyên dùng:** Bạn chỉ cần copy **DUY NHẤT 1 FILE** này sang bất kỳ máy tính Windows nào (qua Zalo, USB, UltraViewer...):
>
> 📁 **`FashionAI_Chatbot_Portable.exe`** (nằm ngay tại thư mục gốc của dự án hoặc trong thư mục `dist\`).
> ⚡ **Dung lượng siêu nhẹ đã tối ưu:** **~18 MB** (giảm hơn 80% so với bản gốc 100MB nhờ loại bỏ các thư viện cồng kềnh `scipy/scikit-learn/numpy` và thay bằng bộ Vector RAG TF-IDF thuần Python).

**Cách sử dụng trên máy khác:**
1. Copy file `FashionAI_Chatbot_Portable.exe` sang máy tính cần chạy (để ở Desktop hoặc bất kỳ đâu).
2. Nhấp đúp chuột vào `FashionAI_Chatbot_Portable.exe`.
3. Ứng dụng sẽ tự động khởi tạo dữ liệu và tự động mở trình duyệt web lên địa chỉ: [http://127.0.0.1:8000](http://127.0.0.1:8000).
4. Bạn có thể trò chuyện, đo size vóc dáng, phối đồ và xem sản phẩm ngay lập tức!
5. Để tắt ứng dụng, chỉ cần đóng cửa sổ console đen lại.

---

### Cách 2: Chạy từ mã nguồn Python (Dành cho lập trình viên / máy phát triển)

#### Bước 1: Mở Terminal tại thư mục dự án
```bash
cd c:\Users\LOQ\Desktop\Chatbot-Thoitrang
```

#### Bước 2: Cài đặt thư viện
```bash
pip install -r requirements.txt
```

#### Bước 3: Khởi chạy
```bash
python run.py
```
> Hệ thống sẽ tự động khởi tạo cơ sở dữ liệu SQLite và nạp dữ liệu mẫu ban đầu nếu chưa có!

### Bước 4: Mở trình duyệt và trải nghiệm
- **Trang chủ Cửa Hàng & Chatbot:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Studio AI Stylist & Đo Size:** [http://127.0.0.1:8000/stylist](http://127.0.0.1:8000/stylist)
- **Tài liệu API Swagger Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 💬 CÁC KỊCH BẢN TEST CHATBOT MẪU

Bạn có thể thử nghiệm nhập trực tiếp các câu hỏi sau vào Chatbot:
1. **Tìm kiếm theo tiêu chí:**
   - *"Tôi cần áo nam màu đen dưới 500k để đi dự tiệc."*
   - *"Có váy nữ nào dưới 500 nghìn không?"*
   - *"Tìm áo sơ mi trắng công sở thanh lịch."*
2. **Tư vấn size:**
   - *"Tôi cao 1m70, nặng 65kg nên mặc size gì?"*
   - *"Nữ cao 1m58 nặng 49kg mặc size gì vừa?"*
3. **Tư vấn phối đồ (Mix & Match):**
   - *"Áo sơ mi oxford phối với quần gì đẹp?"*
   - *"Tôi cần một set đồ nam lịch lãm đi đám cưới."*
   - *"Gợi ý set đồ streetwear đi dạo phố cuối tuần."*
4. **Tư vấn quy tắc màu sắc:**
   - *"Màu đen có hợp với quần jean xanh không?"*
   - *"Áo thun xám khói nên mặc với quần màu gì?"*

---

## 🎓 TỔNG KẾT BÁO CÁO ĐỒ ÁN

- **Đáp ứng đầy đủ 8 giai đoạn & 12 quy trình** trong tài liệu yêu cầu.
- **Có đầy đủ Database quan hệ**, hỗ trợ tìm kiếm SQL chính xác kết hợp Vector Search RAG.
- **Giao diện hiện đại**, chuẩn UX thời trang cao cấp với hiệu ứng chuyển động mượt mà.
- **Chạy độc lập mượt mà**, không bị phụ thuộc chết cứng vào API bên thứ 3 nhờ có bộ não Offline Stylist thông minh.

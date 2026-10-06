# Bé Vui Học 🐥

Game học tập song ngữ **Việt - Anh** cho trẻ **3-5 tuổi**. Chỉ cần một trình duyệt, không cần cài đặt, không cần mạng (sau khi tải về).

*A bilingual (Vietnamese - English) learning game for children aged 3-5. One HTML file, no build step, no dependencies.*

## Tính năng

- **5 chủ đề**, mỗi lượt chơi 5 câu: Đếm số 1-10, Màu và hình, Chữ cái tiếng Việt (có Ê, Ơ, Ô, Đ), Con vật và tiếng kêu, Xe cộ.
- **Chơi ngẫu nhiên:** trộn cả 5 chủ đề (8 câu).
- Nút to, ít chữ, có giọng đọc tiếng Việt và tiếng Anh. Chọn sai chỉ rung nhẹ và được thử lại, không bị trừ điểm.
- Một chú xe chạy trên đường đua theo tiến độ, chơi xong nhận **nhãn dán** (6 chú xe nhân vật + các con vật) để sưu tập.
- Nút cho ba mẹ: bật/tắt âm thanh, đổi "Việt + Anh" / "Chỉ Việt".
- Sao và nhãn dán được lưu trong trình duyệt (`localStorage`).

## Chạy thử trên máy

Cách 1: nhấp đúp vào `index.html`.

Cách 2 (chạy như một web server nhỏ):

```bash
python3 -m http.server 8000
# mở http://localhost:8000
```

## Đưa lên GitHub Pages (có link để bé chơi trên điện thoại)

```bash
git init
git add .
git commit -m "Bé Vui Học: first version"
git branch -M main
git remote add origin https://github.com/<tên-của-bạn>/be-vui-hoc.git
git push -u origin main
```

Sau đó vào repo trên GitHub: **Settings → Pages → Build and deployment → Source: Deploy from a branch → Branch: `main` / `(root)` → Save**. Sau khoảng 1-2 phút game có địa chỉ `https://<tên-của-bạn>.github.io/be-vui-hoc/`.

Trên điện thoại, mở link rồi chọn "Thêm vào Màn hình chính" để mở như một app.

## Thêm hoặc sửa nội dung

Toàn bộ game nằm trong `index.html`. Dữ liệu nằm ở phần `/* ---------- Data ---------- */` trong thẻ `<script>`:

| Biến | Dùng cho |
| --- | --- |
| `OBJS` | Đồ vật trong chủ đề Đếm số |
| `COLORS`, `SHAPES` | Màu sắc và hình khối |
| `WORDS`, `LN` | Từ và chữ cái đầu, cách đọc tên chữ |
| `ANIMALS` | Con vật và tiếng kêu |
| `CARS` | 6 chú xe nhân vật (tên, màu, loại xe, tiếng bấm còi) |

Thêm một dòng vào mảng tương ứng là có nội dung mới. Mỗi hàm `...Round()` tạo ra một câu hỏi, nên cũng dễ thêm chủ đề mới (khai báo thêm trong `TOPICS` và `BUILD`).

## Lưu ý

- Giọng đọc dùng Web Speech API của thiết bị. Nếu máy không có giọng tiếng Việt, hãy cài thêm trong phần cài đặt của hệ điều hành.
- Kiểu chữ "Baloo 2" tải từ Google Fonts. Khi không có mạng, game dùng kiểu chữ có sẵn của máy.
- Các chú xe (Bim, Bon, Tít, Pu, Rô, Mít) là nhân vật **thiết kế gốc**, vẽ bằng SVG ngay trong mã nguồn. Dự án không dùng hình ảnh hay nhân vật có bản quyền của bên thứ ba.

## Giấy phép

[MIT](LICENSE)

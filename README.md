# Bé Vui Học 🐥🚗

Game học tập song ngữ **Việt - Anh** cho trẻ **3-5 tuổi**, chủ đề **ô tô**. Một file HTML duy nhất, không cần cài đặt. Tối ưu cho iPhone và iPad (chạm to, không cần biết chữ).

*A bilingual (Vietnamese - English), car-themed learning game for kids aged 3-5, with glossy cartoon cars. One HTML file, no build step. Optimized for iPhone and iPad; children do not need to read.*

## Tính năng

**Hình ảnh:** các chú xe được vẽ theo phong cách hoạt hình bóng bẩy (mắt to trên kính chắn gió, đổ bóng, ánh sáng) bằng SVG, và dựng 3D bằng khối bo tròn. Giao diện có bảng gỗ, thẻ câu hỏi pastel đánh số và thành phố nền phía sau.

**3 mức độ theo tuổi** (chọn ở màn hình chính, nhớ lại lần sau):

| Mức | Tuổi | Số đáp án | Nội dung |
| --- | --- | --- | --- |
| 1 | 3 tuổi | 2 | đếm đến 5, 4 màu, 3 hình, chữ cái đơn giản, 5 câu mỗi lượt |
| 2 | 4 tuổi | 3 | đếm đến 10, 7 màu, 6 hình, thêm câu hỏi "làm gì", 6 câu mỗi lượt |
| 3 | 5 tuổi | 3 | 9 màu, 8 hình, dãy số, chữ hoa/thường, quy luật khó hơn, 8 câu mỗi lượt |

**11 chủ đề** (khoảng 45 dạng câu hỏi, mỗi câu được trộn ngẫu nhiên và không lặp trong một lượt chơi):

- **Đếm số:** đếm đồ vật và xe, "lấy cho bé N cái", tìm đúng chữ số, số tiếp theo, cộng - trừ bằng xe.
- **Xe cộ:** tên xe, màu xe, xe làm việc gì, đèn giao thông, đếm xe, phương tiện đi trên đường, nước hay trời.
- **Lái xe 3D:** lái xe trên đường, nhặt đủ số ngôi sao (đếm to khi nhặt).
- **Màu và hình:** gọi tên màu, hình, tìm màu giống nhau, tô màu cho xe, đồ vật có hình gì.
- **So sánh:** to - nhỏ, dài - ngắn, cao - thấp, nhiều - ít.
- **Giống nhau và xếp hình:** tìm bạn giống hệt, đoán bóng, xếp tiếp quy luật màu, tìm món khác biệt.
- **Chữ cái:** nhận chữ, chữ đầu của từ, chữ hoa - chữ thường.
- **Con vật:** tên con vật, tiếng kêu, con nào biết bay hoặc bơi.
- **Trái cây và rau:** tên và màu.
- **Cơ thể bé:** bộ phận cơ thể và chức năng.
- **Cảm xúc:** nhận biết cảm xúc và tình huống.
- **Chơi ngẫu nhiên:** trộn tất cả chủ đề.

**Dành cho bé chưa biết chữ:** mọi câu hỏi đều được đọc bằng giọng nói (Việt rồi Anh). Mỗi đáp án có nút loa 🔊 riêng để nghe tên trước khi chọn. Chọn sai chỉ rung nhẹ và được thử lại, không bị trừ điểm.

**Phần thưởng:** một chú xe chạy trên đường đua theo tiến độ. Chơi xong nhận 1 sticker mới trong album 189 sticker chia theo nhóm: 40 chú xe nhân vật (xe cứu thương, xe buýt, xe cẩu, xe ủi, máy cày, xe tên lửa...), 8 bạn siêu nhân vẽ riêng (Nhện Nhí, Mèo Siêu Nhân, Rô-bốt, Rồng Con...), hơn 130 sticker thú vật, biển cả, côn trùng, món ngon, phương tiện, đồ chơi, thiên nhiên, và 1 siêu xe vàng bí mật khi sưu tập đủ 10 chú xe. Chạm vào xe trong album để xem xe 3D.

## Chạy thử trên máy

Cách 1: nhấp đúp `index.html` (cần có mạng lần đầu để tải kiểu chữ và thư viện 3D).

Cách 2 (web server nhỏ):

```bash
python3 -m http.server 8000
# mở http://localhost:8000
```

## Đưa lên GitHub Pages

```bash
git init
git add .
git commit -m "Bé Vui Học: version 2"
git branch -M main
git remote add origin https://github.com/<tên-của-bạn>/be-vui-hoc.git
git push -u origin main
```

Trên GitHub: **Settings → Pages → Build and deployment → Source: Deploy from a branch → Branch: `main` / `(root)` → Save**. Sau 1-2 phút game có địa chỉ `https://<tên-của-bạn>.github.io/be-vui-hoc/`.

**Trên iPhone/iPad:** mở link bằng Safari → nút Chia sẻ → **Thêm vào Màn hình chính** để mở toàn màn hình như một app.

## Thêm hoặc sửa nội dung

Toàn bộ mã nằm trong `index.html`. Dữ liệu bài học nằm ở phần `LESSON DATA` trong thẻ `<script>`:

| Biến | Dùng cho |
| --- | --- |
| `OBJS_VEH`, `OBJS_OTHER` | đồ vật để đếm, chọn |
| `COLORS`, `SHAPES` | màu sắc và hình khối |
| `WORDS`, `LN`, `LET_POOL` | từ, chữ cái đầu, cách đọc tên chữ, chữ theo từng mức |
| `ANI`, `JOBS`, `LIGHTS` | con vật, việc của xe, đèn giao thông |
| `BODY`, `FOOD`, `EMO`, `SITS` | cơ thể, trái cây và rau, cảm xúc và tình huống |
| `CARS`, `addCar()` | 40 chú xe nhân vật (+ siêu xe vàng Kim); thêm xe mới bằng một dòng addCar |
| `HEROES`, `SECTIONS` | bạn siêu nhân và các nhóm sticker trong album |

Thêm một dòng vào mảng tương ứng là có thêm câu hỏi. Mỗi dạng câu hỏi là một hàm `...Round()` trong phần `QUESTION BUILDERS`. Bảng `POOL` quyết định chủ đề nào dùng dạng câu nào ở mỗi mức, nên bạn thêm dạng câu mới chỉ cần viết hàm rồi thêm tên vào `POOL`.

## Lưu ý

- **Giọng đọc** dùng giọng có sẵn của thiết bị (Web Speech API). iPhone/iPad cần cài giọng tiếng Việt trong **Cài đặt → Trợ năng → Nội dung đọc → Giọng nói**. Âm thanh chỉ phát sau lần chạm đầu tiên của bé.
- **Chế độ 3D** dùng thư viện [three.js](https://threejs.org) r128 tải từ cdnjs. Không có mạng thì các phần 2D vẫn chơi bình thường, riêng 3D sẽ báo chưa dùng được.
- Sao và sticker lưu trong trình duyệt của từng thiết bị (`localStorage`).
- Các chú xe (Bim, Bon, Tít, Pu, Rô, Mít, Kim) là nhân vật **thiết kế gốc**, vẽ bằng SVG và dựng 3D bằng khối đơn giản ngay trong mã nguồn. Dự án không dùng hình ảnh hay nhân vật có bản quyền của bên thứ ba.

## Giấy phép

[MIT](LICENSE)

## Học tiếng Anh / English mode

Trên màn hình chính có 3 nút ngôn ngữ (và nút ở góc trên): **Việt + Anh**, **Tiếng Việt**, **English**. Chế độ English hiển thị và đọc hoàn toàn bằng tiếng Anh (tên app là "Little Learners").

Chủ đề mới **Học tiếng Anh / English fun** (có ở cả 3 chế độ, 3 mức tuổi): đây là gì trong tiếng Anh, nghe và chọn hình, màu, chào hỏi (Hello, Thank you...), bảng chữ cái ABC, chữ đầu của từ (B is for ball), đếm bằng tiếng Anh, đánh vần chữ còn thiếu, từ trái nghĩa. Từ vựng gồm con vật, trái cây, phương tiện (cả các chú xe trong game), đồ vật, thiên nhiên, gia đình, hành động, cơ thể, cảm xúc. Thêm từ mới ở mảng `ENGX` trong `index.html`.

## Tia Chớp – nhân vật chính

**Tia Chớp** là chú xe anh hùng màu đỏ, có tia chớp vàng trên đầu (thiết kế gốc, có cả bản 2D và 3D).

- **Nhiệm vụ mỗi ngày:** Tia Chớp xuất hiện ở màn hình chính và nhờ bé làm một nhiệm vụ (đổi theo ngày, mảng `MISSIONS`). Xong nhiệm vụ bé được +3 sao.
- **Game đua xe 3D:** bé lái Tia Chớp.
- **Sticker đặc biệt:** nhận được khi hoàn thành nhiệm vụ đầu tiên.
- **Câu hỏi:** Tia Chớp xuất hiện trong "Đâu là Tia Chớp?" và câu đếm sao.

## Chủ đề mới và xe biết nói

- **Đồ vật trong nhà** (giường, ghế, bàn, cửa, tủ lạnh…), **Các phòng trong nhà**, **Trường học** (sách, bút, thước, cô giáo…) và **Nghề nghiệp** (bác sĩ, lính cứu hỏa, phi công…). Mỗi chủ đề có 1–3 dạng câu hỏi tùy độ tuổi; dữ liệu nằm ở các mảng `OBJ`, `ROOM`, `SCH`, `PRO` trong `index.html`. Từ vựng cũng được thêm vào chủ đề Học tiếng Anh.
- **Xe biết nói:** trong Album sticker, chạm vào một chú xe để xe đổi biểu cảm (emoji + chuyển động) và nói câu ngắn với bé bằng tiếng Việt và tiếng Anh. Bấm "Nói tiếp" để nghe câu khác, hoặc "Xem xe 3D". Thêm câu mới ở hàm `chatLines`.

## Giọng đọc Nam Minh, ảnh thật, icon app

- **Giọng đọc AI (Nam Minh)**: game phát file `audio/<mã>.mp3`, câu nào chưa có file thì tạm dùng giọng của máy. Danh sách câu nằm ở `tools/phrases.json` (đã tạo lại cho toàn bộ nội dung hiện tại). Mỗi lần upload `tools/phrases.json`, GitHub Action **Tạo giọng đọc AI** tự thu các câu còn thiếu và commit vào `audio/` (lần đầu với ~6.000 câu mất khoảng 30–60 phút, các lần sau chỉ thu câu mới).
- Hình trong bài học dùng emoji cỡ lớn (không dùng ảnh thật). Ảnh ô tô thật vẫn dùng được: thả ảnh vào thư mục `cars/` (xem `cars/README.md`).
- **Icon app**: `icons/apple-touch-icon.png` (iPhone/iPad: Safari → Chia sẻ → Thêm vào MH chính), `icons/icon-192.png`, `icons/icon-512.png`, `manifest.webmanifest`.
- **iPhone đời mới**: giao diện tránh tai thỏ/Dynamic Island, thanh Home và mép cong khi xoay ngang (`viewport-fit=cover` + `safe-area-inset`).
- Nút ngôn ngữ ở góc trên hiển thị: **Việt + Anh**, **Tiếng Việt**, **English**.

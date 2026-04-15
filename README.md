# 🏠 Giá đất Hoà Lạc – Thạch Thất – Quốc Oai

Web app thu thập & hiển thị giá đất nền từ **Facebook Groups** qua [Apify](https://apify.com).  
Trích xuất giá bằng regex + AI (tuỳ chọn), lưu PostgreSQL, hiển thị qua giao diện React responsive (mobile-friendly).

---

## Kiến trúc

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Frontend   │────▶│   Backend    │────▶│  PostgreSQL  │
│  React+Nginx │     │   FastAPI    │     │   16-alpine  │
│  port 3001   │     │  port 8000   │     │   (Docker)   │
└─────────────┘     └──────────────┘     └──────────────┘
```

## Cấu trúc dự án

```
├── backend/
│   ├── app/
│   │   ├── models/          # ORM + Pydantic schemas
│   │   ├── routers/         # API endpoints (scrape, data)
│   │   ├── services/        # Apify scraper, price extractor
│   │   ├── tasks/           # Pipeline logic (scrape → extract → dedup → save)
│   │   ├── config.py        # Biến môi trường
│   │   ├── database.py      # SQLAlchemy engine
│   │   └── main.py          # FastAPI app
│   ├── Dockerfile
│   ├── requirements.txt
│   └── sample_data.json
├── frontend/
│   ├── src/
│   │   ├── api/             # Service layer (scrape, data)
│   │   ├── components/      # UI components (layout, price)
│   │   ├── constants/       # Post type config
│   │   ├── hooks/           # Custom hooks (usePriceData, useIsMobile)
│   │   ├── pages/           # Page views (PriceDashboard)
│   │   ├── types/           # TypeScript interfaces
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── docker-compose.yml
├── .env
├── .env.example
└── .gitignore
```

---

## Tính năng

- **Scrape Facebook Groups** qua Apify (hỗ trợ nhóm kín với cookie)
- **Trích xuất giá** tự động bằng regex, hỗ trợ AI (OpenAI / Gemini)
- **Dedup thông minh** – chỉ insert bản ghi mới, bỏ qua trùng lặp
- **Responsive UI** – dùng tốt trên điện thoại (card view) và desktop (table view)
- **Lọc & tìm kiếm** – theo loại bài, giá, SĐT, vị trí, tác giả
- **PostgreSQL** – lưu trữ bền vững, hỗ trợ nhiều session scrape

---

## Thiết lập nhanh

### 1. Tạo file `.env`

```bash
cp .env.example .env
```

Mở `.env` và điền các giá trị:

| Biến | Bắt buộc | Mô tả |
|------|----------|-------|
| `APIFY_TOKEN` | ✅ | API token từ [Apify Console](https://console.apify.com/account/integrations) |
| `FB_COOKIE` | ✅ (nhóm kín) | Cookie Facebook – xem hướng dẫn bên dưới |
| `FB_GROUP_URLS` | ✅ | URL nhóm Facebook, phân tách bằng `,` |
| `OPENAI_API_KEY` | | Dùng GPT trích giá (tuỳ chọn) |
| `GEMINI_API_KEY` | | Dùng Gemini trích giá (tuỳ chọn) |

### 2. Lấy Facebook Cookie (cho nhóm kín)

1. Cài extension **EditThisCookie** trên Chrome.
2. Đăng nhập Facebook bằng **tài khoản phụ** (không dùng nick chính).
3. Vào `facebook.com` → mở EditThisCookie → nhấn **Export**.
4. Lưu JSON vào file `cookies_raw.json`.
5. Chạy script chuyển đổi:
   ```bash
   python convert_cookie.py cookies_raw.json
   ```
6. Copy kết quả dán vào biến `FB_COOKIE` trong `.env`.

> ⚠️ **Cảnh báo**: Dùng cookie có thể khiến Facebook khoá tài khoản. Luôn dùng tài khoản clone.

---

## Chạy với Docker 🐳

### Build & khởi động

```bash
# Build tất cả services
docker compose build

# Khởi động (DB + API + Frontend)
docker compose up -d

# Xem logs
docker compose logs -f api
```

### Truy cập

| Service | URL |
|---------|-----|
| **Frontend** (Web UI) | http://localhost:3001 |
| **API** (Backend) | http://localhost:8000 |
| **API Docs** (Swagger) | http://localhost:8000/docs |

### Sử dụng

1. Mở http://localhost:3001 trên trình duyệt (hoặc điện thoại cùng mạng LAN).
2. Nhấn **"Test sample"** để test với dữ liệu mẫu (không tốn Apify credit).
3. Nhấn **"Đồng bộ"** để scrape dữ liệu thật từ Facebook Groups.
4. Lọc theo loại bài, tìm kiếm SĐT/vị trí, xem chi tiết bài viết.

### Dừng & xoá

```bash
# Dừng containers
docker compose down

# Dừng + xoá database
docker compose down -v
```

---

## API Endpoints

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| `POST` | `/api/scrape` | Scrape từ Facebook Groups, dedup & lưu DB |
| `POST` | `/api/scrape/sample` | Test với sample data |
| `GET` | `/api/data` | Lấy dữ liệu từ DB (filter: session, post_type, ...) |
| `GET` | `/api/stats` | Thống kê tổng quan |

---

## Chi phí tham khảo

| Dịch vụ | Chi phí |
|---------|---------|
| Apify Free | $5 credit/tháng – đủ cho vài nhóm/ngày |
| OpenAI GPT-4o-mini | ~$0.15/1M input tokens |
| Gemini Flash | Miễn phí tier cơ bản – đủ cho vài nhóm/ngày |
| OpenAI GPT-4o-mini | ~$0.15/1M input tokens |
| Gemini Flash | Miễn phí tier cơ bản |

---

## License

MIT
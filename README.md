# ⚡ TechStore Microservice System

Hệ thống e-commerce bán điện thoại và laptop theo kiến trúc microservices.

## 📐 Kiến Trúc

```
Frontend (React, port 3000)
        │
        ▼
API Gateway (Django, port 8000)
        │
        ├──► customer-service (port 8001) ── MySQL
        ├──► staff-service    (port 8002) ── MySQL
        ├──► mobile-service   (port 8003) ── PostgreSQL
        └──► desktop-service  (port 8004) ── PostgreSQL
```

## 🚀 Khởi Động

```bash
# Build và chạy tất cả services
docker-compose up --build

# Chạy nền
docker-compose up -d --build
```

Frontend: http://localhost:3000  
API Gateway: http://localhost:8000

## 🔑 Tài Khoản Mặc Định

| Role | Email | Mật Khẩu |
|------|-------|----------|
| Admin | admin@techstore.com | Admin@123456 |
| Staff | staff01@techstore.com | Staff@123456 |

## 📦 Services

| Service | Port | Database | Mô tả |
|---------|------|----------|-------|
| `frontend` | 3000 | — | React SPA |
| `api-gateway` | 8000 | — | API routing |
| `customer-service` | 8001 | MySQL | Auth, giỏ hàng, đơn hàng |
| `staff-service` | 8002 | MySQL | Quản trị viên |
| `mobile-service` | 8003 | PostgreSQL | Sản phẩm di động |
| `desktop-service` | 8004 | PostgreSQL | Sản phẩm máy tính |

## 🔌 API Chính

```
POST /api/auth/register          Đăng ký khách hàng
POST /api/auth/login             Đăng nhập khách hàng
POST /api/auth/staff/login       Đăng nhập quản trị
GET  /api/products               Tất cả sản phẩm (tổng hợp)
GET  /api/products/mobile        Sản phẩm di động
GET  /api/products/desktop       Sản phẩm máy tính
GET  /api/cart                   Xem giỏ hàng
POST /api/cart/items             Thêm vào giỏ
POST /api/orders/checkout        Đặt hàng
GET  /api/orders                 Lịch sử đơn hàng
GET  /api/admin/orders           Tất cả đơn hàng (admin)
PUT  /api/admin/orders/{id}      Cập nhật trạng thái đơn
POST /api/admin/products/mobile  Thêm sản phẩm di động
POST /api/admin/products/desktop Thêm sản phẩm máy tính
```

## 🗄️ Databases

- **MySQL** (customer-service): customers, carts, cart_items, orders, order_items
- **MySQL** (staff-service): staff
- **PostgreSQL** (mobile-service): mobile_products
- **PostgreSQL** (desktop-service): desktop_products

## 🛠️ Phát Triển

```bash
# Dừng tất cả
docker-compose down

# Xóa volumes (reset database)
docker-compose down -v

# Xem logs
docker-compose logs -f api-gateway
docker-compose logs -f customer-service

# Seed data thủ công
docker exec mobile-service python manage.py seed_data
docker exec desktop-service python manage.py seed_data
docker exec staff-service python manage.py seed_data
```

## 📂 Cấu Trúc Project

```
techstore-microservice/
├── docker-compose.yml
├── frontend/              # React SPA
├── api-gateway/           # Django Gateway
├── customer-service/      # Django REST + MySQL
├── staff-service/         # Django REST + MySQL
├── mobile-service/        # Django REST + PostgreSQL
└── desktop-service/       # Django REST + PostgreSQL
```

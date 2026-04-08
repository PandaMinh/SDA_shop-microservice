# 🤖 MASTER PROMPT — TechStore Microservice System
## For Claude Sonnet 4 Agentic Coding

---

## 🎯 ROLE & CONTEXT

You are a **Senior Full-Stack Architect** specializing in Python microservices. Your task is to build a **complete, production-ready TechStore e-commerce microservice system** that sells phones and laptops. You must write ALL code, create ALL files, and set up the entire project autonomously from scratch.

**Study this architecture flow before starting:**
- A monolithic store is DECOMPOSED into independent services
- Each service has its OWN database (no shared DB)
- Services communicate via REST HTTP calls
- An API Gateway receives ALL frontend requests and routes to correct service
- Docker Compose orchestrates all services together

---

## 📐 SYSTEM ARCHITECTURE OVERVIEW

```
Frontend (React SPA, port 3000)
        │
        ▼
API Gateway (Django, port 8000)  ← Routes all requests
        │
        ├──► customer-service (Django REST, port 8001) ── MySQL DB (port 3306)
        ├──► staff-service    (Django REST, port 8002) ── MySQL DB (port 3307)
        ├──► mobile-service   (Django REST, port 8003) ── PostgreSQL DB (port 5432)
        └──► desktop-service  (Django REST, port 8004) ── PostgreSQL DB (port 5433)
```

### Service Responsibilities:
| Service | Database | Responsibility |
|---------|----------|---------------|
| `customer-service` | MySQL | Register, login, logout, profile, cart, orders, checkout |
| `staff-service` | MySQL | Admin login, manage products, confirm/reject orders |
| `mobile-service` | PostgreSQL | CRUD for phones/tablets product catalog |
| `desktop-service` | PostgreSQL | CRUD for laptops/PCs product catalog |
| `api-gateway` | None | Route requests, aggregate data, serve frontend |

---

## 📁 REQUIRED PROJECT STRUCTURE

```
techstore-microservice/
├── docker-compose.yml
├── README.md
│
├── frontend/                          # React SPA
│   ├── Dockerfile
│   ├── package.json
│   ├── public/
│   └── src/
│       ├── App.jsx
│       ├── index.css
│       ├── pages/
│       │   ├── HomePage.jsx           # Product listing with filter tabs
│       │   ├── ProductDetailPage.jsx  # Product detail + add to cart
│       │   ├── CartPage.jsx           # Cart management
│       │   ├── CheckoutPage.jsx       # Checkout form
│       │   ├── LoginPage.jsx          # Customer login
│       │   ├── RegisterPage.jsx       # Customer register
│       │   └── AdminPage.jsx          # Staff dashboard
│       └── components/
│           ├── Navbar.jsx
│           ├── ProductCard.jsx
│           └── ProtectedRoute.jsx
│
├── api-gateway/                       # Django Gateway
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   └── gateway/
│       ├── settings.py
│       ├── urls.py
│       └── views.py                   # All proxy/routing views
│
├── customer-service/                  # Django REST + MySQL
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   └── app/
│       ├── settings.py
│       ├── urls.py
│       ├── models.py
│       ├── serializers.py
│       └── views.py
│
├── staff-service/                     # Django REST + MySQL
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   └── app/
│       ├── settings.py
│       ├── urls.py
│       ├── models.py
│       ├── serializers.py
│       └── views.py
│
├── mobile-service/                    # Django REST + PostgreSQL
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   └── app/
│       ├── settings.py
│       ├── urls.py
│       ├── models.py
│       ├── serializers.py
│       └── views.py
│
└── desktop-service/                   # Django REST + PostgreSQL
    ├── Dockerfile
    ├── requirements.txt
    ├── manage.py
    └── app/
        ├── settings.py
        ├── urls.py
        ├── models.py
        ├── serializers.py
        └── views.py
```

---

## 🗄️ DATABASE SCHEMAS

### customer-service (MySQL — `customer_db`)
```sql
-- Customer table
CREATE TABLE customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,  -- bcrypt hashed
    phone VARCHAR(20),
    address TEXT,
    created_at DATETIME DEFAULT NOW()
);

-- Cart table (1 cart per customer)
CREATE TABLE carts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    created_at DATETIME DEFAULT NOW()
);

-- CartItem table
CREATE TABLE cart_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cart_id INT NOT NULL,
    product_id INT NOT NULL,         -- references product in mobile/desktop service
    product_type VARCHAR(10) NOT NULL, -- 'mobile' or 'desktop'
    quantity INT NOT NULL DEFAULT 1,
    price DECIMAL(12,2) NOT NULL,    -- snapshot price at time of adding
    product_name VARCHAR(255),       -- snapshot name
    product_image VARCHAR(500)       -- snapshot image URL
);

-- Order table
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    total_amount DECIMAL(12,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',  -- pending, confirmed, shipping, delivered, cancelled
    shipping_address TEXT NOT NULL,
    payment_method VARCHAR(50) DEFAULT 'cod',
    created_at DATETIME DEFAULT NOW(),
    updated_at DATETIME DEFAULT NOW() ON UPDATE NOW()
);

-- OrderItem table
CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    product_type VARCHAR(10) NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(12,2) NOT NULL
);
```

### staff-service (MySQL — `staff_db`)
```sql
-- Staff/Admin table
CREATE TABLE staff (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'staff',  -- 'admin' or 'staff'
    created_at DATETIME DEFAULT NOW()
);
```

### mobile-service (PostgreSQL — `mobile_db`)
```sql
-- Mobile products table (phones, tablets)
CREATE TABLE mobile_products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    brand VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,   -- 'phone' or 'tablet'
    price DECIMAL(12,2) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    description TEXT,
    image_url VARCHAR(500),
    specs JSONB,                     -- {screen, battery, ram, storage, camera}
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### desktop-service (PostgreSQL — `desktop_db`)
```sql
-- Desktop products table (laptops, PCs)
CREATE TABLE desktop_products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    brand VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,   -- 'laptop' or 'pc'
    price DECIMAL(12,2) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    description TEXT,
    image_url VARCHAR(500),
    specs JSONB,                     -- {cpu, ram, storage, gpu, display, battery}
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🔌 COMPLETE API SPECIFICATION

### API Gateway Routes (port 8000)
All frontend requests go to gateway. Gateway proxies to correct service.

```
# Auth
POST   /api/auth/register        → customer-service
POST   /api/auth/login           → customer-service
POST   /api/auth/logout          → customer-service
POST   /api/auth/staff/login     → staff-service

# Products (gateway aggregates mobile + desktop)
GET    /api/products             → calls BOTH mobile-service + desktop-service, merges results
GET    /api/products/mobile      → mobile-service
GET    /api/products/desktop     → desktop-service
GET    /api/products/mobile/{id} → mobile-service
GET    /api/products/desktop/{id}→ desktop-service

# Cart (customer only)
GET    /api/cart                 → customer-service (uses session customer_id)
POST   /api/cart/items           → customer-service
PUT    /api/cart/items/{id}      → customer-service
DELETE /api/cart/items/{id}      → customer-service
DELETE /api/cart/clear           → customer-service

# Orders
POST   /api/orders/checkout      → customer-service
GET    /api/orders               → customer-service (customer's orders)
GET    /api/admin/orders         → customer-service (all orders, staff only)
PUT    /api/admin/orders/{id}    → customer-service (update status)

# Admin Product Management
POST   /api/admin/products/mobile    → mobile-service
PUT    /api/admin/products/mobile/{id} → mobile-service
DELETE /api/admin/products/mobile/{id} → mobile-service
POST   /api/admin/products/desktop   → desktop-service
PUT    /api/admin/products/desktop/{id}→ desktop-service
DELETE /api/admin/products/desktop/{id}→ desktop-service
```

### customer-service internal endpoints (port 8001)
```
POST /customers/register/
POST /customers/login/
POST /customers/logout/
GET  /customers/{id}/
GET  /carts/{customer_id}/
POST /carts/
POST /cart-items/
PUT  /cart-items/{id}/
DELETE /cart-items/{id}/
POST /orders/
GET  /orders/?customer_id={id}
GET  /orders/all/
PUT  /orders/{id}/status/
```

### staff-service internal endpoints (port 8002)
```
POST /staff/login/
GET  /staff/{id}/
```

### mobile-service internal endpoints (port 8003)
```
GET    /mobile-products/
GET    /mobile-products/{id}/
POST   /mobile-products/
PUT    /mobile-products/{id}/
DELETE /mobile-products/{id}/
GET    /mobile-products/check/{id}/  # check stock for cart validation
```

### desktop-service internal endpoints (port 8004)
```
GET    /desktop-products/
GET    /desktop-products/{id}/
POST   /desktop-products/
PUT    /desktop-products/{id}/
DELETE /desktop-products/{id}/
GET    /desktop-products/check/{id}/
```

---

## 💻 IMPLEMENTATION DETAILS

### 1. Authentication (Session-based, simple)
- Use Django sessions for customer auth
- Staff auth uses a simple token stored in localStorage
- Gateway reads session/token and forwards customer_id in headers to services
- No JWT needed (keep it simple but functional)

**Customer login flow:**
```
POST /api/auth/login
  → gateway → customer-service POST /customers/login/
  → customer-service: check email/password (bcrypt)
  → return {customer_id, name, email}
  → gateway: set session['customer_id'] = id
  → frontend: store in localStorage + React state
```

### 2. Inter-Service Communication Pattern
Follow the assignment pattern — services call each other via HTTP:

```python
# In gateway views.py — proxy pattern
import requests

CUSTOMER_SERVICE = "http://customer-service:8001"
MOBILE_SERVICE = "http://mobile-service:8003"
DESKTOP_SERVICE = "http://desktop-service:8004"

def get_all_products(request):
    mobile_resp = requests.get(f"{MOBILE_SERVICE}/mobile-products/")
    desktop_resp = requests.get(f"{DESKTOP_SERVICE}/desktop-products/")
    
    mobile_products = [{"type": "mobile", **p} for p in mobile_resp.json()]
    desktop_products = [{"type": "desktop", **p} for p in desktop_resp.json()]
    
    all_products = mobile_products + desktop_products
    return JsonResponse({"products": all_products})
```

### 3. Cart Validation (Inter-service call)
When customer adds item to cart, customer-service must verify product exists:

```python
# In customer-service cart views
def add_cart_item(request):
    product_id = request.data['product_id']
    product_type = request.data['product_type']  # 'mobile' or 'desktop'
    
    if product_type == 'mobile':
        r = requests.get(f"http://mobile-service:8003/mobile-products/check/{product_id}/")
    else:
        r = requests.get(f"http://desktop-service:8004/desktop-products/check/{product_id}/")
    
    if r.status_code != 200:
        return Response({"error": "Product not found"}, status=404)
    
    product_data = r.json()
    # Save cart item with price snapshot
    ...
```

### 4. Checkout Flow
```
POST /api/orders/checkout
  → gateway receives: {shipping_address, payment_method}
  → gateway gets customer_id from session
  → gateway calls: GET /cart/{customer_id}/ from customer-service
  → gateway calls: POST /orders/ to customer-service with cart data
  → customer-service creates order + order_items
  → customer-service clears cart
  → return order confirmation
```

### 5. Password Hashing
```python
# In customer-service
from django.contrib.auth.hashers import make_password, check_password

# Register
customer.password = make_password(request.data['password'])

# Login
if check_password(request.data['password'], customer.password):
    return Response({"customer_id": customer.id, "name": customer.name})
```

---

## 🐳 DOCKER COMPOSE SPECIFICATION

```yaml
version: '3.8'

services:
  # Databases
  mysql-customer:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root123
      MYSQL_DATABASE: customer_db
    ports: ["3306:3306"]
    volumes: [customer_mysql_data:/var/lib/mysql]

  mysql-staff:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root123
      MYSQL_DATABASE: staff_db
    ports: ["3307:3306"]
    volumes: [staff_mysql_data:/var/lib/mysql]

  postgres-mobile:
    image: postgres:15
    environment:
      POSTGRES_DB: mobile_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres123
    ports: ["5432:5432"]
    volumes: [mobile_pg_data:/var/lib/postgresql/data]

  postgres-desktop:
    image: postgres:15
    environment:
      POSTGRES_DB: desktop_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres123
    ports: ["5433:5432"]
    volumes: [desktop_pg_data:/var/lib/postgresql/data]

  # Services
  customer-service:
    build: ./customer-service
    ports: ["8001:8000"]
    environment:
      DB_HOST: mysql-customer
      DB_NAME: customer_db
      DB_USER: root
      DB_PASSWORD: root123
    depends_on: [mysql-customer]

  staff-service:
    build: ./staff-service
    ports: ["8002:8000"]
    environment:
      DB_HOST: mysql-staff
      DB_NAME: staff_db
      DB_USER: root
      DB_PASSWORD: root123
    depends_on: [mysql-staff]

  mobile-service:
    build: ./mobile-service
    ports: ["8003:8000"]
    environment:
      DB_HOST: postgres-mobile
      DB_NAME: mobile_db
      DB_USER: postgres
      DB_PASSWORD: postgres123
    depends_on: [postgres-mobile]

  desktop-service:
    build: ./desktop-service
    ports: ["8004:8000"]
    environment:
      DB_HOST: postgres-desktop
      DB_NAME: desktop_db
      DB_USER: postgres
      DB_PASSWORD: postgres123
    depends_on: [postgres-desktop]

  api-gateway:
    build: ./api-gateway
    ports: ["8000:8000"]
    depends_on:
      - customer-service
      - staff-service
      - mobile-service
      - desktop-service

  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    environment:
      REACT_APP_API_URL: http://localhost:8000
    depends_on: [api-gateway]

volumes:
  customer_mysql_data:
  staff_mysql_data:
  mobile_pg_data:
  desktop_pg_data:
```

### Dockerfile template for each Django service:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    pkg-config \
    default-libmysqlclient-dev \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput 2>/dev/null || true

# Wait for DB then migrate and start
CMD sh -c "sleep 10 && python manage.py makemigrations --noinput && python manage.py migrate --noinput && python manage.py runserver 0.0.0.0:8000"
```

### requirements.txt for MySQL services (customer, staff):
```
django==4.2
djangorestframework==3.14
mysqlclient==2.2.0
requests==2.31
django-cors-headers==4.3
```

### requirements.txt for PostgreSQL services (mobile, desktop):
```
django==4.2
djangorestframework==3.14
psycopg2-binary==2.9.9
requests==2.31
django-cors-headers==4.3
```

---

## 🎨 FRONTEND DESIGN SPECIFICATION

Build a **React SPA** with a **dark, premium tech-store aesthetic**:

### Design System:
```css
:root {
  --bg-primary: #0a0a0f;          /* Near-black background */
  --bg-secondary: #111118;         /* Card background */
  --bg-elevated: #1a1a25;          /* Elevated components */
  --accent-primary: #6366f1;       /* Indigo accent */
  --accent-secondary: #a855f7;     /* Purple accent */
  --accent-gradient: linear-gradient(135deg, #6366f1, #a855f7);
  --text-primary: #f8fafc;
  --text-secondary: #94a3b8;
  --text-muted: #475569;
  --border: rgba(99, 102, 241, 0.2);
  --success: #10b981;
  --warning: #f59e0b;
  --danger: #ef4444;
  
  /* Typography */
  --font-display: 'Space Grotesk', sans-serif;  /* Headers */
  --font-body: 'Inter', sans-serif;             /* Body */
  --font-mono: 'JetBrains Mono', monospace;     /* Specs/prices */
}
```

### Page Requirements:

#### HomePage (`/`)
- Full-width hero banner with animated gradient and tagline
- Category filter tabs: **All | Phones | Tablets | Laptops | PCs** (filter by product_type)
- Product grid: 4 columns desktop, 2 tablet, 1 mobile
- Each ProductCard shows: image, name, brand badge, price, category tag, "Add to Cart" button
- Skeleton loading state while fetching
- No products found state

#### ProductDetailPage (`/product/:type/:id`)
- Large product image left, details right
- Product name, brand, category badge
- Price in large mono font
- Specs accordion (technical specifications from JSONB)
- Stock indicator (In Stock / Low Stock / Out of Stock)
- Quantity selector + Add to Cart button
- Back button

#### CartPage (`/cart`)
- List of cart items with image, name, quantity stepper, price, remove button
- Order summary sidebar: subtotal, total
- "Proceed to Checkout" button
- Empty cart state with link to homepage

#### CheckoutPage (`/checkout`)
- Form: Full Name, Phone, Address, City
- Payment method radio: COD | Bank Transfer
- Order summary (readonly)
- "Place Order" button
- Success state after order placed

#### LoginPage (`/login`)
- Email + Password form
- Link to register
- Error message display

#### RegisterPage (`/register`)
- Name, Email, Password, Phone fields
- Submit → auto login → redirect to home

#### AdminPage (`/admin`) — Staff only
- Sidebar navigation: Products | Orders
- Products tab:
  - Toggle: Mobile Products | Desktop Products
  - Table with: image, name, brand, category, price, stock, actions (edit/delete)
  - "Add Product" button → modal form
  - Edit → modal form pre-filled
  - Delete → confirmation dialog
- Orders tab:
  - Table: order ID, customer, date, total, status badge, action
  - Status dropdown to change: pending → confirmed → shipping → delivered
  - Filter by status

### React State Management (use React Context):
```javascript
// AuthContext — stores {user, isAdmin, token}
// CartContext — stores {items, total, count}
```

### API calls (axios):
```javascript
const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Use axios instance with base URL and interceptors
const api = axios.create({ baseURL: API_BASE });

// Attach auth header if logged in
api.interceptors.request.use(config => {
  const user = localStorage.getItem('user');
  if (user) {
    const parsed = JSON.parse(user);
    config.headers['X-Customer-Id'] = parsed.customer_id;
    config.headers['X-Staff-Token'] = parsed.token || '';
  }
  return config;
});
```

---

## 🌱 SEED DATA

### Create a management command in each service to seed initial data:

**mobile-service seed** (run: `python manage.py seed_data`):
```python
# 6 phones + 2 tablets with realistic specs
phones = [
    {"name": "iPhone 16 Pro", "brand": "Apple", "category": "phone", "price": 28990000,
     "stock": 50, "specs": {"screen": "6.3 inch Super Retina XDR", "ram": "8GB", 
     "storage": "256GB", "battery": "3274mAh", "camera": "48MP Triple"}},
    {"name": "Samsung Galaxy S25 Ultra", "brand": "Samsung", "category": "phone", "price": 33990000,
     "stock": 30, "specs": {"screen": "6.9 inch Dynamic AMOLED", "ram": "12GB",
     "storage": "512GB", "battery": "5000mAh", "camera": "200MP Quad"}},
    {"name": "Xiaomi 15 Ultra", "brand": "Xiaomi", "category": "phone", "price": 22990000,
     "stock": 45},
    {"name": "Google Pixel 9 Pro", "brand": "Google", "category": "phone", "price": 24990000,
     "stock": 20},
    {"name": "OPPO Find X8 Pro", "brand": "OPPO", "category": "phone", "price": 19990000,
     "stock": 35},
    {"name": "OnePlus 13", "brand": "OnePlus", "category": "phone", "price": 17990000,
     "stock": 40},
]
```

**desktop-service seed**:
```python
laptops = [
    {"name": "MacBook Pro M4 14\"", "brand": "Apple", "category": "laptop", "price": 52990000,
     "stock": 20, "specs": {"cpu": "Apple M4 Pro", "ram": "24GB", "storage": "512GB SSD",
     "gpu": "Integrated 20-core GPU", "display": "14.2\" Liquid Retina XDR", "battery": "72Wh"}},
    {"name": "Dell XPS 15", "brand": "Dell", "category": "laptop", "price": 38990000,
     "stock": 15},
    {"name": "ASUS ROG Zephyrus G16", "brand": "ASUS", "category": "laptop", "price": 45990000,
     "stock": 10},
    {"name": "ThinkPad X1 Carbon Gen 12", "brand": "Lenovo", "category": "laptop", "price": 35990000,
     "stock": 25},
    {"name": "HP Spectre x360 14", "brand": "HP", "category": "laptop", "price": 32990000,
     "stock": 18},
]
```

**staff-service seed** (create default admin):
```python
# Default admin credentials:
# email: admin@techstore.com
# password: Admin@123456
Staff.objects.create(
    username="admin",
    email="admin@techstore.com",
    password=make_password("Admin@123456"),
    role="admin"
)
```

---

## ⚙️ DJANGO SETTINGS TEMPLATE

```python
# For MySQL services (customer-service, staff-service)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'customer_db'),
        'USER': os.environ.get('DB_USER', 'root'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'root123'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        }
    }
}

# For PostgreSQL services (mobile-service, desktop-service)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'mobile_db'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'postgres123'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': '5432',
    }
}

# Common settings for all services
INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'app',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

CORS_ALLOW_ALL_ORIGINS = True  # Development only

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
}
```

---

## 🔒 CORS & GATEWAY SETTINGS

In **api-gateway settings.py**:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://frontend:3000",
]
CORS_ALLOW_CREDENTIALS = True

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_SAMESITE = 'Lax'
```

---

## 📋 CODING RULES & CONSTRAINTS

1. **NO JWT** — Use session-based auth for customers, simple token for staff
2. **NO shared databases** — Each service has its own DB as per microservice principles
3. **ALL inter-service calls** go through HTTP requests (use `requests` library)
4. **CORS enabled** on all services (development mode)
5. **Error handling** — Every API endpoint must return proper HTTP status codes
6. **Vietnamese currency** — Display prices in VND format (e.g., `28,990,000 đ`)
7. **Image URLs** — Use placeholder images from `https://via.placeholder.com/400x400?text=ProductName` if no real images
8. **Frontend** — Use functional components + hooks only (no class components)
9. **No TypeScript** — Plain JavaScript React
10. **CSS** — Use inline styles or CSS modules (no Tailwind, no Bootstrap)

---

## 🚀 EXECUTION ORDER

Build services in this exact order:
1. `mobile-service` (simplest — no inter-service deps)
2. `desktop-service` (same pattern as mobile)
3. `staff-service` (simple auth only)
4. `customer-service` (complex — cart, orders, calls mobile/desktop)
5. `api-gateway` (routes to all above)
6. `frontend` (React app)
7. `docker-compose.yml` (orchestrates everything)
8. Seed data scripts

---

## ✅ VALIDATION CHECKLIST

After building, verify:
- [ ] `docker-compose up --build` starts all 9 containers without errors
- [ ] Register customer at `POST /api/auth/register`
- [ ] Login customer at `POST /api/auth/login`
- [ ] Get all products at `GET /api/products`
- [ ] Add item to cart at `POST /api/cart/items`
- [ ] Checkout at `POST /api/orders/checkout`
- [ ] Staff login at `POST /api/auth/staff/login`
- [ ] Admin can add product via `POST /api/admin/products/mobile`
- [ ] Admin can confirm order via `PUT /api/admin/orders/{id}`
- [ ] Frontend loads at `http://localhost:3000`
- [ ] All pages render without console errors

---

## 📌 IMPORTANT NOTES

- **Health checks**: Add `GET /health/` endpoint to each service returning `{"status": "ok", "service": "mobile-service"}`
- **Wait for DB**: Services must wait for DB to be ready before migrating (use sleep + retry)
- **Auto-migrate**: Each service Dockerfile CMD should run `makemigrations && migrate` before starting
- **Product images**: Use `https://picsum.photos/400/400?random={id}` for placeholder images
- **Vietnamese text**: UI labels should be in Vietnamese (Trang chủ, Giỏ hàng, Đăng nhập, etc.)
- **Responsive**: Frontend must work on mobile screens

---

## 💡 EXAMPLE RESPONSES TO EXPECT

### GET /api/products (gateway aggregated response)
```json
{
  "products": [
    {
      "id": 1,
      "type": "mobile",
      "name": "iPhone 16 Pro",
      "brand": "Apple",
      "category": "phone",
      "price": 28990000,
      "stock": 50,
      "image_url": "https://picsum.photos/400/400?random=1",
      "specs": {"screen": "6.3 inch", "ram": "8GB", "storage": "256GB"}
    },
    {
      "id": 1,
      "type": "desktop",
      "name": "MacBook Pro M4",
      "brand": "Apple",
      "category": "laptop",
      "price": 52990000,
      "stock": 20
    }
  ]
}
```

### POST /api/orders/checkout
Request:
```json
{
  "customer_id": 1,
  "shipping_address": "123 Nguyen Van Cu, Q5, TP.HCM",
  "payment_method": "cod"
}
```
Response:
```json
{
  "order_id": 42,
  "status": "pending",
  "total_amount": 81980000,
  "message": "Đặt hàng thành công! Mã đơn hàng: #42"
}
```

---

*Build the COMPLETE project now. Write every file. Do not skip any file. Do not use placeholder comments like "# add more code here". Every function must be fully implemented.*

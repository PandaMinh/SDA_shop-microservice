# SEQUENCE DIAGRAMS — TechStore Microservice

## 1. Đăng Ký Khách Hàng (Register)

```mermaid
sequenceDiagram
    actor User
    participant FE as Frontend (3000)
    participant GW as API Gateway (8000)
    participant CS as customer-service (8001)
    participant DB as MySQL (customer_db)

    User->>FE: Điền form đăng ký (name, email, password)
    FE->>GW: POST /api/auth/register
    GW->>CS: POST /customers/register/
    CS->>DB: INSERT INTO customers
    CS->>DB: INSERT INTO carts (auto-create cart)
    DB-->>CS: OK
    CS-->>GW: {customer_id, name, email}
    GW-->>FE: 201 Created
    FE-->>User: Auto login → Redirect trang chủ
```

---

## 2. Đăng Nhập Khách Hàng (Login)

```mermaid
sequenceDiagram
    actor User
    participant FE as Frontend (3000)
    participant GW as API Gateway (8000)
    participant CS as customer-service (8001)
    participant DB as MySQL (customer_db)

    User->>FE: Nhập email + password
    FE->>GW: POST /api/auth/login
    GW->>CS: POST /customers/login/
    CS->>DB: SELECT * FROM customers WHERE email=?
    DB-->>CS: Customer record
    CS->>CS: check_password(input, hashed)
    CS-->>GW: {customer_id, name, email}
    GW-->>FE: 200 OK
    FE->>FE: Lưu user vào localStorage
    FE-->>User: Redirect trang chủ
```

---

## 3. Đăng Nhập Quản Trị (Staff Login)

```mermaid
sequenceDiagram
    actor Admin
    participant FE as Frontend (3000)
    participant GW as API Gateway (8000)
    participant SS as staff-service (8002)
    participant DB as MySQL (staff_db)

    Admin->>FE: Nhập email + password (tab Quản Trị)
    FE->>GW: POST /api/auth/staff/login
    GW->>SS: POST /staff/login/
    SS->>DB: SELECT * FROM staff WHERE email=?
    DB-->>SS: Staff record
    SS->>SS: check_password + tạo token "staff_{id}_{email}"
    SS-->>GW: {staff_id, username, role, token}
    GW-->>FE: 200 OK
    FE->>FE: Lưu token vào localStorage
    FE-->>Admin: Redirect /admin dashboard
```

---

## 4. Xem Tất Cả Sản Phẩm (Get All Products)

```mermaid
sequenceDiagram
    actor User
    participant FE as Frontend (3000)
    participant GW as API Gateway (8000)
    participant MS as mobile-service (8003)
    participant DS as desktop-service (8004)
    participant PGM as PostgreSQL (mobile_db)
    participant PGD as PostgreSQL (desktop_db)

    User->>FE: Truy cập trang chủ
    FE->>GW: GET /api/products
    GW->>MS: GET /mobile-products/
    GW->>DS: GET /desktop-products/
    MS->>PGM: SELECT * FROM mobile_products WHERE is_active=TRUE
    DS->>PGD: SELECT * FROM desktop_products WHERE is_active=TRUE
    PGM-->>MS: Danh sách mobile products
    PGD-->>DS: Danh sách desktop products
    MS-->>GW: [{id, name, brand, ...}]
    DS-->>GW: [{id, name, brand, ...}]
    GW->>GW: Merge & add type field ("mobile"/"desktop")
    GW-->>FE: {products: [...mobile, ...desktop]}
    FE-->>User: Hiển thị grid sản phẩm
```

---

## 5. Xem Chi Tiết Sản Phẩm (Product Detail)

```mermaid
sequenceDiagram
    actor User
    participant FE as Frontend (3000)
    participant GW as API Gateway (8000)
    participant MS as mobile-service (8003)
    participant PG as PostgreSQL (mobile_db)

    User->>FE: Click vào sản phẩm mobile
    FE->>GW: GET /api/products/mobile/{id}
    GW->>MS: GET /mobile-products/{id}/
    MS->>PG: SELECT * FROM mobile_products WHERE id=?
    PG-->>MS: Product record (với specs JSONB)
    MS-->>GW: {id, name, price, specs, stock, ...}
    GW-->>FE: Product data
    FE-->>User: Hiển thị trang chi tiết + specs accordion
```

---

## 6. Thêm Sản Phẩm Vào Giỏ Hàng (Add to Cart)

```mermaid
sequenceDiagram
    actor User
    participant FE as Frontend (3000)
    participant GW as API Gateway (8000)
    participant CS as customer-service (8001)
    participant MS as mobile-service (8003)
    participant PG as PostgreSQL (mobile_db)
    participant DB as MySQL (customer_db)

    User->>FE: Click "Thêm vào giỏ" (gửi X-Customer-Id header)
    FE->>GW: POST /api/cart/items {product_id, product_type, quantity}
    GW->>GW: Đọc customer_id từ X-Customer-Id header
    GW->>CS: POST /cart-items/ {customer_id, product_id, ...}
    CS->>MS: GET /mobile-products/check/{product_id}/
    MS->>PG: SELECT id, name, price, stock FROM mobile_products
    PG-->>MS: Product data
    MS-->>CS: {id, name, price, stock, image_url}
    CS->>DB: INSERT INTO cart_items (price snapshot)
    DB-->>CS: CartItem created
    CS-->>GW: CartItem data
    GW-->>FE: 201 Created
    FE->>FE: Cập nhật cart count badge
    FE-->>User: Phản hồi "Đã thêm!"
```

---

## 7. Xem Giỏ Hàng (View Cart)

```mermaid
sequenceDiagram
    actor User
    participant FE as Frontend (3000)
    participant GW as API Gateway (8000)
    participant CS as customer-service (8001)
    participant DB as MySQL (customer_db)

    User->>FE: Vào trang /cart
    FE->>GW: GET /api/cart (X-Customer-Id header)
    GW->>CS: GET /carts/{customer_id}/
    CS->>DB: SELECT carts JOIN cart_items WHERE customer_id=?
    DB-->>CS: Cart + items list
    CS-->>GW: {id, customer_id, items: [...]}
    GW-->>FE: Cart data
    FE-->>User: Hiển thị danh sách sản phẩm + tổng tiền
```

---

## 8. Cập Nhật Số Lượng Giỏ Hàng (Update Cart Item)

```mermaid
sequenceDiagram
    actor User
    participant FE as Frontend (3000)
    participant GW as API Gateway (8000)
    participant CS as customer-service (8001)
    participant DB as MySQL (customer_db)

    User->>FE: Nhấn +/- số lượng
    FE->>GW: PUT /api/cart/items/{item_id} {quantity}
    GW->>CS: PUT /cart-items/{item_id}/ {quantity}
    CS->>DB: UPDATE cart_items SET quantity=? WHERE id=?
    DB-->>CS: Updated item
    CS-->>GW: CartItem data
    GW-->>FE: 200 OK
    FE->>FE: Cập nhật tổng tiền
    FE-->>User: Cart đã cập nhật
```

---

## 9. Xóa Sản Phẩm Khỏi Giỏ (Remove Cart Item)

```mermaid
sequenceDiagram
    actor User
    participant FE as Frontend (3000)
    participant GW as API Gateway (8000)
    participant CS as customer-service (8001)
    participant DB as MySQL (customer_db)

    User->>FE: Nhấn nút ✕
    FE->>GW: DELETE /api/cart/items/{item_id}/delete
    GW->>CS: DELETE /cart-items/{item_id}/delete/
    CS->>DB: DELETE FROM cart_items WHERE id=?
    DB-->>CS: OK
    CS-->>GW: {message: "Item removed"}
    GW-->>FE: 200 OK
    FE->>FE: Xóa item khỏi danh sách
    FE-->>User: Giỏ hàng cập nhật
```

---

## 10. Đặt Hàng / Checkout

```mermaid
sequenceDiagram
    actor User
    participant FE as Frontend (3000)
    participant GW as API Gateway (8000)
    participant CS as customer-service (8001)
    participant DB as MySQL (customer_db)

    User->>FE: Điền địa chỉ + chọn thanh toán → Submit
    FE->>GW: POST /api/orders/checkout {shipping_address, payment_method}
    GW->>GW: Lấy customer_id từ X-Customer-Id
    GW->>CS: POST /orders/ {customer_id, shipping_address, payment_method}
    CS->>DB: SELECT cart_items WHERE cart.customer_id=?
    DB-->>CS: Danh sách cart items
    CS->>CS: Tính total_amount
    CS->>DB: INSERT INTO orders (total, address, status='pending')
    CS->>DB: INSERT INTO order_items (từng sản phẩm)
    CS->>DB: DELETE FROM cart_items (xóa giỏ hàng)
    DB-->>CS: OK
    CS-->>GW: {order_id, status, total_amount, message}
    GW-->>FE: 201 Created
    FE-->>User: Màn hình xác nhận đơn hàng 🎉
```

---

## 11. Xem Đơn Hàng Của Tôi (Customer Orders)

```mermaid
sequenceDiagram
    actor User
    participant FE as Frontend (3000)
    participant GW as API Gateway (8000)
    participant CS as customer-service (8001)
    participant DB as MySQL (customer_db)

    User->>FE: Vào trang /orders
    FE->>GW: GET /api/orders (X-Customer-Id header)
    GW->>CS: GET /orders/customer/?customer_id={id}
    CS->>DB: SELECT orders JOIN order_items WHERE customer_id=?
    DB-->>CS: Danh sách đơn hàng + items
    CS-->>GW: [{order_id, status, total, items:[...]}]
    GW-->>FE: Orders list
    FE-->>User: Hiển thị lịch sử đơn hàng với status badge
```

---

## 12. Thêm Sản Phẩm Mới (Admin — Add Product)

```mermaid
sequenceDiagram
    actor Admin
    participant FE as Frontend (3000)
    participant GW as API Gateway (8000)
    participant SS as staff-service (8002)
    participant MS as mobile-service (8003)
    participant PG as PostgreSQL (mobile_db)

    Admin->>FE: Mở modal "Thêm Sản Phẩm" + submit form
    FE->>GW: POST /api/admin/products/mobile {name, brand, price, ...} + X-Staff-Token
    GW->>SS: GET /staff/verify/ (X-Staff-Token)
    SS-->>GW: {valid: true, role: "admin"}
    GW->>MS: POST /mobile-products/ {product data}
    MS->>PG: INSERT INTO mobile_products
    PG-->>MS: New product with id
    MS-->>GW: Product data 201
    GW-->>FE: 201 Created
    FE->>FE: Reload danh sách sản phẩm
    FE-->>Admin: Sản phẩm đã được thêm
```

---

## 13. Sửa Sản Phẩm (Admin — Edit Product)

```mermaid
sequenceDiagram
    actor Admin
    participant FE as Frontend (3000)
    participant GW as API Gateway (8000)
    participant SS as staff-service (8002)
    participant DS as desktop-service (8004)
    participant PG as PostgreSQL (desktop_db)

    Admin->>FE: Nhấn ✏️ → Sửa thông tin → Submit
    FE->>GW: PUT /api/admin/products/desktop/{id} + X-Staff-Token
    GW->>SS: GET /staff/verify/
    SS-->>GW: {valid: true}
    GW->>DS: PUT /desktop-products/{id}/ {updated fields}
    DS->>PG: UPDATE desktop_products SET ... WHERE id=?
    PG-->>DS: Updated product
    DS-->>GW: Product data 200
    GW-->>FE: 200 OK
    FE-->>Admin: Sản phẩm đã cập nhật
```

---

## 14. Xóa Sản Phẩm (Admin — Delete Product)

```mermaid
sequenceDiagram
    actor Admin
    participant FE as Frontend (3000)
    participant GW as API Gateway (8000)
    participant SS as staff-service (8002)
    participant MS as mobile-service (8003)
    participant PG as PostgreSQL (mobile_db)

    Admin->>FE: Nhấn 🗑️ → Xác nhận xóa
    FE->>GW: DELETE /api/admin/products/mobile/{id} + X-Staff-Token
    GW->>SS: GET /staff/verify/
    SS-->>GW: {valid: true}
    GW->>MS: DELETE /mobile-products/{id}/
    MS->>PG: UPDATE mobile_products SET is_active=FALSE WHERE id=?
    Note over MS,PG: Soft delete (giữ dữ liệu lịch sử)
    PG-->>MS: OK
    MS-->>GW: {message: "Product deleted"}
    GW-->>FE: 200 OK
    FE->>FE: Xóa khỏi danh sách
    FE-->>Admin: Sản phẩm đã xóa
```

---

## 15. Cập Nhật Trạng Thái Đơn Hàng (Admin — Update Order Status)

```mermaid
sequenceDiagram
    actor Admin
    participant FE as Frontend (3000)
    participant GW as API Gateway (8000)
    participant SS as staff-service (8002)
    participant CS as customer-service (8001)
    participant DB as MySQL (customer_db)

    Admin->>FE: Đổi trạng thái đơn hàng (dropdown)
    FE->>GW: PUT /api/admin/orders/{id} {status} + X-Staff-Token
    GW->>SS: GET /staff/verify/
    SS-->>GW: {valid: true}
    GW->>CS: PUT /orders/{id}/status/ {status}
    CS->>DB: UPDATE orders SET status=? WHERE id=?
    DB-->>CS: Updated order
    CS-->>GW: Order data with new status
    GW-->>FE: 200 OK
    FE->>FE: Cập nhật badge trạng thái
    FE-->>Admin: Trạng thái đã cập nhật
```

---

## 16. Xem Tất Cả Đơn Hàng (Admin — All Orders)

```mermaid
sequenceDiagram
    actor Admin
    participant FE as Frontend (3000)
    participant GW as API Gateway (8000)
    participant SS as staff-service (8002)
    participant CS as customer-service (8001)
    participant DB as MySQL (customer_db)

    Admin->>FE: Vào tab "Đơn Hàng" trong Admin
    FE->>GW: GET /api/admin/orders + X-Staff-Token
    GW->>SS: GET /staff/verify/
    SS-->>GW: {valid: true}
    GW->>CS: GET /orders/all/
    CS->>DB: SELECT * FROM orders JOIN order_items ORDER BY created_at DESC
    DB-->>CS: All orders
    CS-->>GW: [{order_id, customer_id, status, items, total}]
    GW-->>FE: Orders list
    FE-->>Admin: Bảng tất cả đơn hàng (có filter theo status)
```

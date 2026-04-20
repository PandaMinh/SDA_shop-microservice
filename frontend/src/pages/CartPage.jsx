import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import RecommendationPanel from '../components/RecommendationPanel';

const formatPrice = (price) => new Intl.NumberFormat('vi-VN').format(price) + ' đ';

export default function CartPage() {
  const { cart, total, updateItem, removeItem, clearCart } = useCart();
  const navigate = useNavigate();
  const items = cart?.items || [];

  if (items.length === 0) {
    return (
      <div className="container" style={{ padding: '80px 24px', textAlign: 'center' }}>
        <div style={{ fontSize: 72, marginBottom: 24 }}>🛒</div>
        <h2 style={{ fontFamily: 'var(--font-display)', fontSize: 26, marginBottom: 12 }}>Giỏ hàng trống</h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: 32 }}>Chưa có sản phẩm nào trong giỏ hàng của bạn.</p>
        <Link to="/">
          <button className="btn btn-primary">Mua Sắm Ngay →</button>
        </Link>
      </div>
    );
  }

  return (
    <div className="container" style={{ padding: '40px 24px' }}>
      <div className="page-header">
        <h1 className="page-title">🛒 Giỏ Hàng</h1>
        <p className="page-subtitle">{items.length} sản phẩm trong giỏ</p>
      </div>

      <RecommendationPanel
        title="Gợi ý khi bạn đang chọn giỏ hàng"
        subtitle="Các sản phẩm được xếp hạng theo hành vi add_to_cart và model_best"
        signal="add_to_cart"
        emptyMessage="Chưa có gợi ý bổ sung từ hành vi giỏ hàng."
      />

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: 32, alignItems: 'start' }}>
        {/* Items */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {items.map(item => (
            <div key={item.id} className="card" style={{ display: 'flex', gap: 16, alignItems: 'center', padding: 16 }}>
              <img
                src={item.product_image || `https://picsum.photos/80/80?random=${item.product_id}`}
                alt={item.product_name}
                style={{ width: 80, height: 80, objectFit: 'cover', borderRadius: 10, background: 'var(--bg-elevated)' }}
                onError={e => { e.target.src = `https://picsum.photos/80/80?random=${item.product_id + 10}`; }}
              />
              <div style={{ flex: 1 }}>
                <h3 style={{ fontFamily: 'var(--font-display)', fontSize: 15, fontWeight: 600, marginBottom: 4 }}>
                  {item.product_name || `Product #${item.product_id}`}
                </h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: 13 }}>
                  {item.product_type === 'mobile' ? '📱 Di Động' : '💻 Máy Tính'}
                </p>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: 16, color: 'var(--accent-primary)', fontWeight: 600, marginTop: 4 }}>
                  {formatPrice(parseFloat(item.price) * item.quantity)}
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 0, background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 8, overflow: 'hidden' }}>
                <button onClick={() => updateItem(item.id, item.quantity - 1)} style={{ width: 34, height: 34, background: 'transparent', color: 'var(--text-primary)', fontSize: 16, border: 'none', cursor: 'pointer' }}>−</button>
                <span style={{ minWidth: 36, textAlign: 'center', fontFamily: 'var(--font-mono)', fontSize: 14, fontWeight: 600 }}>{item.quantity}</span>
                <button onClick={() => updateItem(item.id, item.quantity + 1)} style={{ width: 34, height: 34, background: 'transparent', color: 'var(--text-primary)', fontSize: 16, border: 'none', cursor: 'pointer' }}>+</button>
              </div>
              <button className="btn btn-danger btn-sm" onClick={() => removeItem(item.id)}>✕</button>
            </div>
          ))}

          <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
            <button className="btn btn-secondary btn-sm" onClick={clearCart} style={{ color: 'var(--danger)' }}>
              🗑️ Xóa tất cả
            </button>
          </div>
        </div>

        {/* Summary */}
        <div className="card" style={{ position: 'sticky', top: 80 }}>
          <h2 style={{ fontFamily: 'var(--font-display)', fontSize: 18, fontWeight: 700, marginBottom: 20 }}>Tóm Tắt Đơn Hàng</h2>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12, color: 'var(--text-secondary)', fontSize: 14 }}>
            <span>Tạm tính ({items.length} sp)</span>
            <span style={{ fontFamily: 'var(--font-mono)' }}>{formatPrice(total)}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12, color: 'var(--text-secondary)', fontSize: 14 }}>
            <span>Phí vận chuyển</span>
            <span style={{ color: 'var(--success)' }}>Miễn phí</span>
          </div>
          <div style={{ height: 1, background: 'var(--border-subtle)', margin: '16px 0' }}></div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 24, fontWeight: 700 }}>
            <span>Tổng cộng</span>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 22, color: 'var(--accent-primary)' }}>{formatPrice(total)}</span>
          </div>
          <button className="btn btn-primary" style={{ width: '100%', height: 52, fontSize: 16 }} onClick={() => navigate('/checkout')}>
            Thanh Toán →
          </button>
          <Link to="/" style={{ display: 'block', textAlign: 'center', marginTop: 12, color: 'var(--text-secondary)', fontSize: 14 }}>
            ← Tiếp tục mua sắm
          </Link>
        </div>
      </div>
    </div>
  );
}

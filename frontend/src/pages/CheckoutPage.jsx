import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import { useCart } from '../context/CartContext';
import { useAuth } from '../context/AuthContext';

const formatPrice = (price) => new Intl.NumberFormat('vi-VN').format(price) + ' đ';

export default function CheckoutPage() {
  const { cart, total, fetchCart, clearCart } = useCart();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    full_name: user?.name || '',
    phone: user?.phone || '',
    address: user?.address || '',
    city: '',
    payment_method: 'cod',
  });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(null);
  const [error, setError] = useState('');

  const items = cart?.items || [];
  const handleChange = e => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async e => {
    e.preventDefault();
    if (items.length === 0) { setError('Giỏ hàng trống'); return; }
    setLoading(true);
    setError('');
    try {
      const shipping_address = `${form.full_name}, ${form.phone}, ${form.address}, ${form.city}`;
      const res = await api.post('/api/orders/checkout', {
        customer_id: user.customer_id,
        shipping_address,
        payment_method: form.payment_method,
        customer_name: form.full_name,
        customer_email: user.email,
        items: items,
      });
      setSuccess(res.data);
      if (user?.customer_id) {
        const purchaseEvents = items.map(item => api.post('/api/ai/events', {
          customer_id: user.customer_id,
          event_type: 'buy',
          product_id: item.product_id,
          product_type: item.product_type,
          product_name: item.product_name,
          metadata: { price: item.price, quantity: item.quantity },
        }).catch(() => {}));
        await Promise.all(purchaseEvents);
      }
      await clearCart();
      await fetchCart();
    } catch (err) {
      setError(err.response?.data?.error || 'Đặt hàng thất bại. Vui lòng thử lại.');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="container" style={{ padding: '80px 24px', textAlign: 'center', maxWidth: 560, margin: '0 auto' }}>
        <div style={{ fontSize: 72, marginBottom: 24, animation: 'bounceIn 0.5s ease' }}>🎉</div>
        <h2 style={{ fontFamily: 'var(--font-display)', fontSize: 28, fontWeight: 700, marginBottom: 12, background: 'var(--accent-gradient)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>
          Đặt Hàng Thành Công!
        </h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: 8, fontSize: 16 }}>{success.message}</p>
        <div style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 12, padding: 20, margin: '24px 0' }}>
          <p style={{ fontSize: 14, color: 'var(--text-secondary)' }}>Tổng thanh toán</p>
          <p style={{ fontFamily: 'var(--font-mono)', fontSize: 28, fontWeight: 700, color: 'var(--accent-primary)' }}>{formatPrice(success.total_amount)}</p>
        </div>
        <div style={{ display: 'flex', gap: 12, justifyContent: 'center' }}>
          <button className="btn btn-secondary" onClick={() => navigate('/orders')}>Xem Đơn Hàng</button>
          <button className="btn btn-primary" onClick={() => navigate('/')}>Tiếp Tục Mua Sắm</button>
        </div>
      </div>
    );
  }

  return (
    <div className="container" style={{ padding: '40px 24px' }}>
      <div className="page-header">
        <h1 className="page-title">📦 Thanh Toán</h1>
        <p className="page-subtitle">Điền thông tin giao hàng</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 360px', gap: 32, alignItems: 'start' }}>
        {/* Form */}
        <div className="card">
          {error && <div className="error-message">{error}</div>}
          <form onSubmit={handleSubmit}>
            <h3 style={{ fontFamily: 'var(--font-display)', fontSize: 16, fontWeight: 600, marginBottom: 20, color: 'var(--text-secondary)', textTransform: 'uppercase', fontSize: 12, letterSpacing: 1 }}>
              Thông Tin Người Nhận
            </h3>
            <div className="form-group">
              <label className="form-label">Họ và Tên</label>
              <input name="full_name" value={form.full_name} onChange={handleChange} required placeholder="Nguyễn Văn A" className="form-input" />
            </div>
            <div className="form-group">
              <label className="form-label">Số Điện Thoại</label>
              <input name="phone" value={form.phone} onChange={handleChange} required placeholder="0901234567" className="form-input" />
            </div>
            <div className="form-group">
              <label className="form-label">Địa Chỉ</label>
              <input name="address" value={form.address} onChange={handleChange} required placeholder="123 Đường Nguyễn Văn Cừ" className="form-input" />
            </div>
            <div className="form-group">
              <label className="form-label">Thành Phố</label>
              <input name="city" value={form.city} onChange={handleChange} required placeholder="TP. Hồ Chí Minh" className="form-input" />
            </div>

            <div style={{ height: 1, background: 'var(--border-subtle)', margin: '24px 0' }}></div>

            <h3 style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 16 }}>
              Phương Thức Thanh Toán
            </h3>
            <div style={{ display: 'flex', gap: 12, marginBottom: 24 }}>
              {[{ value: 'cod', label: '💵 Thanh toán khi nhận hàng' }, { value: 'bank', label: '🏦 Chuyển khoản ngân hàng' }].map(method => (
                <label key={method.value} style={{ flex: 1, padding: '12px 16px', background: form.payment_method === method.value ? 'rgba(79, 70, 229, 0.1)' : 'var(--bg-elevated)', border: `2px solid ${form.payment_method === method.value ? 'var(--accent-primary)' : 'var(--border-subtle)'}`, borderRadius: 10, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 10, fontSize: 14, fontWeight: 500 }}>
                  <input type="radio" name="payment_method" value={method.value} checked={form.payment_method === method.value} onChange={handleChange} style={{ display: 'none' }} />
                  {method.label}
                </label>
              ))}
            </div>

            <button type="submit" className="btn btn-primary" style={{ width: '100%', height: 52, fontSize: 16 }} disabled={loading || items.length === 0}>
              {loading ? <><span className="loading-spinner" style={{ width: 20, height: 20 }}></span> Đang xử lý...</> : '🚀 Đặt Hàng'}
            </button>
          </form>
        </div>

        {/* Order Summary */}
        <div className="card" style={{ position: 'sticky', top: 80 }}>
          <h2 style={{ fontFamily: 'var(--font-display)', fontSize: 16, fontWeight: 700, marginBottom: 16 }}>Đơn Hàng ({items.length} sản phẩm)</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginBottom: 16, maxHeight: 280, overflowY: 'auto' }}>
            {items.map(item => (
              <div key={item.id} style={{ display: 'flex', justifyContent: 'space-between', fontSize: 14 }}>
                <span style={{ color: 'var(--text-secondary)', flex: 1 }}>{item.product_name} ×{item.quantity}</span>
                <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-primary)', whiteSpace: 'nowrap', marginLeft: 8 }}>
                  {formatPrice(parseFloat(item.price) * item.quantity)}
                </span>
              </div>
            ))}
          </div>
          <div style={{ height: 1, background: 'var(--border-subtle)', margin: '16px 0' }}></div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 700 }}>
            <span>Tổng Cộng</span>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 20, color: 'var(--accent-primary)' }}>{formatPrice(total)}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

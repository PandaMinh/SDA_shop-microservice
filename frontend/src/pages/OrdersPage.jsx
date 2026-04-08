import React, { useState, useEffect } from 'react';
import api from '../api';
import { useAuth } from '../context/AuthContext';

const formatPrice = (price) => new Intl.NumberFormat('vi-VN').format(price) + ' đ';
const formatDate = (d) => new Date(d).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });

const statusLabel = { pending: 'Chờ xác nhận', confirmed: 'Đã xác nhận', shipping: 'Đang giao', delivered: 'Đã giao', cancelled: 'Đã hủy' };

export default function OrdersPage() {
  const { user } = useAuth();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetch = async () => {
      setLoading(true);
      try {
        const res = await api.get('/api/orders');
        setOrders(res.data || []);
      } catch (e) {
        setOrders([]);
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, []);

  if (loading) {
    return (
      <div className="container" style={{ padding: '60px 24px' }}>
        {[1, 2, 3].map(i => <div key={i} className="skeleton" style={{ height: 120, borderRadius: 12, marginBottom: 16 }} />)}
      </div>
    );
  }

  return (
    <div className="container" style={{ padding: '40px 24px' }}>
      <div className="page-header">
        <h1 className="page-title">📋 Đơn Hàng Của Tôi</h1>
        <p className="page-subtitle">{orders.length} đơn hàng</p>
      </div>

      {orders.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '80px 20px' }}>
          <div style={{ fontSize: 60, marginBottom: 16 }}>📦</div>
          <h3 style={{ fontFamily: 'var(--font-display)', fontSize: 22, color: 'var(--text-secondary)' }}>Chưa có đơn hàng nào</h3>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {orders.map(order => (
            <div key={order.id} className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 }}>
                <div>
                  <p style={{ fontFamily: 'var(--font-mono)', fontSize: 16, fontWeight: 600, color: 'var(--text-primary)' }}>#{order.id}</p>
                  <p style={{ color: 'var(--text-muted)', fontSize: 13 }}>{formatDate(order.created_at)}</p>
                </div>
                <span className={`badge badge-${order.status}`}>{statusLabel[order.status] || order.status}</span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6, marginBottom: 16 }}>
                {(order.items || []).map(item => (
                  <div key={item.id} style={{ display: 'flex', justifyContent: 'space-between', fontSize: 14 }}>
                    <span style={{ color: 'var(--text-secondary)' }}>{item.product_name} ×{item.quantity}</span>
                    <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-primary)' }}>{formatPrice(parseFloat(item.price) * item.quantity)}</span>
                  </div>
                ))}
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid var(--border-subtle)', paddingTop: 12 }}>
                <span style={{ color: 'var(--text-secondary)', fontSize: 14 }}>📍 {order.shipping_address}</span>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: 18, fontWeight: 700, color: 'var(--accent-primary)' }}>{formatPrice(order.total_amount)}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

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
  const [error, setError] = useState('');
  const [reviewDrafts, setReviewDrafts] = useState({});
  const [reviewSubmitting, setReviewSubmitting] = useState({});

  useEffect(() => {
    const fetch = async () => {
      if (!user?.customer_id) {
        setLoading(false);
        return;
      }
      setLoading(true);
      setError('');
      try {
        const res = await api.get('/api/orders', { params: { customer_id: user.customer_id } });
        setOrders(res.data || []);
      } catch (e) {
        setOrders([]);
        setError(e.response?.data?.error || 'Không thể tải đơn hàng. Vui lòng thử lại.');
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, [user]);

  const draftKey = (orderId, item) => `${orderId}-${item.product_id}-${item.product_type}`;

  const getDraft = (key) => reviewDrafts[key] || { rating: 5, comment: '' };

  const updateDraft = (key, patch) => {
    setReviewDrafts(prev => ({
      ...prev,
      [key]: { ...getDraft(key), ...patch },
    }));
  };

  const submitReview = async (orderId, item) => {
    const key = draftKey(orderId, item);
    const draft = getDraft(key);
    setReviewSubmitting(prev => ({ ...prev, [key]: true }));
    try {
      const res = await api.post(`/api/orders/${orderId}/reviews`, {
        product_id: item.product_id,
        product_type: item.product_type,
        rating: draft.rating,
        comment: draft.comment,
      });
      setOrders(prev => prev.map(order => {
        if (order.id !== orderId) return order;
        const reviews = order.reviews ? [...order.reviews, res.data] : [res.data];
        return { ...order, reviews };
      }));
      setReviewDrafts(prev => ({ ...prev, [key]: { rating: 5, comment: '' } }));
    } catch (e) {
      alert(e.response?.data?.error || 'Gửi đánh giá thất bại');
    } finally {
      setReviewSubmitting(prev => ({ ...prev, [key]: false }));
    }
  };

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

      {error && (
        <div className="card" style={{ marginBottom: 16, color: 'var(--danger)' }}>
          {error}
        </div>
      )}

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
                  <div key={item.id} style={{ borderBottom: '1px dashed var(--border-subtle)', paddingBottom: 10 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 14 }}>
                      <span style={{ color: 'var(--text-secondary)' }}>{item.product_name} ×{item.quantity}</span>
                      <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-primary)' }}>{formatPrice(parseFloat(item.price) * item.quantity)}</span>
                    </div>
                    {order.status === 'delivered' && (
                      (() => {
                        const key = draftKey(order.id, item);
                        const existing = (order.reviews || []).find(r => r.product_id === item.product_id && r.product_type === item.product_type);
                        if (existing) {
                          return (
                            <div style={{ marginTop: 8, fontSize: 13, color: 'var(--text-secondary)' }}>
                              <div>Đã đánh giá: {'★'.repeat(existing.rating)}{'☆'.repeat(5 - existing.rating)}</div>
                              {existing.comment && <div style={{ marginTop: 4 }}>{existing.comment}</div>}
                            </div>
                          );
                        }
                        const draft = getDraft(key);
                        return (
                          <div style={{ marginTop: 8, display: 'grid', gridTemplateColumns: '120px 1fr auto', gap: 8, alignItems: 'center' }}>
                            <select
                              className="form-input"
                              value={draft.rating}
                              onChange={e => updateDraft(key, { rating: parseInt(e.target.value, 10) })}
                              style={{ padding: '6px 8px', fontSize: 13 }}
                            >
                              {[5, 4, 3, 2, 1].map(v => <option key={v} value={v}>{v} sao</option>)}
                            </select>
                            <input
                              className="form-input"
                              placeholder="Nhận xét sản phẩm"
                              value={draft.comment}
                              onChange={e => updateDraft(key, { comment: e.target.value })}
                              style={{ padding: '6px 10px', fontSize: 13 }}
                            />
                            <button
                              className="btn btn-primary btn-sm"
                              onClick={() => submitReview(order.id, item)}
                              disabled={reviewSubmitting[key]}
                            >
                              {reviewSubmitting[key] ? 'Đang gửi...' : 'Gửi'}
                            </button>
                          </div>
                        );
                      })()
                    )}
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

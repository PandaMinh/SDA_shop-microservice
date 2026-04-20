import React, { useEffect, useState } from 'react';
import api from '../api';
import ProductCard from './ProductCard';
import { useAuth } from '../context/AuthContext';

export default function RecommendationPanel({
  title = 'Đề xuất cho bạn',
  subtitle = 'Từ lịch sử tìm kiếm, xem, mua, giỏ hàng và yêu thích',
  query = '',
  signal = '',
  emptyMessage = 'Chưa có sản phẩm đề xuất.',
}) {
  const { user } = useAuth();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchRecommendations = async () => {
      if (!user?.customer_id) {
        setProducts([]);
        return;
      }
      try {
        setLoading(true);
        const res = await api.get('/api/ai/recommendations', {
          params: { customer_id: user.customer_id, query, signal },
        });
        setProducts(res.data.products || []);
      } catch {
        setProducts([]);
      } finally {
        setLoading(false);
      }
    };
    fetchRecommendations();
  }, [user, query, signal]);

  return (
    <section style={{ marginTop: 32 }}>
      <div className="page-header" style={{ paddingTop: 0 }}>
        <h2 className="page-title" style={{ fontSize: 24 }}>{title}</h2>
        <p className="page-subtitle">{subtitle}</p>
      </div>
      {!user?.customer_id ? (
        <div className="card" style={{ padding: 20 }}>
          <p style={{ margin: 0, color: 'var(--text-secondary)' }}>Đăng nhập để xem đề xuất cá nhân hóa.</p>
        </div>
      ) : loading ? (
        <div className="card" style={{ padding: 20 }}>
          <p style={{ margin: 0, color: 'var(--text-secondary)' }}>Đang tải đề xuất...</p>
        </div>
      ) : products.length === 0 ? (
        <div className="card" style={{ padding: 20 }}>
          <p style={{ margin: 0, color: 'var(--text-secondary)' }}>{emptyMessage}</p>
        </div>
      ) : (
        <div className="product-grid">
          {products.slice(0, 6).map(product => (
            <ProductCard key={`${product.type || 'mix'}-${product.id}`} product={product} />
          ))}
        </div>
      )}
    </section>
  );
}

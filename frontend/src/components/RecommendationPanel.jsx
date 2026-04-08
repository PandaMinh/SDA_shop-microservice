import React, { useEffect, useState } from 'react';
import api from '../api';
import ProductCard from './ProductCard';
import { useAuth } from '../context/AuthContext';

export default function RecommendationPanel() {
  const { user } = useAuth();
  const [products, setProducts] = useState([]);

  useEffect(() => {
    const fetchRecommendations = async () => {
      if (!user?.customer_id) {
        setProducts([]);
        return;
      }
      try {
        const res = await api.get('/api/ai/recommendations', { params: { customer_id: user.customer_id } });
        setProducts(res.data.products || []);
      } catch {
        setProducts([]);
      }
    };
    fetchRecommendations();
  }, [user]);

  if (!user?.customer_id || products.length === 0) {
    return null;
  }

  return (
    <section style={{ marginTop: 32 }}>
      <div className="page-header" style={{ paddingTop: 0 }}>
        <h2 className="page-title" style={{ fontSize: 24 }}>Đề xuất cho bạn</h2>
        <p className="page-subtitle">Từ lịch sử tìm kiếm, xem, mua, giỏ hàng và yêu thích</p>
      </div>
      <div className="product-grid">
        {products.slice(0, 6).map(product => (
          <ProductCard key={`${product.type || 'mix'}-${product.id}`} product={product} />
        ))}
      </div>
    </section>
  );
}

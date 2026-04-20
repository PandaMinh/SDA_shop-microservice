import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api';
import { useCart } from '../context/CartContext';
import { useAuth } from '../context/AuthContext';
import { isFavorite, toggleFavorite } from '../utils/favorites';

const formatPrice = (price) => new Intl.NumberFormat('vi-VN').format(price) + ' đ';

export default function ProductDetailPage() {
  const { type, id } = useParams();
  const navigate = useNavigate();
  const { addToCart } = useCart();
  const { user } = useAuth();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [quantity, setQuantity] = useState(1);
  const [adding, setAdding] = useState(false);
  const [added, setAdded] = useState(false);
  const [error, setError] = useState('');
  const [specsOpen, setSpecsOpen] = useState(true);
  const [favorite, setFavorite] = useState(false);

  useEffect(() => {
    const fetch = async () => {
      setLoading(true);
      try {
        const res = await api.get(`/api/products/${type}/${id}`);
        setProduct({ ...res.data, type });
      } catch (e) {
        setError('Không tìm thấy sản phẩm.');
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, [type, id]);

  useEffect(() => {
    if (!user?.customer_id || !product) return;
    api.post('/api/ai/events', {
      customer_id: user.customer_id,
      event_type: 'view',
      product_id: product.id,
      product_type: type,
      product_name: product.name,
      metadata: { brand: product.brand, category: product.category },
    }).catch(() => {});
  }, [user, product, type]);

  useEffect(() => {
    if (!product) return;
    setFavorite(isFavorite(product.id, type));
  }, [product, type]);

  const handleAddToCart = async () => {
    if (!user) { navigate('/login'); return; }
    setAdding(true);
    try {
      await addToCart(parseInt(id), type, quantity);
      if (user?.customer_id && product) {
        api.post('/api/ai/events', {
          customer_id: user.customer_id,
          event_type: 'cart',
          product_id: product.id,
          product_type: type,
          product_name: product.name,
          metadata: { brand: product.brand, category: product.category, quantity },
        }).catch(() => {});
      }
      setAdded(true);
      setTimeout(() => setAdded(false), 2000);
    } catch (e) {
      navigate('/login');
    } finally {
      setAdding(false);
    }
  };

  const handleFavorite = () => {
    const payload = {
      id: product.id,
      type,
      name: product.name,
      brand: product.brand,
      category: product.category,
      price: product.price,
      image_url: product.image_url,
      stock: product.stock,
    };
    const next = toggleFavorite(payload);
    setFavorite(next);
    if (user?.customer_id && product) {
      api.post('/api/ai/events', {
        customer_id: user.customer_id,
        event_type: 'favorite',
        product_id: product.id,
        product_type: type,
        product_name: product.name,
        metadata: { brand: product.brand, category: product.category, favorite: next },
      }).catch(() => {});
    }
  };

  const stockStatus = (stock) => {
    if (!stock) return { text: 'Hết hàng', color: 'var(--danger)' };
    if (stock <= 5) return { text: `Còn ${stock} sản phẩm`, color: 'var(--warning)' };
    return { text: `✓ Còn hàng (${stock} sản phẩm)`, color: 'var(--success)' };
  };

  const categoryNames = { phone: 'Điện thoại', tablet: 'Máy tính bảng', laptop: 'Laptop', pc: 'PC Desktop' };
  const typeNames = { mobile: 'Di Động', desktop: 'Máy Tính' };

  if (loading) {
    return (
      <div className="container" style={{ padding: '60px 24px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 48 }}>
          <div className="skeleton" style={{ height: 480, borderRadius: 16 }} />
          <div>
            <div className="skeleton" style={{ height: 32, marginBottom: 16, borderRadius: 8 }} />
            <div className="skeleton" style={{ height: 24, width: '60%', marginBottom: 24, borderRadius: 8 }} />
            <div className="skeleton" style={{ height: 48, marginBottom: 32, borderRadius: 8 }} />
            <div className="skeleton" style={{ height: 52, borderRadius: 10 }} />
          </div>
        </div>
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="container" style={{ padding: '80px 24px', textAlign: 'center' }}>
        <div style={{ fontSize: 60, marginBottom: 16 }}>😕</div>
        <h2 style={{ fontFamily: 'var(--font-display)', color: 'var(--text-secondary)', marginBottom: 16 }}>{error}</h2>
        <button className="btn btn-secondary" onClick={() => navigate('/')}>← Về Trang Chủ</button>
      </div>
    );
  }

  const stock = stockStatus(product.stock);

  return (
    <div className="container" style={{ padding: '40px 24px' }}>
      <button
        className="btn btn-secondary btn-sm"
        style={{ marginBottom: 32 }}
        onClick={() => navigate(-1)}
      >
        ← Quay Lại
      </button>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 48, alignItems: 'start' }}>
        {/* Image */}
        <div style={{ borderRadius: 20, overflow: 'hidden', background: 'var(--bg-elevated)', border: '1px solid var(--border-subtle)' }}>
          <img
            src={product.image_url || `https://picsum.photos/600/500?random=${product.id}`}
            alt={product.name}
            style={{ width: '100%', display: 'block', objectFit: 'cover' }}
            onError={e => { e.target.src = `https://picsum.photos/600/500?random=${product.id + 50}`; }}
          />
        </div>

        {/* Details */}
        <div>
          <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
            <span className={`badge badge-${product.category}`}>{categoryNames[product.category] || product.category}</span>
            <span className={`badge badge-${type}`}>{typeNames[type]}</span>
          </div>

          <h1 style={{ fontFamily: 'var(--font-display)', fontSize: 28, fontWeight: 700, marginBottom: 8, letterSpacing: '-0.5px', color: 'var(--text-primary)' }}>
            {product.name}
          </h1>

          <p style={{ color: 'var(--text-secondary)', fontSize: 15, marginBottom: 4 }}>
            Thương hiệu: <strong style={{ color: 'var(--text-primary)' }}>{product.brand}</strong>
          </p>

          <p style={{ color: stock.color, fontSize: 14, marginBottom: 24, display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{ width: 8, height: 8, borderRadius: '50%', background: stock.color, display: 'inline-block' }}></span>
            {stock.text}
          </p>

          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 34, fontWeight: 700, color: 'var(--accent-primary)', marginBottom: 32 }}>
            {formatPrice(product.price)}
          </div>

          {product.description && (
            <p style={{ color: 'var(--text-secondary)', fontSize: 15, lineHeight: 1.7, marginBottom: 28, padding: '16px', background: 'var(--bg-elevated)', borderRadius: 10 }}>
              {product.description}
            </p>
          )}

          {/* Quantity */}
          {product.stock > 0 && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 24 }}>
              <span style={{ color: 'var(--text-secondary)', fontSize: 14, fontWeight: 500 }}>Số lượng:</span>
              <div style={{ display: 'flex', alignItems: 'center', gap: 0, background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 8, overflow: 'hidden' }}>
                <button onClick={() => setQuantity(q => Math.max(1, q - 1))} style={{ width: 36, height: 36, background: 'transparent', color: 'var(--text-primary)', fontSize: 18, border: 'none', cursor: 'pointer' }}>−</button>
                <span style={{ minWidth: 40, textAlign: 'center', fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{quantity}</span>
                <button onClick={() => setQuantity(q => Math.min(product.stock, q + 1))} style={{ width: 36, height: 36, background: 'transparent', color: 'var(--text-primary)', fontSize: 18, border: 'none', cursor: 'pointer' }}>+</button>
              </div>
            </div>
          )}

          <button
            className="btn btn-primary"
            style={{ width: '100%', height: 52, fontSize: 16 }}
            onClick={handleAddToCart}
            disabled={adding || product.stock === 0}
          >
            {adding ? <><span className="loading-spinner" style={{ width: 20, height: 20 }}></span> Đang thêm...</>
              : added ? '✓ Đã thêm vào giỏ hàng!'
              : product.stock === 0 ? 'Hết hàng'
              : `🛒 Thêm ${quantity > 1 ? quantity + ' sản phẩm' : ''} vào giỏ hàng`}
          </button>

          <button
            className="btn btn-secondary"
            style={{ width: '100%', height: 52, fontSize: 16, marginTop: 12 }}
            onClick={handleFavorite}
          >
            {favorite ? '♥ Đã yêu thích' : '♡ Thêm vào yêu thích'}
          </button>
        </div>
      </div>

      {/* Specs */}
      {product.specs && Object.keys(product.specs).length > 0 && (
        <div style={{ marginTop: 48 }}>
          <button
            onClick={() => setSpecsOpen(!specsOpen)}
            style={{ width: '100%', background: 'var(--bg-elevated)', border: '1px solid var(--border-subtle)', borderRadius: specsOpen ? '12px 12px 0 0' : 12, padding: '16px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer', color: 'var(--text-primary)', fontWeight: 600, fontSize: 15 }}
          >
            <span>📋 Thông Số Kỹ Thuật</span>
            <span>{specsOpen ? '▲' : '▼'}</span>
          </button>
          {specsOpen && (
            <div style={{ border: '1px solid var(--border-subtle)', borderTop: 'none', borderRadius: '0 0 12px 12px', overflow: 'hidden' }}>
              {Object.entries(product.specs).map(([key, value], i) => (
                <div key={key} style={{ display: 'flex', padding: '14px 20px', background: i % 2 === 0 ? 'var(--bg-card)' : 'var(--bg-secondary)' }}>
                  <span style={{ width: '40%', color: 'var(--text-secondary)', fontSize: 14, textTransform: 'capitalize' }}>{key.replace(/_/g, ' ')}</span>
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: 14, color: 'var(--text-primary)' }}>{value}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

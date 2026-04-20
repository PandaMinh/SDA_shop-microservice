import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import { useAuth } from '../context/AuthContext';
import api from '../api';
import { isFavorite, toggleFavorite } from '../utils/favorites';

const formatPrice = (price) => {
  return new Intl.NumberFormat('vi-VN').format(price) + ' đ';
};

export default function ProductCard({ product }) {
  const navigate = useNavigate();
  const { addToCart } = useCart();
  const { user, isAdmin } = useAuth();
  const [adding, setAdding] = useState(false);
  const [added, setAdded] = useState(false);
  const [favorite, setFavorite] = useState(false);

  const productType = product.type || (product.category === 'phone' || product.category === 'tablet' ? 'mobile' : 'desktop');

  useEffect(() => {
    setFavorite(isFavorite(product.id, productType));
  }, [product.id, productType]);

  const stockStatus = () => {
    if (product.stock === 0) return { text: 'Hết hàng', color: 'var(--danger)' };
    if (product.stock <= 5) return { text: `Còn ${product.stock} sản phẩm`, color: 'var(--warning)' };
    return { text: 'Còn hàng', color: 'var(--success)' };
  };

  const stock = stockStatus();

  const handleCardClick = () => {
    if (user?.customer_id) {
      api.post('/api/ai/events', {
        customer_id: user.customer_id,
        event_type: 'click',
        product_id: product.id,
        product_type: productType,
        product_name: product.name,
        metadata: { brand: product.brand, category: product.category },
      }).catch(() => {});
    }
    navigate(`/product/${productType}/${product.id}`);
  };

  const handleAddToCart = async (e) => {
    e.stopPropagation();
    if (!user || isAdmin) {
      navigate('/login');
      return;
    }
    if (product.stock === 0) return;
    setAdding(true);
    try {
      await addToCart(product.id, productType, 1);
      if (user?.customer_id) {
        api.post('/api/ai/events', {
          customer_id: user.customer_id,
          event_type: 'cart',
          product_id: product.id,
          product_type: productType,
          product_name: product.name,
          metadata: { brand: product.brand, category: product.category },
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

  const handleToggleFavorite = (e) => {
    e.stopPropagation();
    const payload = {
      id: product.id,
      type: productType,
      name: product.name,
      brand: product.brand,
      category: product.category,
      price: product.price,
      image_url: product.image_url,
      stock: product.stock,
    };
    const next = toggleFavorite(payload);
    setFavorite(next);
    if (user?.customer_id) {
      api.post('/api/ai/events', {
        customer_id: user.customer_id,
        event_type: 'favorite',
        product_id: product.id,
        product_type: productType,
        product_name: product.name,
        metadata: { brand: product.brand, category: product.category, favorite: next },
      }).catch(() => {});
    }
  };

  const getCategoryBadgeClass = () => {
    const cat = product.category;
    if (cat === 'phone') return 'badge badge-phone';
    if (cat === 'tablet') return 'badge badge-tablet';
    if (cat === 'laptop') return 'badge badge-laptop';
    if (cat === 'pc') return 'badge badge-pc';
    return 'badge badge-mobile';
  };

  const categoryNames = { phone: 'Điện thoại', tablet: 'Máy tính bảng', laptop: 'Laptop', pc: 'PC Desktop' };

  return (
    <div
      className="card"
      style={{ padding: 0, cursor: 'pointer', overflow: 'hidden', transition: 'all 0.25s', display: 'flex', flexDirection: 'column' }}
      onClick={handleCardClick}
      onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-4px)'; e.currentTarget.style.boxShadow = '0 12px 40px rgba(79, 70, 229, 0.1)'; e.currentTarget.style.borderColor = 'rgba(79, 70, 229, 0.3)'; }}
      onMouseLeave={e => { e.currentTarget.style.transform = ''; e.currentTarget.style.boxShadow = ''; e.currentTarget.style.borderColor = ''; }}
    >
      {/* Image */}
      <div style={{ position: 'relative', paddingBottom: '70%', overflow: 'hidden', background: 'var(--bg-elevated)' }}>
        <img
          src={product.image_url || `https://picsum.photos/400/400?random=${product.id}`}
          alt={product.name}
          style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover', transition: 'transform 0.4s ease' }}
          onMouseEnter={e => e.target.style.transform = 'scale(1.05)'}
          onMouseLeave={e => e.target.style.transform = ''}
          onError={e => { e.target.src = `https://picsum.photos/400/400?random=${product.id + 100}`; }}
        />
        <div style={{ position: 'absolute', top: 10, left: 10 }}>
          <span className={getCategoryBadgeClass()}>{categoryNames[product.category] || product.category}</span>
        </div>
        <div style={{ position: 'absolute', top: 10, right: 10, background: 'rgba(0,0,0,0.6)', borderRadius: 6, padding: '2px 8px', fontSize: 12 }}>
          {product.brand}
        </div>
      </div>

      {/* Content */}
      <div style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: 8, flex: 1 }}>
        <h3 style={{ fontFamily: 'var(--font-display)', fontSize: 15, fontWeight: 600, color: 'var(--text-primary)', lineHeight: 1.3, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
          {product.name}
        </h3>

        <div style={{ fontSize: 12, color: stock.color, display: 'flex', alignItems: 'center', gap: 4 }}>
          <span style={{ width: 6, height: 6, borderRadius: '50%', background: stock.color, display: 'inline-block' }}></span>
          {stock.text}
        </div>

        <div style={{ fontFamily: 'var(--font-mono)', fontSize: 18, fontWeight: 700, color: 'var(--accent-primary)', marginTop: 'auto' }}>
          {formatPrice(product.price)}
        </div>

        <button
          className="btn btn-secondary btn-sm"
          style={{ width: '100%', marginTop: 4, fontSize: 13, padding: '10px' }}
          onClick={handleToggleFavorite}
        >
          {favorite ? '♥ Đã yêu thích' : '♡ Yêu thích'}
        </button>

        <button
          className={`btn btn-primary`}
          style={{ width: '100%', marginTop: 4, fontSize: 13, padding: '10px' }}
          onClick={handleAddToCart}
          disabled={adding || product.stock === 0}
        >
          {adding ? <span className="loading-spinner" style={{ width: 16, height: 16 }}></span>
            : added ? '✓ Đã thêm!'
            : product.stock === 0 ? 'Hết hàng'
            : '🛒 Thêm vào giỏ'}
        </button>
      </div>
    </div>
  );
}

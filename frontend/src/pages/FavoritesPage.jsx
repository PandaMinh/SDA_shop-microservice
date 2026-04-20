import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import ProductCard from '../components/ProductCard';
import { getFavorites, saveFavorites } from '../utils/favorites';

export default function FavoritesPage() {
  const [favorites, setFavorites] = useState([]);

  useEffect(() => {
    setFavorites(getFavorites());
    const onStorage = (e) => {
      if (e.key === 'favorite_products') {
        setFavorites(getFavorites());
      }
    };
    const onUpdate = () => setFavorites(getFavorites());
    window.addEventListener('storage', onStorage);
    window.addEventListener('favorites-updated', onUpdate);
    return () => {
      window.removeEventListener('storage', onStorage);
      window.removeEventListener('favorites-updated', onUpdate);
    };
  }, []);

  const clearAll = () => {
    saveFavorites([]);
    setFavorites([]);
  };

  if (favorites.length === 0) {
    return (
      <div className="container" style={{ padding: '80px 24px', textAlign: 'center' }}>
        <div style={{ fontSize: 72, marginBottom: 24 }}>💖</div>
        <h2 style={{ fontFamily: 'var(--font-display)', fontSize: 26, marginBottom: 12 }}>Chưa có sản phẩm yêu thích</h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: 32 }}>Hãy thêm sản phẩm bạn thích để xem lại ở đây.</p>
        <Link to="/">
          <button className="btn btn-primary">Khám Phá Sản Phẩm →</button>
        </Link>
      </div>
    );
  }

  return (
    <div className="container" style={{ padding: '40px 24px' }}>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 className="page-title">💖 Sản Phẩm Yêu Thích</h1>
          <p className="page-subtitle">{favorites.length} sản phẩm</p>
        </div>
        <button className="btn btn-secondary btn-sm" onClick={clearAll} style={{ color: 'var(--danger)' }}>
          Xóa tất cả
        </button>
      </div>

      <div className="product-grid">
        {favorites.map(item => (
          <ProductCard key={`${item.type}-${item.id}`} product={item} />
        ))}
      </div>
    </div>
  );
}

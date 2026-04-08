import React, { useState, useEffect } from 'react';
import api from '../api';
import ProductCard from '../components/ProductCard';
import RecommendationPanel from '../components/RecommendationPanel';
import { useAuth } from '../context/AuthContext';

const CATEGORIES = [
  { key: 'all', label: '✦ Tất Cả', type: null, cat: null },
  { key: 'phone', label: '📱 Điện Thoại', type: 'mobile', cat: 'phone' },
  { key: 'tablet', label: '📟 Máy Tính Bảng', type: 'mobile', cat: 'tablet' },
  { key: 'laptop', label: '💻 Laptop', type: 'desktop', cat: 'laptop' },
  { key: 'pc', label: '🖥️ PC Desktop', type: 'desktop', cat: 'pc' },
  { key: 'shirt', label: '👕 Áo', type: 'clothes', cat: 'shirt' },
  { key: 'pants', label: '👖 Quần', type: 'clothes', cat: 'pants' },
];

export default function HomePage() {
  const { user } = useAuth();
  const [products, setProducts] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeCategory, setActiveCategory] = useState('all');
  const [search, setSearch] = useState('');

  useEffect(() => {
    const fetchProducts = async () => {
      setLoading(true);
      try {
        const res = await api.get('/api/products');
        setProducts(res.data.products || []);
      } catch (e) {
        setProducts([]);
      } finally {
        setLoading(false);
      }
    };
    fetchProducts();
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (!search.trim() || !user?.customer_id) return;
      api.post('/api/ai/events', {
        customer_id: user.customer_id,
        event_type: 'search',
        query: search,
        metadata: { category: activeCategory },
      }).catch(() => {});
    }, 400);
    return () => clearTimeout(timer);
  }, [search, activeCategory, user]);

  useEffect(() => {
    let result = products;
    const cat = CATEGORIES.find(c => c.key === activeCategory);
    if (cat && cat.cat) {
      result = result.filter(p => p.category === cat.cat);
    }
    if (search.trim()) {
      const term = search.toLowerCase();
      result = result.filter(p => p.name.toLowerCase().includes(term) || p.brand.toLowerCase().includes(term));
    }
    setFiltered(result);
  }, [products, activeCategory, search]);

  return (
    <div>
      {/* Hero */}
      <div style={{
        background: 'linear-gradient(135deg, #f4f6f8 0%, #eef2f6 50%, #f4f6f8 100%)',
        borderBottom: '1px solid var(--border-subtle)',
        padding: '80px 0 60px',
        position: 'relative',
        overflow: 'hidden',
      }}>
        {/* Glow orbs */}
        <div style={{ position: 'absolute', top: -100, left: '20%', width: 400, height: 400, background: 'radial-gradient(circle, rgba(79, 70, 229, 0.1) 0%, transparent 70%)', borderRadius: '50%', pointerEvents: 'none' }} />
        <div style={{ position: 'absolute', bottom: -80, right: '15%', width: 300, height: 300, background: 'radial-gradient(circle, rgba(147, 51, 234, 0.08) 0%, transparent 70%)', borderRadius: '50%', pointerEvents: 'none' }} />

        <div className="container" style={{ position: 'relative', textAlign: 'center' }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, background: 'rgba(79, 70, 229, 0.1)', border: '1px solid rgba(79, 70, 229, 0.2)', borderRadius: 20, padding: '6px 16px', marginBottom: 24, fontSize: 13, color: '#4f46e5' }}>
            ⚡ Sản phẩm công nghệ cao cấp
          </div>
          <h1 style={{ fontFamily: 'var(--font-display)', fontSize: 56, fontWeight: 800, lineHeight: 1.1, marginBottom: 20, letterSpacing: '-1px' }}>
            <span style={{ background: 'var(--accent-gradient)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>Công Nghệ</span>
            <br />
            <span style={{ color: 'var(--text-primary)' }}>Đỉnh Cao 2025</span>
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: 18, maxWidth: 500, margin: '0 auto 36px', lineHeight: 1.7 }}>
            Khám phá bộ sưu tập điện thoại và laptop mới nhất từ các thương hiệu hàng đầu thế giới.
          </p>
          {/* Search */}
          <div style={{ maxWidth: 480, margin: '0 auto', position: 'relative' }}>
            <span style={{ position: 'absolute', left: 16, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)', fontSize: 16 }}>🔍</span>
            <input
              type="text"
              placeholder="Tìm kiếm sản phẩm, thương hiệu..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="form-input"
              style={{ paddingLeft: 44, height: 52, fontSize: 15, borderRadius: 12 }}
            />
          </div>
        </div>
      </div>

      <div className="container" style={{ padding: '40px 24px' }}>
        {/* Category Tabs */}
        <div className="tabs">
          {CATEGORIES.map(cat => (
            <button
              key={cat.key}
              className={`tab ${activeCategory === cat.key ? 'active' : ''}`}
              onClick={() => setActiveCategory(cat.key)}
            >
              {cat.label}
            </button>
          ))}
        </div>

        {/* Results count */}
        {!loading && (
          <p style={{ color: 'var(--text-muted)', fontSize: 14, marginBottom: 20, marginTop: -16 }}>
            {filtered.length} sản phẩm
          </p>
        )}

        {/* Grid */}
        {loading ? (
          <div className="product-grid">
            {Array.from({ length: 8 }).map((_, i) => (
              <div key={i} style={{ borderRadius: 16, overflow: 'hidden' }}>
                <div className="skeleton" style={{ paddingBottom: '70%' }} />
                <div style={{ padding: 16, background: 'var(--bg-card)' }}>
                  <div className="skeleton" style={{ height: 20, marginBottom: 12, borderRadius: 4 }} />
                  <div className="skeleton" style={{ height: 16, width: '60%', marginBottom: 12, borderRadius: 4 }} />
                  <div className="skeleton" style={{ height: 42, borderRadius: 8 }} />
                </div>
              </div>
            ))}
          </div>
        ) : filtered.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '80px 20px' }}>
            <div style={{ fontSize: 60, marginBottom: 16 }}>📦</div>
            <h3 style={{ fontFamily: 'var(--font-display)', fontSize: 22, color: 'var(--text-secondary)', marginBottom: 8 }}>
              Không tìm thấy sản phẩm
            </h3>
            <p style={{ color: 'var(--text-muted)' }}>Thử tìm kiếm với từ khóa khác</p>
          </div>
        ) : (
          <div className="product-grid">
            {filtered.map(product => (
              <ProductCard key={`${product.type}-${product.id}`} product={product} />
            ))}
          </div>
        )}

        <RecommendationPanel />
      </div>
    </div>
  );
}

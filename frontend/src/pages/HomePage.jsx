import React, { useState, useEffect } from 'react';
import api from '../api';
import ProductCard from '../components/ProductCard';
import RecommendationPanel from '../components/RecommendationPanel';
import { useAuth } from '../context/AuthContext';

const CATEGORIES = [
  { key: 'all', label: '✦ Tất Cả', type: null, cat: null },
  { key: 'phone', label: '📱 Điện Thoại', type: 'mobile', cat: 'phone' },
  { key: 'tablet', label: '📲 Máy Tính Bảng', type: 'mobile', cat: 'tablet' },
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
  const [searchInput, setSearchInput] = useState('');

  const executeSearch = () => {
    setSearch(searchInput);
  };

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
    if (!search.trim() || !user?.customer_id) return;
    api.post('/api/ai/events', {
      customer_id: user.customer_id,
      event_type: 'search',
      query: search,
      metadata: { category: activeCategory },
    }).catch(() => {});
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
      {/* Category Tabs (Top Bar) */}
      <div style={{ background: '#fff', borderBottom: '1px solid var(--border-subtle)', position: 'sticky', top: 0, zIndex: 10 }}>
        <div className="container" style={{ padding: '12px 24px' }}>
          <div className="tabs" style={{ marginBottom: 0, border: 'none', background: 'transparent', padding: 0 }}>
            {CATEGORIES.map(cat => (
              <button
                key={cat.key}
                className={`tab ${activeCategory === cat.key ? 'active' : ''}`}
                onClick={() => setActiveCategory(cat.key)}
                style={{ padding: '8px 16px', borderRadius: 20 }}
              >
                {cat.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Hero */}
      <div style={{
        background: 'linear-gradient(135deg, #f4f6f8 0%, #eef2f6 50%, #f4f6f8 100%)',
        borderBottom: '1px solid var(--border-subtle)',
        padding: '60px 0 40px',
        position: 'relative',
        overflow: 'hidden',
      }}>
        <div style={{ position: 'absolute', top: -100, left: '20%', width: 400, height: 400, background: 'radial-gradient(circle, rgba(79, 70, 229, 0.1) 0%, transparent 70%)', borderRadius: '50%', pointerEvents: 'none' }} />
        <div style={{ position: 'absolute', bottom: -80, right: '15%', width: 300, height: 300, background: 'radial-gradient(circle, rgba(147, 51, 234, 0.08) 0%, transparent 70%)', borderRadius: '50%', pointerEvents: 'none' }} />

        <div className="container" style={{ position: 'relative', textAlign: 'center' }}>
          <h1 style={{ fontFamily: 'var(--font-display)', fontSize: 56, fontWeight: 800, lineHeight: 1.1, marginBottom: 20, letterSpacing: '-1px' }}>
            <span style={{ background: 'var(--accent-gradient)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>Công Nghệ</span>
            <br />
            <span style={{ color: 'var(--text-primary)' }}>Đỉnh Cao 2025</span>
          </h1>

          {/* Search */}
          <div style={{ maxWidth: 480, margin: '24px auto 0', position: 'relative', display: 'flex', gap: 8 }}>
            <input
              type="text"
              placeholder="Tìm kiếm sản phẩm, thương hiệu..."
              value={searchInput}
              onChange={e => setSearchInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && executeSearch()}
              className="form-input"
              style={{ flex: 1, paddingLeft: 24, height: 52, fontSize: 16, borderRadius: '26px' }}
            />
            <button 
              className="btn btn-primary" 
              onClick={executeSearch}
              style={{ borderRadius: '26px', padding: '0 24px', height: 52 }}
            >
              <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
              </svg>
            </button>
          </div>
        </div>
      </div>

      <div className="container" style={{ padding: '24px 24px 60px' }}>
        <RecommendationPanel
          title={search ? 'Đề xuất theo lượt search mới nhất' : 'Đề xuất cho bạn'}
          subtitle={search ? `Dựa trên từ khóa "${search}" và model_best của ai-service` : 'Từ lịch sử tìm kiếm, xem, mua, giỏ hàng và yêu thích'}
          query={search}
          signal={search ? 'search' : ''}
          emptyMessage="Chưa có sản phẩm khớp với ngữ cảnh tìm kiếm hiện tại."
        />

        {/* Results count */}
        {!loading && (
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24, marginTop: 16 }}>
            <h2 style={{ margin: 0, fontSize: 22 }}>Danh sách sản phẩm</h2>
            <p style={{ color: 'var(--text-muted)', fontSize: 14, margin: 0 }}>
              {filtered.length} sản phẩm
            </p>
          </div>
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
            <div style={{ fontSize: 60, marginBottom: 16 }}></div>
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
      </div>
    </div>
  );
}

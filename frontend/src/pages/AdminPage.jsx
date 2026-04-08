import React, { useState, useEffect } from 'react';
import api from '../api';

const formatPrice = (price) => new Intl.NumberFormat('vi-VN').format(price) + ' đ';
const formatDate = (d) => new Date(d).toLocaleDateString('vi-VN');
const STATUS_LIST = ['pending', 'confirmed', 'shipping', 'delivered', 'cancelled'];
const STATUS_LABEL = { pending: 'Chờ xác nhận', confirmed: 'Đã xác nhận', shipping: 'Đang giao', delivered: 'Đã giao', cancelled: 'Đã hủy' };

function ProductModal({ product, onClose, onSave, productType }) {
  const [form, setForm] = useState(
    product || { name: '', brand: '', category: productType === 'mobile' ? 'phone' : 'laptop', price: '', stock: 0, description: '', image_url: '', specs: {} }
  );
  const [saving, setSaving] = useState(false);
  const [specsText, setSpecsText] = useState(JSON.stringify(form.specs || {}, null, 2));

  const handleChange = e => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async e => {
    e.preventDefault();
    setSaving(true);
    try {
      const payload = { ...form, specs: JSON.parse(specsText || '{}') };
      if (product?.id) {
        await api.put(`/api/admin/products/${productType}/${product.id}`, payload);
      } else {
        await api.post(`/api/admin/products/${productType}`, payload);
      }
      onSave();
      onClose();
    } catch (err) {
      alert('Lỗi: ' + (err.response?.data?.error || err.message));
    } finally {
      setSaving(false);
    }
  };

  const categories = productType === 'mobile' ? ['phone', 'tablet'] : productType === 'desktop' ? ['laptop', 'pc'] : ['shirt', 'pants'];
  const categoryLabel = { phone: 'Điện thoại', tablet: 'Máy tính bảng', laptop: 'Laptop', pc: 'PC Desktop', shirt: 'Áo', pants: 'Quần' };

  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <h2 className="modal-title">{product?.id ? '✏️ Sửa Sản Phẩm' : '➕ Thêm Sản Phẩm'}</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Tên Sản Phẩm</label>
            <input name="name" value={form.name} onChange={handleChange} required className="form-input" placeholder="iPhone 16 Pro" />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div className="form-group">
              <label className="form-label">Thương Hiệu</label>
              <input name="brand" value={form.brand} onChange={handleChange} required className="form-input" placeholder="Apple" />
            </div>
            <div className="form-group">
              <label className="form-label">Loại</label>
              <select name="category" value={form.category} onChange={handleChange} className="form-input">
                {categories.map(c => <option key={c} value={c}>{categoryLabel[c]}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Giá (VND)</label>
              <input name="price" type="number" value={form.price} onChange={handleChange} required className="form-input" placeholder="28990000" />
            </div>
            <div className="form-group">
              <label className="form-label">Tồn Kho</label>
              <input name="stock" type="number" value={form.stock} onChange={handleChange} required className="form-input" />
            </div>
          </div>
          <div className="form-group">
            <label className="form-label">URL Ảnh</label>
            <input name="image_url" value={form.image_url} onChange={handleChange} className="form-input" placeholder="https://..." />
          </div>
          <div className="form-group">
            <label className="form-label">Mô Tả</label>
            <textarea name="description" value={form.description} onChange={handleChange} className="form-input" rows={3} style={{ resize: 'vertical' }} />
          </div>
          <div className="form-group">
            <label className="form-label">Thông Số (JSON)</label>
            <textarea value={specsText} onChange={e => setSpecsText(e.target.value)} className="form-input" rows={4} style={{ fontFamily: 'var(--font-mono)', fontSize: 13, resize: 'vertical' }} />
          </div>
          <div style={{ display: 'flex', gap: 12, justifyContent: 'flex-end', marginTop: 8 }}>
            <button type="button" className="btn btn-secondary" onClick={onClose}>Hủy</button>
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? <span className="loading-spinner" style={{ width: 16, height: 16 }}></span> : product?.id ? 'Cập Nhật' : 'Thêm Mới'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function ImportModal({ product, onClose, onSave, productType }) {
  const [form, setForm] = useState({ quantity_imported: '', cost_price: '', supplier: '', note: '' });
  const [saving, setSaving] = useState(false);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    api.get(`/api/admin/products/${productType}/${product.id}/imports`).then(res => setHistory(res.data)).catch(() => {});
  }, [product, productType]);

  const handleChange = e => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async e => {
    e.preventDefault();
    setSaving(true);
    try {
      await api.post(`/api/admin/products/${productType}/${product.id}/import`, form);
      onSave();
      api.get(`/api/admin/products/${productType}/${product.id}/imports`).then(res => setHistory(res.data)).catch(() => {});
      setForm({ quantity_imported: '', cost_price: '', supplier: '', note: '' });
    } catch (err) {
      alert('Lỗi: ' + (err.response?.data?.error || err.message));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal" style={{ maxWidth: 640 }}>
        <h2 className="modal-title">📦 Nhập Hàng: {product.name}</h2>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
          {/* Form Create */}
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Số Lượng Nhập</label>
              <input name="quantity_imported" type="number" value={form.quantity_imported} onChange={handleChange} required className="form-input" min="1" />
            </div>
            <div className="form-group">
              <label className="form-label">Giá Nhập (VND)</label>
              <input name="cost_price" type="number" value={form.cost_price} onChange={handleChange} className="form-input" />
            </div>
            <div className="form-group">
              <label className="form-label">Nhà Cung Cấp</label>
              <input name="supplier" value={form.supplier} onChange={handleChange} className="form-input" />
            </div>
            <div className="form-group">
              <label className="form-label">Ghi Chú</label>
              <textarea name="note" value={form.note} onChange={handleChange} className="form-input" rows={2}></textarea>
            </div>
            <button type="submit" className="btn btn-primary" style={{ width: '100%' }} disabled={saving}>
              {saving ? 'Đang Nhập...' : 'Xác Nhận Nhập Hàng'}
            </button>
          </form>

          {/* History */}
          <div>
            <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 12 }}>Lịch Sử Nhập Hàng</h3>
            <div style={{ maxHeight: 300, overflowY: 'auto', border: '1px solid var(--border)', borderRadius: 8, padding: 8 }}>
              {history.length === 0 ? <p style={{ color: 'var(--text-muted)', fontSize: 13, textAlign: 'center', padding: 20 }}>Chưa có lịch sử nhập hàng.</p> : history.map(h => (
                <div key={h.id} style={{ fontSize: 13, padding: '8px 0', borderBottom: '1px solid var(--border-subtle)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                    <span style={{ fontWeight: 600, color: 'var(--success)' }}>+{h.quantity_imported} SP</span>
                    <span style={{ color: 'var(--text-muted)' }}>{formatDate(h.created_at)}</span>
                  </div>
                  {h.cost_price && <div>Giá nhập: {formatPrice(h.cost_price)}</div>}
                  {h.supplier && <div style={{ color: 'var(--text-secondary)' }}>NCC: {h.supplier}</div>}
                </div>
              ))}
            </div>
          </div>
        </div>
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 16 }}>
          <button type="button" className="btn btn-secondary" onClick={onClose}>Đóng</button>
        </div>
      </div>
    </div>
  );
}

export default function AdminPage() {
  const [activeTab, setActiveTab] = useState('products');
  const [productType, setProductType] = useState('mobile');
  const [products, setProducts] = useState([]);
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editProduct, setEditProduct] = useState(null);
  const [importProduct, setImportProduct] = useState(null);
  const [statusFilter, setStatusFilter] = useState('all');
  const [recommendations, setRecommendations] = useState([]);

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        const res = await api.get('/api/ai/recommendations');
        setRecommendations(res.data.products || []);
      } catch {
        setRecommendations([]);
      }
    };
    if (activeTab === 'orders') {
      fetchRecommendations();
    }
  }, [activeTab]);

  const fetchProducts = async () => {
    setLoading(true);
    try {
      const res = await api.get(`/api/products/${productType}`);
      setProducts(res.data || []);
    } catch { setProducts([]); }
    finally { setLoading(false); }
  };

  const fetchOrders = async () => {
    setLoading(true);
    try {
      const res = await api.get('/api/admin/orders');
      setOrders(res.data || []);
    } catch { setOrders([]); }
    finally { setLoading(false); }
  };

  useEffect(() => { if (activeTab === 'products') fetchProducts(); }, [productType, activeTab]);
  useEffect(() => { if (activeTab === 'orders') fetchOrders(); }, [activeTab]);

  const handleDelete = async (id) => {
    if (!window.confirm('Bạn có chắc muốn xóa sản phẩm này?')) return;
    try {
      await api.delete(`/api/admin/products/${productType}/${id}`);
      fetchProducts();
    } catch (e) { alert('Xóa thất bại'); }
  };

  const handleStatusChange = async (orderId, status) => {
    try {
      await api.put(`/api/admin/orders/${orderId}`, { status });
      fetchOrders();
    } catch { alert('Cập nhật thất bại'); }
  };

  const filteredOrders = orders.filter(o => statusFilter === 'all' || o.status === statusFilter);

  return (
    <div className="container" style={{ padding: '40px 24px' }}>
      <div className="page-header">
        <h1 className="page-title">⚙️ Quản Trị TechStore</h1>
        <p className="page-subtitle">Quản lý sản phẩm và đơn hàng</p>
      </div>

      {/* Main Tabs */}
      <div className="tabs">
        <button className={`tab ${activeTab === 'products' ? 'active' : ''}`} onClick={() => setActiveTab('products')}>📦 Sản Phẩm</button>
        <button className={`tab ${activeTab === 'orders' ? 'active' : ''}`} onClick={() => setActiveTab('orders')}>📋 Đơn Hàng</button>
        <button className={`tab ${activeTab === 'recommendations' ? 'active' : ''}`} onClick={() => setActiveTab('recommendations')}>✨ Đề Xuất</button>
      </div>

      {/* Products Tab */}
      {activeTab === 'products' && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
            <div style={{ display: 'flex', gap: 8 }}>
              {['mobile', 'desktop', 'clothes'].map(t => (
                <button key={t} className={`btn btn-sm ${productType === t ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setProductType(t)}>
                  {t === 'mobile' ? '📱 Di Động' : t === 'desktop' ? '💻 Máy Tính' : '👕 Quần Áo'}
                </button>
              ))}
            </div>
            <button className="btn btn-primary btn-sm" onClick={() => { setEditProduct(null); setShowModal(true); }}>
              ➕ Thêm Sản Phẩm
            </button>
          </div>

          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Ảnh</th>
                  <th>Tên Sản Phẩm</th>
                  <th>Thương Hiệu</th>
                  <th>Loại</th>
                  <th>Giá</th>
                  <th>Tồn Kho</th>
                  <th>Thao Tác</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr><td colSpan={7} style={{ textAlign: 'center', padding: 40 }}><span className="loading-spinner"></span></td></tr>
                ) : products.length === 0 ? (
                  <tr><td colSpan={7} style={{ textAlign: 'center', padding: 40, color: 'var(--text-muted)' }}>Chưa có sản phẩm</td></tr>
                ) : products.map(p => (
                  <tr key={p.id}>
                    <td>
                      <img src={p.image_url || `https://picsum.photos/48/48?random=${p.id}`} alt={p.name} style={{ width: 48, height: 48, borderRadius: 8, objectFit: 'cover' }} onError={e => { e.target.src = `https://picsum.photos/48/48?random=${p.id + 5}`; }} />
                    </td>
                    <td style={{ fontWeight: 500, maxWidth: 200 }}>{p.name}</td>
                    <td style={{ color: 'var(--text-secondary)' }}>{p.brand}</td>
                    <td><span className={`badge badge-${p.category}`}>{p.category}</span></td>
                    <td style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent-primary)' }}>{formatPrice(p.price)}</td>
                    <td>
                      <span style={{ color: p.stock === 0 ? 'var(--danger)' : p.stock <= 5 ? 'var(--warning)' : 'var(--success)' }}>
                        {p.stock}
                      </span>
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: 8 }}>
                        <button className="btn btn-secondary btn-sm" onClick={() => { setEditProduct(p); setShowModal(true); }}>✏️</button>
                        <button className="btn btn-secondary btn-sm" onClick={() => setImportProduct(p)}>📦 Nhập Hàng</button>
                        <button className="btn btn-danger btn-sm" onClick={() => handleDelete(p.id)}>🗑️</button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 'recommendations' && (
        <div>
          <div className="page-header" style={{ paddingTop: 0 }}>
            <h2 className="page-title" style={{ fontSize: 24 }}>Đề xuất sản phẩm</h2>
            <p className="page-subtitle">Hiển thị các sản phẩm được AI xếp hạng theo tương tác người dùng</p>
          </div>
          {recommendations.length === 0 ? (
            <div className="card">Chưa có dữ liệu tương tác để tạo đề xuất.</div>
          ) : (
            <div className="product-grid">
              {recommendations.map(product => (
                <div key={`${product.type || 'mix'}-${product.id}`} className="card">
                  <div style={{ fontWeight: 700, marginBottom: 8 }}>{product.name}</div>
                  <div style={{ color: 'var(--text-secondary)', fontSize: 13 }}>{product.brand}</div>
                  <div style={{ marginTop: 8, fontFamily: 'var(--font-mono)' }}>{formatPrice(product.price)}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Orders Tab */}
      {activeTab === 'orders' && (
        <div>
          <div style={{ display: 'flex', gap: 8, marginBottom: 20, flexWrap: 'wrap' }}>
            {['all', ...STATUS_LIST].map(s => (
              <button key={s} className={`btn btn-sm ${statusFilter === s ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setStatusFilter(s)}>
                {s === 'all' ? 'Tất Cả' : STATUS_LABEL[s]}
              </button>
            ))}
          </div>

          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Mã ĐH</th>
                  <th>Khách Hàng</th>
                  <th>Ngày Đặt</th>
                  <th>Tổng Tiền</th>
                  <th>Trạng Thái</th>
                  <th>Thao Tác</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr><td colSpan={6} style={{ textAlign: 'center', padding: 40 }}><span className="loading-spinner"></span></td></tr>
                ) : filteredOrders.length === 0 ? (
                  <tr><td colSpan={6} style={{ textAlign: 'center', padding: 40, color: 'var(--text-muted)' }}>Không có đơn hàng</td></tr>
                ) : filteredOrders.map(order => (
                  <tr key={order.id}>
                    <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>#{order.id}</td>
                    <td>
                      <div style={{ fontWeight: 500 }}>{order.customer_name || `Customer #${order.customer_id}`}</div>
                      <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{order.customer_email}</div>
                    </td>
                    <td style={{ color: 'var(--text-secondary)', fontSize: 13 }}>{formatDate(order.created_at)}</td>
                    <td style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent-primary)', fontWeight: 600 }}>{formatPrice(order.total_amount)}</td>
                    <td><span className={`badge badge-${order.status}`}>{STATUS_LABEL[order.status] || order.status}</span></td>
                    <td>
                      <select
                        value={order.status}
                        onChange={e => handleStatusChange(order.id, e.target.value)}
                        className="form-input"
                        style={{ padding: '6px 10px', fontSize: 13, width: 'auto' }}
                      >
                        {STATUS_LIST.map(s => <option key={s} value={s}>{STATUS_LABEL[s]}</option>)}
                      </select>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {showModal && (
        <ProductModal
          product={editProduct}
          productType={productType}
          onClose={() => { setShowModal(false); setEditProduct(null); }}
          onSave={fetchProducts}
        />
      )}
      
      {importProduct && (
        <ImportModal
          product={importProduct}
          productType={productType}
          onClose={() => setImportProduct(null)}
          onSave={fetchProducts}
        />
      )}
    </div>
  );
}

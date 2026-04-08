import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../api';
import { useAuth } from '../context/AuthContext';

export default function LoginPage() {
  const [form, setForm] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [isStaff, setIsStaff] = useState(false);
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleChange = e => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async e => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const endpoint = isStaff ? '/api/auth/staff/login' : '/api/auth/login';
      const res = await api.post(endpoint, form);
      login(res.data);
      navigate(isStaff ? '/admin' : '/');
    } catch (err) {
      setError(err.response?.data?.error || 'Đăng nhập thất bại. Vui lòng thử lại.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '90vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24 }}>
      <div style={{ width: '100%', maxWidth: 420 }}>
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: 40 }}>
          <div style={{ fontSize: 48, marginBottom: 16 }}>⚡</div>
          <h1 style={{ fontFamily: 'var(--font-display)', fontSize: 28, fontWeight: 800, background: 'var(--accent-gradient)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text', marginBottom: 8 }}>
            Đăng Nhập
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: 15 }}>Chào mừng trở lại TechStore!</p>
        </div>

        {/* Toggle */}
        <div className="tabs" style={{ marginBottom: 28 }}>
          <button className={`tab ${!isStaff ? 'active' : ''}`} onClick={() => { setIsStaff(false); setError(''); }}>
            👤 Khách Hàng
          </button>
          <button className={`tab ${isStaff ? 'active' : ''}`} onClick={() => { setIsStaff(true); setError(''); }}>
            ⚙️ Quản Trị
          </button>
        </div>

        <div className="card">
          {error && <div className="error-message">{error}</div>}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Email</label>
              <input name="email" type="email" value={form.email} onChange={handleChange} required placeholder="example@email.com" className="form-input" />
            </div>
            <div className="form-group">
              <label className="form-label">Mật Khẩu</label>
              <input name="password" type="password" value={form.password} onChange={handleChange} required placeholder="••••••••" className="form-input" />
            </div>
            <button type="submit" className="btn btn-primary" style={{ width: '100%', height: 48, marginTop: 8 }} disabled={loading}>
              {loading ? <><span className="loading-spinner" style={{ width: 18, height: 18 }}></span> Đang đăng nhập...</> : 'Đăng Nhập →'}
            </button>
          </form>

          {!isStaff && (
            <p style={{ textAlign: 'center', marginTop: 20, color: 'var(--text-secondary)', fontSize: 14 }}>
              Chưa có tài khoản?{' '}
              <Link to="/register" style={{ color: 'var(--accent-primary)', fontWeight: 600 }}>Đăng ký ngay</Link>
            </p>
          )}
          {isStaff && (
            <div style={{ marginTop: 20, padding: '12px 16px', background: 'rgba(79, 70, 229, 0.08)', borderRadius: 8, fontSize: 12, color: 'var(--text-muted)' }}>
              <strong style={{ color: 'var(--text-secondary)' }}>Demo:</strong> admin@techstore.com / Admin@123456
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

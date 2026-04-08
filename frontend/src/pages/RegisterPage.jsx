import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../api';
import { useAuth } from '../context/AuthContext';

export default function RegisterPage() {
  const [form, setForm] = useState({ name: '', email: '', password: '', phone: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleChange = e => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async e => {
    e.preventDefault();
    setError('');
    if (form.password.length < 6) {
      setError('Mật khẩu phải có ít nhất 6 ký tự.');
      return;
    }
    setLoading(true);
    try {
      const res = await api.post('/api/auth/register', form);
      login(res.data);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.error || 'Đăng ký thất bại. Vui lòng thử lại.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '90vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24 }}>
      <div style={{ width: '100%', maxWidth: 440 }}>
        <div style={{ textAlign: 'center', marginBottom: 40 }}>
          <div style={{ fontSize: 48, marginBottom: 16 }}>🚀</div>
          <h1 style={{ fontFamily: 'var(--font-display)', fontSize: 28, fontWeight: 800, background: 'var(--accent-gradient)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text', marginBottom: 8 }}>
            Tạo Tài Khoản
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: 15 }}>Tham gia TechStore ngay hôm nay!</p>
        </div>

        <div className="card">
          {error && <div className="error-message">{error}</div>}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Họ và Tên</label>
              <input name="name" type="text" value={form.name} onChange={handleChange} required placeholder="Nguyễn Văn A" className="form-input" />
            </div>
            <div className="form-group">
              <label className="form-label">Email</label>
              <input name="email" type="email" value={form.email} onChange={handleChange} required placeholder="example@email.com" className="form-input" />
            </div>
            <div className="form-group">
              <label className="form-label">Mật Khẩu</label>
              <input name="password" type="password" value={form.password} onChange={handleChange} required placeholder="Tối thiểu 6 ký tự" className="form-input" />
            </div>
            <div className="form-group">
              <label className="form-label">Số Điện Thoại</label>
              <input name="phone" type="tel" value={form.phone} onChange={handleChange} placeholder="0901234567" className="form-input" />
            </div>
            <button type="submit" className="btn btn-primary" style={{ width: '100%', height: 48, marginTop: 8 }} disabled={loading}>
              {loading ? <><span className="loading-spinner" style={{ width: 18, height: 18 }}></span> Đang tạo...</> : '✨ Đăng Ký Ngay'}
            </button>
          </form>

          <p style={{ textAlign: 'center', marginTop: 20, color: 'var(--text-secondary)', fontSize: 14 }}>
            Đã có tài khoản?{' '}
            <Link to="/login" style={{ color: 'var(--accent-primary)', fontWeight: 600 }}>Đăng nhập</Link>
          </p>
        </div>
      </div>
    </div>
  );
}

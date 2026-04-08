import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useCart } from '../context/CartContext';

export default function Navbar() {
  const { user, isAdmin, logout } = useAuth();
  const { count } = useCart();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/');
    setMobileOpen(false);
  };

  const navStyle = {
    position: 'sticky',
    top: 0,
    zIndex: 100,
    background: 'rgba(255, 255, 255, 0.85)',
    backdropFilter: 'blur(20px)',
    borderBottom: '1px solid rgba(79, 70, 229, 0.1)',
    height: 64,
    display: 'flex',
    alignItems: 'center',
  };

  const logoStyle = {
    fontFamily: 'var(--font-display)',
    fontSize: 22,
    fontWeight: 800,
    background: 'var(--accent-gradient)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    backgroundClip: 'text',
    letterSpacing: '-0.5px',
  };

  const linkStyle = (path) => ({
    color: location.pathname === path ? 'var(--text-primary)' : 'var(--text-secondary)',
    fontSize: 14,
    fontWeight: 500,
    transition: 'color 0.2s',
    padding: '6px 12px',
    borderRadius: 6,
    background: location.pathname === path ? 'rgba(79, 70, 229, 0.1)' : 'transparent',
  });

  return (
    <nav style={navStyle}>
      <div className="container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
        <Link to="/" style={logoStyle}>⚡ TechStore</Link>

        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Link to="/" style={linkStyle('/')}>Trang Chủ</Link>

          {user && !isAdmin && (
            <>
              <Link to="/cart" style={{ ...linkStyle('/cart'), position: 'relative' }}>
                🛒 Giỏ Hàng
                {count > 0 && (
                  <span style={{
                    position: 'absolute',
                    top: -4,
                    right: -4,
                    background: 'var(--accent-gradient)',
                    color: 'white',
                    borderRadius: '50%',
                    width: 18,
                    height: 18,
                    fontSize: 10,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontWeight: 700,
                  }}>{count > 9 ? '9+' : count}</span>
                )}
              </Link>
              <Link to="/orders" style={linkStyle('/orders')}>Đơn Hàng</Link>
            </>
          )}

          {isAdmin && (
            <Link to="/admin" style={linkStyle('/admin')}>
              ⚙️ Quản Trị
            </Link>
          )}

          {user ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginLeft: 8 }}>
              <div style={{
                background: 'var(--bg-elevated)',
                border: '1px solid var(--border)',
                borderRadius: 20,
                padding: '6px 14px',
                fontSize: 13,
                color: 'var(--text-secondary)',
              }}>
                👤 {user.name || user.username}
              </div>
              <button
                onClick={handleLogout}
                className="btn btn-secondary btn-sm"
              >
                Đăng Xuất
              </button>
            </div>
          ) : (
            <div style={{ display: 'flex', gap: 8, marginLeft: 8 }}>
              <Link to="/login">
                <button className="btn btn-secondary btn-sm">Đăng Nhập</button>
              </Link>
              <Link to="/register">
                <button className="btn btn-primary btn-sm">Đăng Ký</button>
              </Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}

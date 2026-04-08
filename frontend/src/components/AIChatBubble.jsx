import React, { useEffect, useMemo, useState } from 'react';
import api from '../api';
import { useAuth } from '../context/AuthContext';

const STORAGE_KEY = 'techstore_chat_messages';

export default function AIChatBubble() {
  const { user } = useAuth();
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        setMessages(JSON.parse(stored));
      } catch {
        setMessages([]);
      }
    }
  }, []);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
  }, [messages]);

  const header = useMemo(
    () => (user?.name ? `Xin chào ${user.name}, mình có thể gợi ý gì?` : 'Hỏi mình để tìm sản phẩm phù hợp'),
    [user],
  );

  const sendMessage = async () => {
    const text = message.trim();
    if (!text) return;
    const userMessage = { role: 'user', text };
    setMessages(prev => [...prev, userMessage]);
    setMessage('');
    setLoading(true);
    try {
      const res = await api.post('/api/ai/chat', {
        message: text,
        customer_id: user?.customer_id || null,
      });
      setMessages(prev => [...prev, { role: 'assistant', text: res.data.answer || 'Mình chưa có phản hồi.' }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', text: 'Hệ thống AI đang tạm thời không phản hồi.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ position: 'fixed', right: 20, bottom: 20, zIndex: 1200 }}>
      {open && (
        <div style={{
          width: 360,
          height: 520,
          background: 'var(--bg-elevated)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 20,
          boxShadow: '0 24px 60px rgba(15, 23, 42, 0.18)',
          overflow: 'hidden',
          marginBottom: 12,
          display: 'flex',
          flexDirection: 'column',
        }}>
          <div style={{ padding: 16, background: 'var(--accent-gradient)', color: '#fff' }}>
            <div style={{ fontWeight: 700, fontSize: 15 }}>AI Shopping Assistant</div>
            <div style={{ fontSize: 12, opacity: 0.9, marginTop: 4 }}>{header}</div>
          </div>
          <div style={{ flex: 1, overflowY: 'auto', padding: 16, display: 'flex', flexDirection: 'column', gap: 10 }}>
            {messages.length === 0 ? (
              <div style={{ color: 'var(--text-muted)', fontSize: 13, lineHeight: 1.6 }}>
                Hỏi ví dụ: "Tôi cần laptop cho lập trình" hoặc "Tìm áo khoác dưới 1 triệu".
              </div>
            ) : messages.map((item, index) => (
              <div
                key={`${item.role}-${index}`}
                style={{
                  alignSelf: item.role === 'user' ? 'flex-end' : 'flex-start',
                  maxWidth: '90%',
                  background: item.role === 'user' ? 'rgba(79, 70, 229, 0.12)' : 'var(--bg-secondary)',
                  color: 'var(--text-primary)',
                  borderRadius: 14,
                  padding: '10px 12px',
                  fontSize: 13,
                  whiteSpace: 'pre-wrap',
                }}
              >
                {item.text}
              </div>
            ))}
            {loading && <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>Đang tìm gợi ý...</div>}
          </div>
          <div style={{ padding: 12, borderTop: '1px solid var(--border-subtle)', display: 'flex', gap: 8 }}>
            <input
              value={message}
              onChange={e => setMessage(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && sendMessage()}
              placeholder="Nhập nhu cầu của bạn..."
              className="form-input"
              style={{ flex: 1, height: 42 }}
            />
            <button className="btn btn-primary btn-sm" onClick={sendMessage} disabled={loading}>
              Gửi
            </button>
          </div>
        </div>
      )}
      <button className="btn btn-primary" onClick={() => setOpen(v => !v)} style={{ borderRadius: 999, padding: '14px 18px' }}>
        {open ? 'Đóng chat' : 'AI Chat'}
      </button>
    </div>
  );
}

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
  const quickPrompts = [
    'Tìm laptop học lập trình dưới 25 triệu',
    'Gợi ý điện thoại chụp ảnh đẹp',
    'Tôi đang cần thêm đồ liên quan đến giỏ hàng',
  ];

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
      setMessages(prev => [...prev, {
        role: 'assistant',
        text: res.data.answer || 'Mình chưa có phản hồi.',
        sources: res.data.sources || [],
        graphFacts: res.data.graph_facts || [],
      }]);
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
          background: 'linear-gradient(180deg, #fffaf2 0%, #ffffff 28%, #fff 100%)',
          border: '1px solid rgba(217, 119, 6, 0.16)',
          borderRadius: 24,
          boxShadow: '0 30px 90px rgba(15, 23, 42, 0.16)',
          overflow: 'hidden',
          marginBottom: 12,
          display: 'flex',
          flexDirection: 'column',
        }}>
          <div style={{ padding: 18, background: 'linear-gradient(135deg, #0f172a 0%, #1d4ed8 58%, #f59e0b 100%)', color: '#fff' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'center' }}>
              <div>
                <div style={{ fontWeight: 800, fontSize: 16, letterSpacing: 0.2 }}>TechStore AI Concierge</div>
                <div style={{ fontSize: 12, opacity: 0.9, marginTop: 4 }}>{header}</div>
              </div>
              <div style={{ fontSize: 11, padding: '6px 10px', borderRadius: 999, background: 'rgba(255,255,255,0.16)' }}>
                KB_Graph + RAG
              </div>
            </div>
          </div>
          <div style={{ padding: '12px 16px 0', display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            {quickPrompts.map(prompt => (
              <button
                key={prompt}
                type="button"
                onClick={() => setMessage(prompt)}
                style={{ border: '1px solid rgba(148, 163, 184, 0.35)', background: '#fff', borderRadius: 999, padding: '7px 12px', fontSize: 12, cursor: 'pointer', color: 'var(--text-secondary)' }}
              >
                {prompt}
              </button>
            ))}
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
                {item.sources?.length > 0 && (
                  <div style={{ marginTop: 10, display: 'grid', gap: 8 }}>
                    {item.sources.slice(0, 3).map(source => (
                      <div key={`${source.id}-${source.type || 'mix'}`} style={{ padding: '8px 10px', borderRadius: 12, background: '#fff', border: '1px solid rgba(148, 163, 184, 0.2)' }}>
                        <div style={{ fontWeight: 700, fontSize: 12 }}>{source.name}</div>
                        <div style={{ fontSize: 11, color: 'var(--text-secondary)', marginTop: 2 }}>{source.brand} • {source.category} • {source.price} đ</div>
                      </div>
                    ))}
                  </div>
                )}
                {item.graphFacts?.length > 0 && (
                  <div style={{ marginTop: 8, fontSize: 11, color: 'var(--text-muted)' }}>
                    Graph: {item.graphFacts.slice(0, 2).join(' | ')}
                  </div>
                )}
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
      <button className="btn btn-primary" onClick={() => setOpen(v => !v)} style={{ borderRadius: 999, padding: '14px 18px', boxShadow: '0 16px 40px rgba(245, 158, 11, 0.28)' }}>
        {open ? 'Đóng chat' : 'AI Chat'}
      </button>
    </div>
  );
}

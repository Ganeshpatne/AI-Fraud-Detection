import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageSquare, Send, Sparkles, Trash2, Loader2, X } from 'lucide-react';
import { chatQuery } from '../api.js';

const quickActions = [
  'Show system overview',
  'List high-risk users',
  'Show recent alerts',
  "What's the fraud rate?"
];

export default function ChatBot() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: 'bot', text: "Hello! I'm FraudShield AI assistant. Ask me anything about fraud detection, alerts, or transactions." }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesRef = useRef(null);

  useEffect(() => {
    if (messagesRef.current) {
      messagesRef.current.scrollTop = messagesRef.current.scrollHeight;
    }
  }, [messages]);

  const sendMessage = async (text) => {
    if (!text.trim()) return;
    const userMsg = { role: 'user', text: text.trim() };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await chatQuery(text.trim());
      setMessages(prev => [...prev, {
        role: 'bot',
        text: res.answer || 'I processed your request.'
      }]);
    } catch (e) {
      setMessages(prev => [...prev, {
        role: 'bot',
        text: `I'm having trouble connecting to the AI backend. Error: ${e.message}`
      }]);
    }
    setLoading(false);
  };

  const handleClear = () => {
    setMessages([
      { role: 'bot', text: "Conversation cleared. How can I help you?" }
    ]);
  };

  const showQuickActions = messages.length <= 2;

  return (
    <>
      {/* Trigger button */}
      <button className="chatbot-trigger" onClick={() => setOpen(!open)}
        style={{ transform: open ? 'rotate(90deg)' : 'none' }}>
        {open ? <X size={24} /> : <MessageSquare size={24} />}
      </button>

      {/* Panel */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: 20, opacity: 0 }}
            transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}
            className="chatbot-panel"
          >
            {/* Header */}
            <div style={{
              padding: '16px 20px', borderBottom: '1px solid var(--color-border)',
              display: 'flex', alignItems: 'center', gap: 12
            }}>
              <div style={{
                width: 40, height: 40, borderRadius: '50%',
                background: 'linear-gradient(135deg, #0077b6, #00b4d8)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                flexShrink: 0
              }}>
                <Sparkles size={20} color="white" />
              </div>
              <div style={{ flex: 1 }}>
                <p style={{ fontSize: '0.92rem', fontWeight: 600, color: 'var(--color-text)' }}>FraudShield AI</p>
                <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                  <span className="live-dot" style={{ width: 6, height: 6 }} />
                  <span style={{ fontSize: '0.7rem', color: '#10b981' }}>Online</span>
                </div>
              </div>
              <button onClick={handleClear} style={{
                background: 'var(--color-bg-raised)', border: 'none',
                borderRadius: 8, padding: 8, color: 'var(--color-muted)', cursor: 'pointer'
              }}>
                <Trash2 size={16} />
              </button>
            </div>

            {/* Messages */}
            <div ref={messagesRef} style={{
              flex: 1, overflow: 'auto', padding: '16px',
              display: 'flex', flexDirection: 'column', gap: 10
            }}>
              {messages.map((msg, i) => (
                <div key={i} className={msg.role === 'user' ? 'chat-message-user' : 'chat-message-bot'}>
                  {msg.text}
                </div>
              ))}
              {loading && (
                <div className="chat-message-bot" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Loader2 size={14} style={{ animation: 'spin 1s linear infinite' }} />
                  Analyzing...
                </div>
              )}
            </div>

            {/* Quick actions */}
            {showQuickActions && (
              <div style={{
                padding: '0 16px 12px',
                display: 'flex', flexWrap: 'wrap', gap: 6
              }}>
                {quickActions.map(qa => (
                  <button key={qa} onClick={() => sendMessage(qa)}
                    style={{
                      background: 'rgba(0,180,216,0.08)',
                      border: '1px solid rgba(0,180,216,0.2)',
                      borderRadius: 50, padding: '6px 14px',
                      color: '#00b4d8', fontSize: '0.75rem',
                      cursor: 'pointer', fontWeight: 500,
                      transition: 'background 0.2s'
                    }}>
                    {qa}
                  </button>
                ))}
              </div>
            )}

            {/* Input */}
            <div style={{
              padding: '12px 16px', borderTop: '1px solid var(--color-border)',
              position: 'relative'
            }}>
              <input value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter') sendMessage(input); }}
                placeholder="Ask about fraud patterns..."
                style={{
                  width: '100%', padding: '12px 48px 12px 16px',
                  borderRadius: 12, border: '1px solid var(--color-border)',
                  background: 'var(--color-bg-raised)', color: 'var(--color-text)',
                  fontSize: '0.85rem'
                }} />
              <button onClick={() => sendMessage(input)}
                disabled={!input.trim()}
                style={{
                  position: 'absolute', right: 24, top: '50%',
                  transform: 'translateY(-50%)',
                  width: 32, height: 32, borderRadius: 8,
                  background: input.trim()
                    ? 'linear-gradient(135deg, #0077b6, #00b4d8)'
                    : 'var(--color-bg-raised)',
                  border: 'none', cursor: input.trim() ? 'pointer' : 'not-allowed',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  color: 'white', transition: 'background 0.2s'
                }}>
                <Send size={14} />
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}

import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Send, Bot, User, X, MessageSquare, Loader2, Trash2, Sparkles } from 'lucide-react';

const ChatBot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [message, setMessage] = useState('');
  const [chatHistory, setChatHistory] = useState([
    { role: 'bot', content: 'Hello! I am FraudShield AI, your intelligent fraud investigation assistant. I can help you with transaction analysis, alerts, risk scores, and more. What would you like to know?' }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => `session_${Date.now()}`);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatHistory]);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!message.trim() || isLoading) return;

    const userMessage = message;
    setMessage('');
    setChatHistory(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await axios.post('http://localhost:8000/api/chatbot/query', {
        message: userMessage,
        session_id: sessionId
      });

      setChatHistory(prev => [...prev, { 
        role: 'bot', 
        content: response.data.answer,
        subQueries: response.data.sub_queries,
        isGreeting: response.data.is_greeting
      }]);
    } catch (error) {
      setChatHistory(prev => [...prev, { 
        role: 'bot', 
        content: 'Sorry, I encountered an error. Please make sure the backend is running and try again.' 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearHistory = async () => {
    try {
      await axios.delete(`http://localhost:8000/api/chatbot/history/${sessionId}`);
    } catch (e) {}
    setChatHistory([
      { role: 'bot', content: 'Conversation cleared. How can I help you with fraud investigation?' }
    ]);
  };

  const quickActions = [
    "Show system overview",
    "List high-risk users",
    "Show recent alerts",
    "What's the fraud rate?"
  ];

  return (
    <div style={{ position: 'fixed', bottom: '30px', right: '30px', zIndex: 1000 }}>
      {/* Floating Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          width: '60px',
          height: '60px',
          borderRadius: '50%',
          background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
          border: 'none',
          color: 'white',
          cursor: 'pointer',
          boxShadow: '0 8px 32px rgba(59, 130, 246, 0.4)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transition: 'all 0.3s ease',
          transform: isOpen ? 'rotate(90deg)' : 'rotate(0deg)'
        }}
        onMouseEnter={(e) => e.target.style.transform = isOpen ? 'rotate(90deg) scale(1.1)' : 'scale(1.1)'}
        onMouseLeave={(e) => e.target.style.transform = isOpen ? 'rotate(90deg)' : 'scale(1)'}
      >
        {isOpen ? <X size={26} /> : <MessageSquare size={26} />}
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div style={{
          position: 'absolute',
          bottom: '80px',
          right: '0',
          width: '400px',
          height: '580px',
          background: 'linear-gradient(180deg, rgba(15, 23, 42, 0.98), rgba(15, 23, 42, 0.95))',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255,255,255,0.08)',
          borderRadius: '20px',
          boxShadow: '0 25px 60px rgba(0,0,0,0.5)',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          animation: 'chatSlideUp 0.3s ease-out'
        }}>
          {/* Header */}
          <div style={{
            padding: '16px 20px',
            background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(139, 92, 246, 0.1))',
            borderBottom: '1px solid rgba(255,255,255,0.06)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '12px',
                background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <Sparkles size={20} color="#fff" />
              </div>
              <div>
                <h3 style={{ margin: 0, fontSize: '15px', fontWeight: '700', color: '#fff' }}>FraudShield AI</h3>
                <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                  <div style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: '#22c55e' }} />
                  <p style={{ margin: 0, fontSize: '11px', color: '#94a3b8' }}>Online</p>
                </div>
              </div>
            </div>
            <button
              onClick={handleClearHistory}
              style={{
                background: 'rgba(255,255,255,0.05)',
                border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: '8px',
                padding: '6px',
                color: '#94a3b8',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              title="Clear conversation"
            >
              <Trash2 size={14} />
            </button>
          </div>

          {/* Messages */}
          <div style={{
            flex: 1,
            overflowY: 'auto',
            padding: '16px',
            display: 'flex',
            flexDirection: 'column',
            gap: '12px'
          }}>
            {chatHistory.map((chat, index) => (
              <div key={index} style={{ alignSelf: chat.role === 'user' ? 'flex-end' : 'flex-start', maxWidth: '85%' }}>
                <div style={{ display: 'flex', gap: '8px', flexDirection: chat.role === 'user' ? 'row-reverse' : 'row', alignItems: 'flex-start' }}>
                  <div style={{
                    width: '28px',
                    height: '28px',
                    borderRadius: '50%',
                    background: chat.role === 'user'
                      ? 'linear-gradient(135deg, #3b82f6, #2563eb)'
                      : 'linear-gradient(135deg, #8b5cf6, #6d28d9)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0
                  }}>
                    {chat.role === 'user' ? <User size={13} color="#fff" /> : <Bot size={13} color="#fff" />}
                  </div>
                  <div style={{
                    padding: '10px 14px',
                    borderRadius: '14px',
                    fontSize: '13px',
                    lineHeight: '1.5',
                    backgroundColor: chat.role === 'user' ? '#3b82f6' : 'rgba(30, 41, 59, 0.8)',
                    color: chat.role === 'user' ? '#fff' : '#e2e8f0',
                    border: chat.role === 'user' ? 'none' : '1px solid rgba(255,255,255,0.06)',
                    borderTopRightRadius: chat.role === 'user' ? '3px' : '14px',
                    borderTopLeftRadius: chat.role === 'user' ? '14px' : '3px',
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word'
                  }}>
                    {chat.content}
                  </div>
                </div>
              </div>
            ))}
            {isLoading && (
              <div style={{ alignSelf: 'flex-start', display: 'flex', gap: '8px', alignItems: 'flex-start' }}>
                <div style={{
                  width: '28px', height: '28px', borderRadius: '50%',
                  background: 'linear-gradient(135deg, #8b5cf6, #6d28d9)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0
                }}>
                  <Bot size={13} color="#fff" />
                </div>
                <div style={{
                  backgroundColor: 'rgba(30, 41, 59, 0.8)',
                  border: '1px solid rgba(255,255,255,0.06)',
                  padding: '10px 14px',
                  borderRadius: '14px',
                  borderTopLeftRadius: '3px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  <Loader2 size={14} className="chatbot-spin" style={{ color: '#8b5cf6' }} />
                  <span style={{ fontSize: '13px', color: '#94a3b8' }}>Analyzing...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick Actions (shown when chat is mostly empty) */}
          {chatHistory.length <= 2 && !isLoading && (
            <div style={{ padding: '0 16px 8px', display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
              {quickActions.map((action, i) => (
                <button
                  key={i}
                  onClick={() => {
                    setMessage(action);
                    setTimeout(() => {
                      const form = document.querySelector('.chatbot-form');
                      if (form) form.dispatchEvent(new Event('submit', { bubbles: true }));
                    }, 100);
                  }}
                  style={{
                    fontSize: '11px',
                    padding: '5px 10px',
                    borderRadius: '20px',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    border: '1px solid rgba(59, 130, 246, 0.2)',
                    color: '#60a5fa',
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                >
                  {action}
                </button>
              ))}
            </div>
          )}

          {/* Input */}
          <form
            className="chatbot-form"
            onSubmit={handleSendMessage}
            style={{
              padding: '16px',
              background: 'rgba(30, 41, 59, 0.4)',
              borderTop: '1px solid rgba(255,255,255,0.06)'
            }}
          >
            <div style={{ position: 'relative' }}>
              <input
                ref={inputRef}
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Ask about transactions, alerts, users..."
                style={{
                  width: '100%',
                  backgroundColor: 'rgba(15, 23, 42, 0.8)',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '12px',
                  padding: '12px 48px 12px 16px',
                  fontSize: '13px',
                  color: '#fff',
                  outline: 'none',
                  transition: 'border-color 0.2s',
                  boxSizing: 'border-box'
                }}
                onFocus={(e) => e.target.style.borderColor = 'rgba(59, 130, 246, 0.5)'}
                onBlur={(e) => e.target.style.borderColor = 'rgba(255,255,255,0.1)'}
              />
              <button
                type="submit"
                disabled={isLoading || !message.trim()}
                style={{
                  position: 'absolute',
                  right: '8px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  width: '32px',
                  height: '32px',
                  borderRadius: '8px',
                  background: message.trim() ? 'linear-gradient(135deg, #3b82f6, #8b5cf6)' : 'transparent',
                  border: 'none',
                  color: message.trim() ? '#fff' : '#475569',
                  cursor: message.trim() ? 'pointer' : 'default',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  transition: 'all 0.2s'
                }}
              >
                <Send size={16} />
              </button>
            </div>
          </form>
        </div>
      )}

      <style>{`
        @keyframes chatSlideUp {
          from { opacity: 0; transform: translateY(20px) scale(0.95); }
          to { opacity: 1; transform: translateY(0) scale(1); }
        }
        .chatbot-spin { animation: chatSpin 1s linear infinite; }
        @keyframes chatSpin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default ChatBot;

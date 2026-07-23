import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Eye, EyeOff, LogIn, UserPlus } from 'lucide-react';
import { loginUser, registerUser, loginWithGoogle, loginWithGithub } from '../api.js';
import Logo from '../components/Logo.jsx';

export default function Login({ onLogin }) {
  const [isRegister, setIsRegister] = useState(false);
  const [showPw, setShowPw] = useState(false);
  const [form, setForm] = useState({ username: '', password: '', role: 'analyst' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // ─── Handle GitHub OAuth Callback ─────────────────────────────
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    if (code) {
      setLoading(true);
      setError('');
      // Clear code from URL bar
      window.history.replaceState({}, document.title, window.location.pathname);
      loginWithGithub(code)
        .then((result) => {
          onLogin(result);
        })
        .catch((err) => {
          setError(err.message || 'GitHub OAuth failed');
        })
        .finally(() => setLoading(false));
    }
  }, [onLogin]);

  // ─── Load Google Identity Services SDK ─────────────────────────
  useEffect(() => {
    const scriptId = 'google-gsi-script';
    if (!document.getElementById(scriptId)) {
      const script = document.createElement('script');
      script.id = scriptId;
      script.src = 'https://accounts.google.com/gsi/client';
      script.async = true;
      script.defer = true;
      document.head.appendChild(script);
    }
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const result = isRegister
        ? await registerUser(form)
        : await loginUser({ username: form.username, password: form.password });
      onLogin(result);
    } catch (err) {
      setError(err.message || 'Authentication failed');
    }
    setLoading(false);
  };

  const handleGoogleSSO = () => {
    setError('');
    const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID || '';
    if (!clientId) {
      setError('Google OAuth Client ID is missing. Add VITE_GOOGLE_CLIENT_ID or GOOGLE_CLIENT_ID to Infisical/env.');
      return;
    }

    if (window.google?.accounts?.id) {
      setLoading(true);
      window.google.accounts.id.initialize({
        client_id: clientId,
        callback: async (response) => {
          try {
            const result = await loginWithGoogle(response.credential);
            onLogin(result);
          } catch (err) {
            setError(err.message || 'Google Login failed');
          } finally {
            setLoading(false);
          }
        },
      });
      window.google.accounts.id.prompt((notification) => {
        if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
          // Fallback to explicit Google OAuth popup with current origin
          const redirectUri = window.location.origin;
          const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${clientId}&response_type=token&scope=email%20profile&redirect_uri=${encodeURIComponent(redirectUri)}`;
          const popup = window.open(authUrl, 'GoogleAuth', 'width=500,height=600');

          const checkPopup = setInterval(() => {
            if (popup && popup.closed) {
              clearInterval(checkPopup);
              setLoading(false);
            }
          }, 500);
        }
      });
    } else {
      setError('Google Sign-In SDK is loading. Please try again in a moment.');
    }
  };

  const handleGithubSSO = () => {
    setError('');
    const clientId = import.meta.env.VITE_GITHUB_CLIENT_ID || '';
    if (!clientId) {
      setError('GitHub OAuth Client ID is missing. Add VITE_GITHUB_CLIENT_ID or GITHUB_CLIENT_ID to Infisical/env.');
      return;
    }
    const redirectUri = `${window.location.origin}/login`;
    window.location.href = `https://github.com/login/oauth/authorize?client_id=${clientId}&scope=user:email&redirect_uri=${encodeURIComponent(redirectUri)}`;
  };

  const inputStyle = {
    width: '100%', padding: '12px 14px', borderRadius: 10,
    border: '1px solid var(--color-border)', background: 'var(--color-bg-raised)',
    color: 'var(--color-text)', fontSize: '0.9rem', outline: 'none',
    transition: 'border-color 0.2s'
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', background: 'var(--color-bg)' }}>
      {/* Left decorative panel */}
      <div className="login-left-panel" style={{
        flex: 1, background: 'linear-gradient(160deg, #0077b6, #00b4d8 60%, #0f1a2e)',
        display: 'flex', flexDirection: 'column', justifyContent: 'center',
        alignItems: 'center', padding: 48, position: 'relative'
      }}>
        <svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 30 30" fill="none" style={{ opacity: 0.3 }}>
          <path d="M15 2L4 7V15C4 21.3 8.9 27.2 15 28.5C21.1 27.2 26 21.3 26 15V7L15 2Z"
            stroke="#fff" strokeWidth="1.8" strokeLinejoin="round" fill="rgba(255,255,255,0.07)"/>
          <rect x="11" y="11" width="8" height="8" rx="1.5" stroke="#fff" strokeWidth="1.4"/>
        </svg>
        <p className="font-heading" style={{
          color: 'white', fontSize: 'clamp(1.4rem, 3vw, 2rem)',
          textAlign: 'center', marginTop: 32, maxWidth: 360
        }}>Zero-trust security for every transaction</p>
        <p style={{
          position: 'absolute', bottom: 24, left: 24,
          fontSize: '0.75rem', color: 'rgba(255,255,255,0.6)'
        }}>Developed by Ganesh Patne</p>
      </div>

      {/* Right: login form */}
      <div style={{
        flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center',
        padding: 24
      }}>
        <motion.div
          initial={{ opacity: 0, y: 32 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
          style={{
            background: 'var(--color-bg-card)', border: '1px solid var(--color-border)',
            borderRadius: 20, padding: 40, maxWidth: 400, width: '100%',
            boxShadow: '0 24px 64px rgba(0,0,0,0.5)'
          }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
            <Logo />
            <span className="font-heading" style={{ fontSize: '1.3rem', color: 'var(--color-text)' }}>FraudShield AI</span>
          </div>
          <p style={{ fontSize: '0.88rem', color: '#64748b', marginBottom: 28 }}>
            {isRegister ? 'Create your account' : 'Sign in to your account'}
          </p>

          {error && (
            <div style={{
              background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)',
              borderRadius: 10, padding: '10px 14px', marginBottom: 16,
              fontSize: '0.82rem', color: '#ef4444'
            }}>{error}</div>
          )}

          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: 16 }}>
              <label style={{ fontSize: '0.8rem', color: '#94a3b8', marginBottom: 6, display: 'block' }}>Username</label>
              <input style={inputStyle} value={form.username}
                onChange={e => setForm({ ...form, username: e.target.value })}
                placeholder="Enter username" required />
            </div>

            <div style={{ marginBottom: 16, position: 'relative' }}>
              <label style={{ fontSize: '0.8rem', color: '#94a3b8', marginBottom: 6, display: 'block' }}>Password</label>
              <input style={inputStyle} type={showPw ? 'text' : 'password'}
                value={form.password}
                onChange={e => setForm({ ...form, password: e.target.value })}
                placeholder="Enter password" required />
              <button type="button" onClick={() => setShowPw(!showPw)}
                style={{
                  position: 'absolute', right: 12, top: 34,
                  background: 'none', border: 'none', color: '#64748b',
                  cursor: 'pointer', padding: 4
                }}>
                {showPw ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>

            {isRegister && (
              <div style={{ marginBottom: 16 }}>
                <label style={{ fontSize: '0.8rem', color: '#94a3b8', marginBottom: 6, display: 'block' }}>Role</label>
                <select style={{ ...inputStyle, cursor: 'pointer' }} value={form.role}
                  onChange={e => setForm({ ...form, role: e.target.value })}>
                  <option value="analyst">Analyst</option>
                  <option value="admin">Admin</option>
                  <option value="viewer">Viewer</option>
                </select>
              </div>
            )}

            <button type="submit" disabled={loading} style={{
              width: '100%', padding: 13, borderRadius: 50,
              background: 'linear-gradient(135deg, #0077b6, #00b4d8)',
              color: 'white', fontWeight: 700, border: 'none',
              cursor: loading ? 'wait' : 'pointer',
              fontSize: '0.95rem', display: 'flex', alignItems: 'center',
              justifyContent: 'center', gap: 8, transition: 'filter 0.2s',
              opacity: loading ? 0.7 : 1
            }}>
              {isRegister ? <UserPlus size={18} /> : <LogIn size={18} />}
              {loading ? 'Processing...' : isRegister ? 'Create Account' : 'Sign In'}
            </button>
          </form>

          <div style={{ display: 'flex', alignItems: 'center', gap: 10, margin: '24px 0 16px' }}>
            <div style={{ flex: 1, height: 1, background: 'var(--color-border)' }} />
            <span style={{ fontSize: '0.75rem', color: 'var(--color-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Or continue with</span>
            <div style={{ flex: 1, height: 1, background: 'var(--color-border)' }} />
          </div>

          <div style={{ display: 'flex', gap: 12, marginBottom: 20 }}>
            <button type="button" onClick={handleGoogleSSO} style={{
              flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
              padding: '10px', borderRadius: 50, border: '1px solid var(--color-border)',
              background: 'var(--color-bg-card)', color: 'var(--color-text)', cursor: 'pointer',
              fontSize: '0.85rem', fontWeight: 600, transition: 'background 0.2s'
            }}
              onMouseEnter={e => e.currentTarget.style.background = 'var(--color-bg-raised)'}
              onMouseLeave={e => e.currentTarget.style.background = 'var(--color-bg-card)'}
            >
              <svg width="18" height="18" viewBox="0 0 18 18">
                <path d="M17.64 9.2c0-.63-.06-1.25-.16-1.84H9v3.47h4.84c-.21 1.12-.84 2.07-1.79 2.7v2.24h2.9c1.7-1.57 2.69-3.88 2.69-6.57z" fill="#4285F4"/>
                <path d="M9 18c2.43 0 4.47-.8 5.96-2.18l-2.9-2.24c-.8.54-1.84.87-3.06.87-2.35 0-4.34-1.58-5.05-3.72H.95v2.3C2.43 15.98 5.48 18 9 18z" fill="#34A853"/>
                <path d="M3.95 10.73A5.4 5.4 0 0 1 3.6 9c0-.6.1-1.2.27-1.77v-2.3H.95A8.99 8.99 0 0 0 0 9c0 1.62.43 3.14 1.18 4.47l2.77-2.3z" fill="#FBBC05"/>
                <path d="M9 3.58c1.32 0 2.5.45 3.44 1.35L15 2.4C13.46 1 11.43 0 9 0 5.48 0 2.43 2.02.95 4.97l2.77 2.3c.71-2.14 2.7-3.72 5.05-3.72z" fill="#EA4335"/>
              </svg>
              Google
            </button>
            <button type="button" onClick={handleGithubSSO} style={{
              flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
              padding: '10px', borderRadius: 50, border: '1px solid var(--color-border)',
              background: 'var(--color-bg-card)', color: 'var(--color-text)', cursor: 'pointer',
              fontSize: '0.85rem', fontWeight: 600, transition: 'background 0.2s'
            }}
              onMouseEnter={e => e.currentTarget.style.background = 'var(--color-bg-raised)'}
              onMouseLeave={e => e.currentTarget.style.background = 'var(--color-bg-card)'}
            >
              <svg width="18" height="18" viewBox="0 0 18 18" fill="currentColor">
                <path d="M9 0C4.03 0 0 4.03 0 9c0 3.98 2.58 7.35 6.16 8.54.45.08.61-.2.61-.43v-1.53c-2.5.54-3.03-1.2-3.03-1.2-.41-1.04-.99-1.32-.99-1.32-.82-.56.06-.55.06-.55.9.06 1.38.93 1.38.93.8 1.38 2.11.98 2.62.75.08-.58.31-.98.57-1.2-2-.23-4.1-1-4.1-4.45 0-.98.35-1.78.93-2.4-.09-.23-.4-1.14.09-2.37 0 0 .75-.24 2.46.92.71-.2 1.48-.3 2.25-.3.77 0 1.54.1 2.25.3 1.7-1.16 2.45-.92 2.45-.92.49 1.23.18 2.14.09 2.37.58.62.93 1.42.93 2.4 0 3.46-2.1 4.21-4.11 4.43.32.28.61.83.61 1.68v2.5c0 .24.16.52.62.43C15.42 16.35 18 12.98 18 9c0-4.97-4.03-9-9-9z"/>
              </svg>
              GitHub
            </button>
          </div>

          <p style={{ textAlign: 'center', marginTop: 20, fontSize: '0.82rem', color: '#64748b' }}>
            {isRegister ? 'Already have an account? ' : "Don't have an account? "}
            <button onClick={() => { setIsRegister(!isRegister); setError(''); }}
              style={{
                background: 'none', border: 'none', color: '#00b4d8',
                cursor: 'pointer', fontWeight: 600, fontSize: '0.82rem'
              }}>
              {isRegister ? 'Sign In' : 'Register'}
            </button>
          </p>
        </motion.div>
      </div>

      <style>{`
        .login-left-panel { display: none; }
        @media (min-width: 1024px) {
          .login-left-panel { display: flex !important; }
        }
      `}</style>
    </div>
  );
}

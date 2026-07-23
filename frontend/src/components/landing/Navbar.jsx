import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Menu, X, Sun, Moon } from 'lucide-react';
import Logo from '../Logo.jsx';

const navLinks = ['Features', 'How It Works', 'Stats', 'About Us'];

export default function Navbar({ isDark, onToggleTheme }) {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <>
      <nav className="navbar" style={{ padding: '0', transition: 'background 0.3s, border-color 0.3s' }}>
        <div style={{
          maxWidth: 1280, margin: '0 auto', padding: '16px 24px',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between'
        }}>
          {/* Left: Logo */}
          <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: 10, textDecoration: 'none' }}>
            <Logo />
            <span className="font-heading" style={{ fontSize: 18, color: 'var(--color-text)', transition: 'color 0.3s' }}>FraudShield AI</span>
          </Link>

          {/* Center: Nav links (desktop) */}
          <div style={{ display: 'flex', gap: 32, alignItems: 'center' }} className="hidden-mobile">
            {navLinks.map(link => (
              <a key={link} href={`#${link.toLowerCase().replace(/\s+/g, '-')}`}
                style={{
                  fontSize: '0.875rem', fontWeight: 500, color: 'var(--color-muted)',
                  textDecoration: 'none', transition: 'color 0.2s'
                }}
                onMouseEnter={e => e.target.style.color = 'var(--color-text)'}
                onMouseLeave={e => e.target.style.color = 'var(--color-muted)'}
              >{link}</a>
            ))}
          </div>

          {/* Right: Buttons (desktop) */}
          <div style={{ display: 'flex', gap: 12, alignItems: 'center' }} className="hidden-mobile">
            <button
              onClick={onToggleTheme}
              style={{
                background: 'transparent',
                border: '1px solid var(--color-border)',
                borderRadius: '50%',
                width: 38,
                height: 38,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--color-text)',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                outline: 'none',
              }}
              onMouseEnter={e => {
                e.currentTarget.style.background = 'var(--color-bg-raised)';
                e.currentTarget.style.borderColor = 'var(--color-accent)';
              }}
              onMouseLeave={e => {
                e.currentTarget.style.background = 'transparent';
                e.currentTarget.style.borderColor = 'var(--color-border)';
              }}
              title={isDark ? "Switch to Light Mode" : "Switch to Dark Mode"}
            >
              {isDark ? <Sun size={16} /> : <Moon size={16} />}
            </button>

            <Link to="/login" style={{
              background: 'var(--color-bg-card)', border: '1px solid var(--color-border)',
              color: 'var(--color-text)', borderRadius: 50, padding: '10px 20px',
              fontSize: '0.875rem', textDecoration: 'none', transition: 'all 0.2s ease'
            }}
              onMouseEnter={e => {
                e.target.style.background = 'var(--color-bg-raised)';
                e.target.style.borderColor = 'var(--color-accent)';
              }}
              onMouseLeave={e => {
                e.target.style.background = 'var(--color-bg-card)';
                e.target.style.borderColor = 'var(--color-border)';
              }}
            >Sign In</Link>
            
            <Link to="/login" style={{
              background: 'var(--color-accent)', color: '#ffffff', borderRadius: 50,
              padding: '10px 20px', fontWeight: 700, fontSize: '0.875rem',
              textDecoration: 'none', transition: 'filter 0.2s'
            }}
              onMouseEnter={e => e.target.style.filter = 'brightness(1.1)'}
              onMouseLeave={e => e.target.style.filter = 'none'}
            >Get Started Free</Link>
          </div>

          {/* Mobile right controls */}
          <div style={{ display: 'flex', gap: 12, alignItems: 'center' }} className="show-mobile">
            <button
              onClick={onToggleTheme}
              style={{
                background: 'transparent',
                border: '1px solid var(--color-border)',
                borderRadius: '50%',
                width: 36,
                height: 36,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--color-text)',
                cursor: 'pointer',
                outline: 'none',
              }}
            >
              {isDark ? <Sun size={15} /> : <Moon size={15} />}
            </button>

            <button onClick={() => setMobileOpen(true)}
              style={{ background: 'none', border: 'none', color: 'var(--color-text)', cursor: 'pointer', padding: 4 }}>
              <Menu size={24} />
            </button>
          </div>
        </div>
      </nav>

      {/* Mobile Sheet */}
      <AnimatePresence>
        {mobileOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              onClick={() => setMobileOpen(false)}
              style={{
                position: 'fixed', inset: 0, background: 'rgba(8,14,26,0.6)',
                backdropFilter: 'blur(4px)', zIndex: 60
              }}
            />
            <motion.div
              initial={{ x: '100%' }} animate={{ x: 0 }} exit={{ x: '100%' }}
              transition={{ ease: [0.22, 1, 0.36, 1], duration: 0.42 }}
              style={{
                position: 'fixed', right: 0, top: 0,
                width: 'min(85vw, 340px)', height: '100dvh',
                background: 'var(--color-bg-card)', borderLeft: '1px solid var(--color-border)',
                zIndex: 70, padding: '24px', display: 'flex', flexDirection: 'column',
                transition: 'background 0.3s, border-color 0.3s'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Logo />
                  <span className="font-heading" style={{ fontSize: 16, color: 'var(--color-text)' }}>FraudShield AI</span>
                </div>
                <button onClick={() => setMobileOpen(false)}
                  style={{ background: 'none', border: 'none', color: 'var(--color-text)', cursor: 'pointer' }}>
                  <X size={22} />
                </button>
              </div>

              <div style={{ height: 1, background: 'var(--color-border)', marginBottom: 24 }} />

              <div style={{ display: 'flex', flexDirection: 'column', gap: 8, flex: 1 }}>
                {navLinks.map((link, i) => (
                  <motion.a key={link}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.15 + i * 0.06, ease: [0.22, 1, 0.36, 1] }}
                    href={`#${link.toLowerCase().replace(/\s+/g, '-')}`}
                    onClick={() => setMobileOpen(false)}
                    style={{
                      fontSize: '1rem', color: 'var(--color-muted)', textDecoration: 'none',
                      padding: '12px 0', fontWeight: 500
                    }}
                  >{link}</motion.a>
                ))}
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 12, paddingTop: 24 }}>
                <Link to="/login" onClick={() => setMobileOpen(false)}
                  style={{
                    background: 'var(--color-bg-raised)', border: '1px solid var(--color-border)',
                    color: 'var(--color-text)', borderRadius: 50, padding: '12px',
                    textAlign: 'center', textDecoration: 'none', fontWeight: 500
                  }}>Sign In</Link>
                <Link to="/login" onClick={() => setMobileOpen(false)}
                  style={{
                    background: 'var(--color-accent)', color: '#ffffff', borderRadius: 50,
                    padding: '12px', textAlign: 'center', textDecoration: 'none', fontWeight: 700
                  }}>Get Started Free</Link>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
}

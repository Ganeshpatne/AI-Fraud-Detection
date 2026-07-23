import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { ShieldAlert, Zap, BrainCircuit, ArrowRightCircle } from 'lucide-react';

const fadeUp = {
  hidden: { opacity: 0, y: 30 },
  visible: (d = 0) => ({
    opacity: 1, y: 0,
    transition: { ease: [0.22, 1, 0.36, 1], duration: 0.65, delay: d }
  })
};

const alertRows = [
  { severity: 'critical', color: '#ef4444', label: 'CRITICAL', msg: 'Suspicious wire transfer — $12,400', time: '2s ago' },
  { severity: 'high', color: '#f59e0b', label: 'HIGH', msg: 'Unusual login location detected', time: '14s ago' },
  { severity: 'medium', color: '#00b4d8', label: 'MEDIUM', msg: 'Multiple failed auth attempts', time: '31s ago' },
];

export default function Hero() {
  return (
    <section className="hero-section" id="hero" style={{ transition: 'background 0.3s' }}>
      {/* Background effects */}
      <div className="hero-gradient-tl" />
      <div className="hero-gradient-br" />
      <div className="hero-grid-overlay" />
      <div className="hero-orb hero-orb-1" />
      <div className="hero-orb hero-orb-2" />
      <div className="hero-orb hero-orb-3" />

      <div style={{
        maxWidth: 1280, margin: '0 auto', padding: '0 24px',
        paddingTop: 'clamp(100px, 10vw, 120px)',
        paddingBottom: 'clamp(60px, 8vw, 100px)',
        position: 'relative', zIndex: 2,
        display: 'grid', gridTemplateColumns: '1fr', gap: 48, alignItems: 'center'
      }} className="hero-grid">
        {/* Left content */}
        <div style={{ maxWidth: 640 }}>
          {/* Badge */}
          <motion.div variants={fadeUp} initial="hidden" animate="visible" custom={0}
            style={{
              display: 'inline-flex', alignItems: 'center', gap: 8,
              border: '1px solid var(--color-border)', background: 'var(--color-bg-raised)',
              borderRadius: 50, padding: '6px 14px', marginBottom: 28
            }}>
            <span className="live-dot-sm" />
            <span style={{ fontSize: '0.78rem', color: 'var(--color-accent)', fontWeight: 600 }}>
              Live Fraud Detection · AI-Powered
            </span>
          </motion.div>

          {/* Heading */}
          <motion.h1 variants={fadeUp} initial="hidden" animate="visible" custom={0.1}
            className="font-heading" style={{
              fontSize: 'clamp(2.2rem, 6vw, 4rem)', lineHeight: 1.1,
              letterSpacing: '-0.02em', color: 'var(--color-text)', marginBottom: 24,
              transition: 'color 0.3s'
            }}>
            Detect Fraud Before It Strikes
            <br className="hidden-mobile" />
            <span style={{ color: 'var(--color-accent)' }}> — Powered by AI</span>
          </motion.h1>

          {/* Subtext */}
          <motion.p variants={fadeUp} initial="hidden" animate="visible" custom={0.25}
            style={{
              fontSize: 'clamp(0.95rem, 2.5vw, 1.15rem)', lineHeight: 1.7,
              color: 'var(--color-muted)', maxWidth: 520, marginBottom: 32,
              transition: 'color 0.3s'
            }}>
            FraudShield AI monitors every transaction in real time, flags suspicious activity with
            94%+ accuracy, and gives your team instant, explainable alerts — so fraud never gets a second chance.
          </motion.p>

          {/* CTA buttons */}
          <motion.div variants={fadeUp} initial="hidden" animate="visible" custom={0.4}
            style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
            <Link to="/login" style={{
              background: 'var(--color-accent)', color: '#ffffff', borderRadius: 50,
              padding: '16px 28px', fontWeight: 700,
              fontSize: 'clamp(0.9rem, 2vw, 1rem)',
              boxShadow: '0 4px 24px rgba(0,119,182,0.3)',
              minWidth: 210, display: 'flex', justifyContent: 'space-between',
              alignItems: 'center', gap: 28, textDecoration: 'none',
              transition: 'transform 0.2s, filter 0.2s'
            }}
              onMouseEnter={e => e.target.style.filter = 'brightness(1.1)'}
              onMouseLeave={e => e.target.style.filter = 'none'}
            >
              Start For Free <ArrowRightCircle size={20} />
            </Link>
          </motion.div>

          {/* Trust line */}
          <motion.p variants={fadeUp} initial="hidden" animate="visible" custom={0.5}
            style={{ fontSize: '0.78rem', color: 'var(--color-muted)', marginTop: 20 }}>
            Trusted by 200+ fraud analysts · No credit card required
          </motion.p>
        </div>

        {/* Right: floating dashboard preview (desktop only) */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
          className="hero-preview-card"
          style={{
            background: 'var(--color-bg-card)', border: '1px solid var(--color-border)',
            borderRadius: 16, padding: 24,
            boxShadow: '0 32px 80px rgba(0,0,0,0.15)',
            animation: 'float-slow 6s ease-in-out infinite',
            transform: 'perspective(1200px) rotateY(-8deg) rotateX(3deg)',
            transition: 'background 0.3s, border-color 0.3s'
          }}>
          {/* Live pill */}
          <div style={{
            display: 'inline-flex', alignItems: 'center', gap: 6,
            background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.3)',
            borderRadius: 50, padding: '4px 12px', marginBottom: 16
          }}>
            <span className="live-dot" />
            <span style={{ fontSize: '0.72rem', color: '#10b981', fontWeight: 600 }}>LIVE</span>
          </div>
          <div style={{ fontSize: '0.82rem', color: 'var(--color-muted)', fontWeight: 600, marginBottom: 12 }}>
            Recent Alerts
          </div>
          {alertRows.map((a, i) => (
            <div key={i} style={{
              display: 'flex', alignItems: 'center', gap: 10, padding: '10px 0',
              borderBottom: i < 2 ? '1px solid var(--color-border)' : 'none'
            }}>
              <span style={{
                width: 8, height: 8, borderRadius: '50%', background: a.color, flexShrink: 0
              }} />
              <span style={{
                fontSize: '0.72rem', fontWeight: 700, padding: '2px 8px',
                borderRadius: 4, background: `${a.color}22`, color: a.color,
              }}>{a.label}</span>
              <span style={{ fontSize: '0.8rem', color: 'var(--color-text)', flex: 1 }}>{a.msg}</span>
              <span style={{ fontSize: '0.7rem', color: 'var(--color-muted)' }}>{a.time}</span>
            </div>
          ))}
        </motion.div>
      </div>

      {/* Extra CSS for hero grid */}
      <style>{`
        .hero-grid { grid-template-columns: 1fr !important; }
        .hero-preview-card { display: none; }
        .hidden-mobile { display: none !important; }
        .show-mobile { display: block !important; }
        @media (min-width: 768px) {
          .hidden-mobile { display: flex !important; }
          .show-mobile { display: none !important; }
        }
        @media (min-width: 1024px) {
          .hero-grid { grid-template-columns: 1fr 1fr !important; }
          .hero-preview-card { display: block !important; }
        }
      `}</style>
    </section>
  );
}

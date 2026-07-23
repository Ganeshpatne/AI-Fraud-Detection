import React from 'react';
import { motion } from 'framer-motion';
import { LayoutDashboard, Bell, FlaskConical, FileText, Database, Search } from 'lucide-react';
import { Link } from 'react-router-dom';

const fadeUp = {
  hidden: { opacity: 0, y: 28 },
  visible: (d = 0) => ({
    opacity: 1, y: 0,
    transition: { ease: [0.22, 1, 0.36, 1], duration: 0.6, delay: d }
  })
};

const features = [
  { icon: LayoutDashboard, path: '/app/dashboard', title: 'Real-Time Dashboard', desc: 'Live metrics: fraud rate, risk scores, hourly patterns, location heatmaps — all updating every 3 seconds.' },
  { icon: Bell, path: '/app/alerts', title: 'Live Alert Feed', desc: 'Instant WebSocket-powered alerts the moment fraud is detected. Critical, High, and Medium severity tiers.' },
  { icon: FlaskConical, path: '/app/simulation', title: 'Fraud Simulation', desc: 'Test any transaction scenario and get instant AI risk predictions before going live.' },
  { icon: FileText, path: '/app/reports', title: 'Investigation Reports', desc: 'One-click PDF generation for any flagged transaction — audit-ready and shareable in seconds.' },
  { icon: Database, path: '/app/upload', title: 'Dataset Manager', desc: 'Upload custom CSV datasets, select fraud domain, and retrain the ML model without writing a single line of code.' },
  { icon: Search, path: '/app/transactions', title: 'Transaction Explorer', desc: 'Instantly search, filter, and review historical transactions with detailed AI risk profiles and behavioral analysis.' },
];

export default function Features() {
  return (
    <section id="features" style={{ background: 'var(--color-bg)', padding: 'clamp(80px,10vw,120px) 24px', transition: 'background 0.3s' }}>
      <div style={{ maxWidth: 1280, margin: '0 auto', textAlign: 'center' }}>
        <motion.p initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }}
          style={{
            fontSize: '0.72rem', letterSpacing: '0.14em', color: 'var(--color-accent)',
            fontWeight: 600, textTransform: 'uppercase', marginBottom: 16
          }}>CORE CAPABILITIES</motion.p>

        <motion.h2 initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }} transition={{ ease: [0.22, 1, 0.36, 1], duration: 0.6 }}
          className="font-heading" style={{
            fontSize: 'clamp(1.8rem, 4vw, 2.8rem)', color: 'var(--color-text)', marginBottom: 16,
            transition: 'color 0.3s'
          }}>Everything Your Fraud Team Needs</motion.h2>

        <motion.p initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }} transition={{ delay: 0.1, ease: [0.22, 1, 0.36, 1], duration: 0.6 }}
          style={{
            color: 'var(--color-muted)', maxWidth: 560, margin: '0 auto 56px',
            fontSize: '0.95rem', lineHeight: 1.7, transition: 'color 0.3s'
          }}>
          From real-time transaction monitoring to AI-generated investigation reports — FraudShield AI covers your full detection pipeline.
        </motion.p>

        <div style={{
          display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '1.5rem', maxWidth: 1280
        }}>
          {features.map((f, i) => (
            <motion.div key={f.title}
              variants={fadeUp} initial="hidden" whileInView="visible"
              viewport={{ once: true }} custom={i * 0.08}
              style={{ display: 'flex' }}
            >
              <Link to={f.path} className="card card-hover"
                style={{ 
                   display: 'flex', flexDirection: 'column', padding: '28px 24px', 
                   textAlign: 'left', borderRadius: 16, textDecoration: 'none', width: '100%',
                   background: 'var(--color-bg-card)', border: '1px solid var(--color-border)',
                   transition: 'background 0.3s, border-color 0.3s, transform 0.3s, box-shadow 0.3s'
                }}
                onMouseEnter={e => {
                  e.currentTarget.style.borderColor = 'var(--color-accent)';
                  e.currentTarget.style.transform = 'translateY(-4px)';
                  e.currentTarget.style.boxShadow = '0 16px 40px rgba(0,0,0,0.1)';
                }}
                onMouseLeave={e => {
                  e.currentTarget.style.borderColor = 'var(--color-border)';
                  e.currentTarget.style.transform = 'none';
                  e.currentTarget.style.boxShadow = 'none';
                }}
              >
                <div className="feature-icon-circle" style={{ marginBottom: 'auto' }}>
                  <f.icon size={22} />
                </div>
                <h3 className="font-heading" style={{
                  fontSize: '1.05rem', color: 'var(--color-text)', margin: '16px 0 8px',
                  transition: 'color 0.3s'
                }}>{f.title}</h3>
                <p style={{ fontSize: '0.88rem', lineHeight: 1.65, color: 'var(--color-muted)', margin: 0, transition: 'color 0.3s' }}>{f.desc}</p>
              </Link>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

import React, { useEffect, useRef, useState } from 'react';
import { motion, useInView } from 'framer-motion';
import { Target, Zap, Activity, Globe } from 'lucide-react';

const stats = [
  { value: 94.2, suffix: '%', label: 'Detection Accuracy', icon: Target },
  { value: 50, prefix: '<', suffix: 'ms', label: 'Avg. Response Time', icon: Zap },
  { value: 500, suffix: 'K+', label: 'Transactions Analyzed', icon: Activity },
  { value: 12, suffix: '+', label: 'Fraud Domains Supported', icon: Globe },
];

function CountUp({ target, suffix = '', prefix = '', duration = 2000 }) {
  const [count, setCount] = useState(0);
  const ref = useRef(null);
  const inView = useInView(ref, { once: true });

  useEffect(() => {
    if (!inView) return;
    let start = 0;
    const step = target / (duration / 16);
    const timer = setInterval(() => {
      start += step;
      if (start >= target) {
        setCount(target);
        clearInterval(timer);
      } else {
        setCount(Math.floor(start * 10) / 10);
      }
    }, 16);
    return () => clearInterval(timer);
  }, [inView, target, duration]);

  const display = Number.isInteger(target) ? Math.round(count) : count.toFixed(1);
  return <span ref={ref}>{prefix}{display}{suffix}</span>;
}

export default function Stats() {
  return (
    <section id="stats" style={{
      position: 'relative',
      background: 'var(--color-bg)',
      padding: 'clamp(80px, 10vw, 120px) 24px',
      borderTop: '1px solid var(--color-border)',
      borderBottom: '1px solid var(--color-border)',
      overflow: 'hidden',
      transition: 'background 0.3s, border-color 0.3s'
    }}>
      {/* Background flare */}
      <div style={{
        position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)',
        width: '100%', maxWidth: 800, height: 400,
        background: 'radial-gradient(ellipse at center, rgba(0,180,216,0.06) 0%, transparent 70%)',
        pointerEvents: 'none'
      }} />

      <div style={{
        maxWidth: 1280, margin: '0 auto', position: 'relative', zIndex: 2,
        display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
        gap: '2rem'
      }}>
        {stats.map((s, i) => (
          <motion.div key={s.label}
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.15, ease: [0.22, 1, 0.36, 1], duration: 0.7 }}
            style={{
              background: 'var(--color-bg-card)',
              border: '1px solid var(--color-border)',
              borderRadius: 20, padding: '32px 24px',
              textAlign: 'center', backdropFilter: 'blur(10px)',
              boxShadow: '0 10px 40px rgba(0,0,0,0.05)',
              position: 'relative', overflow: 'hidden',
              transition: 'background 0.3s, border-color 0.3s, transform 0.3s'
            }}
            onMouseEnter={e => {
              e.currentTarget.style.borderColor = 'var(--color-accent)';
              e.currentTarget.style.background = 'var(--color-bg-raised)';
            }}
            onMouseLeave={e => {
              e.currentTarget.style.borderColor = 'var(--color-border)';
              e.currentTarget.style.background = 'var(--color-bg-card)';
            }}
          >
            {/* Top accent line */}
            <div style={{
              position: 'absolute', top: 0, left: 0, width: '100%', height: 2,
              background: 'linear-gradient(90deg, transparent, var(--color-accent), transparent)'
            }} />

            <div style={{
              width: 48, height: 48, borderRadius: 12,
              background: 'rgba(0,180,216,0.1)', margin: '0 auto 20px',
              display: 'flex', alignItems: 'center', justifyContent: 'center'
            }}>
              <s.icon size={24} style={{ color: 'var(--color-accent)' }} />
            </div>

            <div className="font-heading" style={{
              fontSize: 'clamp(2.2rem, 4vw, 3rem)', color: 'var(--color-text)',
              lineHeight: 1, marginBottom: 12, transition: 'color 0.3s'
            }}>
              <CountUp target={s.value} suffix={s.suffix} prefix={s.prefix || ''} />
            </div>
            <p style={{ fontSize: '0.9rem', color: 'var(--color-muted)', fontWeight: 500, transition: 'color 0.3s' }}>{s.label}</p>
          </motion.div>
        ))}
      </div>
    </section>
  );
}

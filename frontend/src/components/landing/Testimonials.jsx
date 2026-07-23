import React from 'react';
import { motion } from 'framer-motion';

const testimonials = [
  {
    quote: 'FraudShield cut our false positive rate by 40%. The AI explainer alone saved our team hours of manual investigation every week.',
    name: 'Priya Sharma',
    role: 'Senior Fraud Analyst, FinSecure'
  },
  {
    quote: 'The live alert feed is incredible. We used to find out about fraud the next morning — now we know in real time.',
    name: 'Daniel Okonkwo',
    role: 'Risk Officer, PayBridge Africa'
  },
  {
    quote: 'Being able to upload our own dataset and retrain the model without engineering support changed everything for us.',
    name: 'Kenji Watanabe',
    role: 'Head of Compliance, NeoBank Japan'
  },
];

export default function Testimonials() {
  return (
    <section style={{ background: 'var(--color-bg)', padding: 'clamp(80px,10vw,120px) 24px', transition: 'background 0.3s' }}>
      <div style={{ maxWidth: 1280, margin: '0 auto', textAlign: 'center' }}>
        <motion.h2 initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }} transition={{ ease: [0.22, 1, 0.36, 1], duration: 0.6 }}
          className="font-heading" style={{
            fontSize: 'clamp(1.8rem, 4vw, 2.8rem)', color: 'var(--color-text)', marginBottom: 56,
            transition: 'color 0.3s'
          }}>What Analysts Say</motion.h2>

        <div style={{
          display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '1.5rem'
        }}>
          {testimonials.map((t, i) => (
            <motion.div key={t.name}
              initial={{ opacity: 0, y: 28 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1, ease: [0.22, 1, 0.36, 1], duration: 0.6 }}
              className="card" style={{
                padding: 28, textAlign: 'left', borderRadius: 16, position: 'relative',
                background: 'var(--color-bg-card)', border: '1px solid var(--color-border)',
                transition: 'background 0.3s, border-color 0.3s'
              }}>
              <span className="font-heading" style={{
                fontSize: '3rem', color: 'rgba(0,180,216,0.15)',
                position: 'absolute', top: 16, left: 24, lineHeight: 1
              }}>"</span>
              <p style={{
                fontSize: '0.92rem', lineHeight: 1.7, color: 'var(--color-text)',
                fontStyle: 'italic', marginTop: 28, marginBottom: 20, transition: 'color 0.3s'
              }}>{t.quote}</p>
              <p style={{ fontSize: '0.9rem', color: 'var(--color-text)', fontWeight: 600, transition: 'color 0.3s' }}>{t.name}</p>
              <p style={{ fontSize: '0.78rem', color: 'var(--color-muted)', transition: 'color 0.3s' }}>{t.role}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

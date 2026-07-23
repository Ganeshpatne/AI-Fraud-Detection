import React from 'react';
import { motion } from 'framer-motion';
import { Upload, ScanLine, ShieldCheck } from 'lucide-react';

const steps = [
  { num: '1', icon: Upload, title: 'Ingest Your Data', desc: 'Upload any transaction CSV or connect your live data stream. FraudShield auto-detects schema and trains on your fraud domain.' },
  { num: '2', icon: ScanLine, title: 'AI Scans Every Transaction', desc: 'Our hybrid engine — rule-based checks, Isolation Forest anomaly detection, and XGBoost ML — scores every transaction in milliseconds.' },
  { num: '3', icon: ShieldCheck, title: 'Instant Alert & Report', desc: 'Fraud is flagged, an alert fires to your team, and a PDF investigation report is generated automatically.' },
];

export default function HowItWorks() {
  return (
    <section id="how-it-works" style={{ background: 'var(--color-bg-raised)', padding: 'clamp(80px,10vw,120px) 24px', transition: 'background 0.3s' }}>
      <div style={{ maxWidth: 960, margin: '0 auto', textAlign: 'center' }}>
        <motion.p initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }}
          style={{
            fontSize: '0.72rem', letterSpacing: '0.14em', color: 'var(--color-accent)',
            fontWeight: 600, textTransform: 'uppercase', marginBottom: 16
          }}>HOW IT WORKS</motion.p>

        <motion.h2 initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }} transition={{ ease: [0.22, 1, 0.36, 1], duration: 0.6 }}
          className="font-heading" style={{
            fontSize: 'clamp(1.8rem, 4vw, 2.8rem)', color: 'var(--color-text)', marginBottom: 56,
            transition: 'color 0.3s'
          }}>Fraud Caught in 3 Steps</motion.h2>

        <div className="steps-row">
          {steps.map((s, i) => (
            <React.Fragment key={s.num}>
              {i > 0 && <div className="step-connector" />}
              <motion.div
                initial={{ opacity: 0, y: 28 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.15, ease: [0.22, 1, 0.36, 1], duration: 0.6 }}
                style={{ flex: 1, textAlign: 'center', padding: '0 16px' }}>
                {/* Premium Icon Wrapper */}
                <div style={{
                  width: 64, height: 64, borderRadius: 16,
                  background: 'var(--color-bg-card)',
                  border: '1px solid var(--color-border)',
                  boxShadow: '0 8px 32px rgba(0, 180, 216, 0.1)',
                  margin: '0 auto 24px',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  transform: 'rotate(-3deg)',
                  transition: 'background 0.3s, border-color 0.3s'
                }}>
                  <s.icon size={32} style={{ color: 'var(--color-accent)', transform: 'rotate(3deg)', transition: 'color 0.3s' }} />
                </div>
                
                {/* Title */}
                <h3 className="font-heading" style={{ fontSize: '1.1rem', color: 'var(--color-text)', marginBottom: 12, transition: 'color 0.3s' }}>
                  {s.title}
                </h3>
                <p style={{ fontSize: '0.85rem', color: 'var(--color-muted)', lineHeight: 1.65, transition: 'color 0.3s' }}>{s.desc}</p>
              </motion.div>
            </React.Fragment>
          ))}
        </div>
      </div>

      <style>{`
        .steps-row {
          display: flex;
          flex-direction: column;
          gap: 32px;
          align-items: center;
        }
        .step-connector {
          width: 2px;
          height: 40px;
          border-left: 2px dashed var(--color-border);
        }
        @media (min-width: 768px) {
          .steps-row {
            flex-direction: row;
            align-items: flex-start;
            gap: 0;
          }
          .step-connector {
            width: auto;
            height: auto;
            border-left: none;
            border-top: 2px dashed var(--color-border);
            flex: 0 0 40px;
            margin-top: 20px;
          }
        }
      `}</style>
    </section>
  );
}

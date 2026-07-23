import React from 'react';
import { motion } from 'framer-motion';
import { Linkedin, Code2, GraduationCap, Briefcase, Award } from 'lucide-react';

export default function AboutDeveloper() {
  return (
    <section id="about-us" style={{
      position: 'relative',
      background: 'var(--color-bg-raised)',
      padding: 'clamp(50px, 6vw, 70px) 24px',
      borderTop: '1px solid var(--color-border)',
      borderBottom: '1px solid var(--color-border)',
      overflow: 'hidden',
      transition: 'background 0.3s, border-color 0.3s'
    }}>
      {/* Glow effect matching uideck preview style */}
      <div style={{
        position: 'absolute', top: '10%', right: '-10%', width: 500, height: 500,
        background: 'radial-gradient(circle, rgba(99,102,241,0.08) 0%, transparent 70%)',
        pointerEvents: 'none', zIndex: 1
      }} />

      <div style={{ maxWidth: 1000, margin: '0 auto', position: 'relative', zIndex: 2 }}>
        <div style={{ textAlign: 'center', marginBottom: 56 }}>
          <motion.p initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }}
            style={{
              fontSize: '0.72rem', letterSpacing: '0.14em', color: 'var(--color-accent)',
              fontWeight: 600, textTransform: 'uppercase', marginBottom: 16
            }}>THE CREATOR</motion.p>

          <motion.h2 initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }} transition={{ ease: [0.22, 1, 0.36, 1], duration: 0.6 }}
            className="font-heading" style={{
              fontSize: 'clamp(1.8rem, 4vw, 2.8rem)', color: 'var(--color-text)', marginBottom: 16
            }}>Meet the Architect</motion.h2>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 32 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
          style={{
            background: 'var(--color-bg-card)',
            border: '1px solid var(--color-border)',
            borderRadius: 24,
            padding: 'clamp(24px, 5vw, 48px)',
            boxShadow: '0 20px 50px rgba(0,0,0,0.06)',
            display: 'grid',
            gridTemplateColumns: '1fr',
            gap: 40,
            alignItems: 'center',
            transition: 'background 0.3s, border-color 0.3s'
          }}
          className="dev-grid"
        >
          {/* Left Panel: Profile Info */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 20, marginBottom: 28 }}>
              {/* Avatar circle with glow */}
              <div style={{
                width: 80, height: 80, borderRadius: '50%',
                background: 'linear-gradient(135deg, var(--color-accent), var(--color-accent-2))',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                boxShadow: '0 8px 30px rgba(99,102,241,0.3)', color: '#fff',
                fontSize: '2rem', fontWeight: 700
              }}>
                GP
              </div>
              <div>
                <h3 className="font-heading" style={{ fontSize: '1.4rem', color: 'var(--color-text)', margin: 0 }}>
                  Ganesh Patne
                </h3>
                <p style={{ fontSize: '0.9rem', color: 'var(--color-accent)', fontWeight: 500, margin: '4px 0 0' }}>
                  Backend Developer Intern
                </p>
              </div>
            </div>

            <p style={{
              fontSize: '0.98rem', lineHeight: 1.7, color: 'var(--color-text)',
              opacity: 0.85, marginBottom: 28
            }}>
              Pursuing a Bachelor of Engineering in Information Technology from Shah and Anchor Kutchhi Engineering College, Mumbai University (graduating in 2026). 
              Ganesh specializes in architecting high-performance backend layers, building automated document workflows, and training machine learning anomaly engines to keep financial platforms secure.
            </p>

            {/* Quick Details List */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16, marginBottom: 32 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <Briefcase size={18} color="var(--color-accent)" />
                <span style={{ fontSize: '0.88rem', color: 'var(--color-text)' }}>
                  Backend Developer Intern at <strong>Home First Finance Company (HFFC)</strong>
                </span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <GraduationCap size={18} color="var(--color-accent)" />
                <span style={{ fontSize: '0.88rem', color: 'var(--color-text)' }}>
                  IT Undergraduate, Mumbai University · 2026 Cohort
                </span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <Award size={18} color="var(--color-accent)" />
                <span style={{ fontSize: '0.88rem', color: 'var(--color-text)' }}>
                  Designed AI routing layers & real-time analytics architectures
                </span>
              </div>
            </div>

            {/* LinkedIn Button CTA */}
            <a
              href="https://www.linkedin.com/in/ganesh-patne"
              target="_blank"
              rel="noopener noreferrer"
              style={{
                display: 'inline-flex', alignItems: 'center', gap: 10,
                background: 'var(--color-accent)', color: '#ffffff', borderRadius: 50,
                padding: '14px 28px', fontWeight: 700, textDecoration: 'none',
                boxShadow: '0 4px 20px rgba(99,102,241,0.25)', transition: 'all 0.2s ease'
              }}
              onMouseEnter={e => e.currentTarget.style.filter = 'brightness(1.1)'}
              onMouseLeave={e => e.currentTarget.style.filter = 'none'}
            >
              <Linkedin size={18} /> Connect on LinkedIn
            </a>
          </div>

          {/* Right Panel: Technical Skills Showcase */}
          <div style={{
            background: 'var(--color-bg-raised)', border: '1px solid var(--color-border)',
            borderRadius: 20, padding: '28px 24px', transition: 'background 0.3s, border-color 0.3s'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
              <Code2 size={20} color="var(--color-accent)" />
              <h4 className="font-heading" style={{ fontSize: '1.05rem', color: 'var(--color-text)', margin: 0 }}>
                Technical Expertise
              </h4>
            </div>

            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10 }}>
              {[
                'Python', 'Django', 'React.js', 'PostgreSQL', 'MySQL', 'XGBoost', 
                'Isolation Forest', 'REST APIs', 'Document Processing', 'Data Automation', 'Power BI'
              ].map(skill => (
                <div
                  key={skill}
                  style={{
                    background: 'var(--color-bg-card)',
                    border: '1px solid var(--color-border)',
                    borderRadius: 30, padding: '8px 16px',
                    fontSize: '0.82rem', fontWeight: 600, color: 'var(--color-text)',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.02)',
                    transition: 'all 0.2s ease'
                  }}
                  onMouseEnter={e => {
                    e.currentTarget.style.borderColor = 'var(--color-accent)';
                    e.currentTarget.style.transform = 'translateY(-2px)';
                  }}
                  onMouseLeave={e => {
                    e.currentTarget.style.borderColor = 'var(--color-border)';
                    e.currentTarget.style.transform = 'none';
                  }}
                >
                  {skill}
                </div>
              ))}
            </div>

            <div style={{ marginTop: 24, padding: '16px', borderRadius: 12, background: 'var(--color-bg-card)', border: '1px solid var(--color-border)' }}>
              <p style={{ fontSize: '0.8rem', color: 'var(--color-muted)', margin: 0, lineHeight: 1.5 }}>
                ✨ <strong>Specialized Focus:</strong> Ganesh architected an internal real-time document processing pipeline using Django, React, and PostgreSQL, featuring an AI routing layer that dynamically handles document flow.
              </p>
            </div>
          </div>
        </motion.div>
      </div>

      <style>{`
        .dev-grid {
          grid-template-columns: 1.2fr 0.8fr !important;
        }
        @media (max-width: 768px) {
          .dev-grid {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </section>
  );
}

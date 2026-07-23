import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { ArrowRightCircle } from 'lucide-react';
import Logo from '../Logo.jsx';

export default function Footer() {
  return (
    <>
      {/* CTA Band */}
      <section style={{
        background: 'radial-gradient(ellipse at center, rgba(0,119,182,0.08), transparent)',
        borderTop: '1px solid var(--color-border)', borderBottom: '1px solid var(--color-border)',
        padding: '80px 24px', textAlign: 'center', transition: 'border-color 0.3s'
      }}>
        <motion.div initial={{ opacity: 0, y: 28 }} whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }} transition={{ ease: [0.22, 1, 0.36, 1], duration: 0.6 }}
          style={{ maxWidth: 640, margin: '0 auto' }}>
          <h2 className="font-heading" style={{
            fontSize: 'clamp(1.8rem, 4vw, 2.6rem)', color: 'var(--color-text)', marginBottom: 16,
            transition: 'color 0.3s'
          }}>Ready to Protect Your Platform?</h2>
          <p style={{ color: 'var(--color-muted)', marginBottom: 32, fontSize: '0.95rem', lineHeight: 1.7, transition: 'color 0.3s' }}>
            Join analysts who trust FraudShield AI to stop fraud before it costs them.
          </p>
          <div style={{ display: 'flex', gap: 16, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Link to="/login" style={{
              background: 'var(--color-accent)', color: '#ffffff', borderRadius: 50,
              padding: '16px 28px', fontWeight: 700, textDecoration: 'none',
              display: 'flex', alignItems: 'center', gap: 12,
              boxShadow: '0 4px 24px rgba(0,119,182,0.3)', transition: 'all 0.2s ease'
            }}
              onMouseEnter={e => e.target.style.filter = 'brightness(1.1)'}
              onMouseLeave={e => e.target.style.filter = 'none'}
            >
              Start For Free <ArrowRightCircle size={20} />
            </Link>
          </div>
        </motion.div>
      </section>

      {/* Footer */}
      <footer style={{
        background: 'var(--color-bg-card)', borderTop: '1px solid var(--color-border)',
        padding: '48px 24px 32px', transition: 'background 0.3s, border-color 0.3s'
      }}>
        <div style={{
          maxWidth: 1280, margin: '0 auto',
          display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '2rem'
        }}>
          {/* Brand */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
              <Logo />
              <span className="font-heading" style={{ fontSize: 16, color: 'var(--color-text)', transition: 'color 0.3s' }}>FraudShield AI</span>
            </div>
            <p style={{ fontSize: '0.82rem', color: 'var(--color-muted)', lineHeight: 1.6, transition: 'color 0.3s' }}>
              AI-powered fraud detection for the modern financial stack.
            </p>
          </div>

          {/* Product */}
          <div>
            <h4 style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--color-muted)', marginBottom: 16, transition: 'color 0.3s' }}>Product</h4>
            {[
              { name: 'Dashboard', path: '/app/dashboard' },
              { name: 'Alerts', path: '/app/alerts' },
              { name: 'Simulation', path: '/app/simulation' },
              { name: 'Reports', path: '/app/reports' }
            ].map(l => (
              <Link key={l.name} to={l.path} style={{
                display: 'block', fontSize: '0.82rem', color: 'var(--color-muted)',
                textDecoration: 'none', marginBottom: 10, transition: 'color 0.2s'
              }}
                onMouseEnter={e => e.target.style.color = 'var(--color-text)'}
                onMouseLeave={e => e.target.style.color = 'var(--color-muted)'}
              >{l.name}</Link>
            ))}
          </div>

          {/* Docs */}
          <div>
            <h4 style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--color-muted)', marginBottom: 16, transition: 'color 0.3s' }}>Docs</h4>
            {['API Reference', 'Datasets', 'Integrations'].map(l => (
              <a key={l} href="#" style={{
                display: 'block', fontSize: '0.82rem', color: 'var(--color-muted)',
                textDecoration: 'none', marginBottom: 10, transition: 'color 0.2s'
              }}
                onMouseEnter={e => e.target.style.color = 'var(--color-text)'}
                onMouseLeave={e => e.target.style.color = 'var(--color-muted)'}
              >{l}</a>
            ))}
          </div>

          {/* Company */}
          <div>
            <h4 style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--color-muted)', marginBottom: 16, transition: 'color 0.3s' }}>Company</h4>
            {[
              { name: 'About Us', href: '#about' },
              { name: 'Contact', href: '#' },
              { name: 'Privacy', href: '#' }
            ].map(l => (
              <a key={l.name} href={l.href} style={{
                display: 'block', fontSize: '0.82rem', color: 'var(--color-muted)',
                textDecoration: 'none', marginBottom: 10, transition: 'color 0.2s'
              }}
                onMouseEnter={e => e.target.style.color = 'var(--color-text)'}
                onMouseLeave={e => e.target.style.color = 'var(--color-muted)'}
              >{l.name}</a>
            ))}
          </div>
        </div>

        <div style={{
          maxWidth: 1280, margin: '32px auto 0',
          borderTop: '1px solid var(--color-border)', paddingTop: 24,
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          flexWrap: 'wrap', gap: 12, transition: 'border-color 0.3s'
        }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--color-muted)', transition: 'color 0.3s' }}>© 2026 FraudShield AI</span>
          <span style={{ fontSize: '0.75rem', color: 'var(--color-muted)', transition: 'color 0.3s' }}>Developed by Ganesh Patne</span>
        </div>
      </footer>
    </>
  );
}

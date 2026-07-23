import React, { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { Database, LayoutDashboard, ArrowLeftRight, Bell, FlaskConical, FileText, LogOut, Moon, Sun, Menu, X } from 'lucide-react';
import Logo from './Logo.jsx';

const navItems = [
  { to: '/app/upload', icon: Database, label: 'Datasets' },
  { to: '/app/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/app/transactions', icon: ArrowLeftRight, label: 'Transactions' },
  { to: '/app/alerts', icon: Bell, label: 'Live Alerts' },
  { to: '/app/simulation', icon: FlaskConical, label: 'Fraud Simulation' },
  { to: '/app/reports', icon: FileText, label: 'Reports' },
];

export default function Sidebar({ user, onLogout, isDark, onToggleTheme }) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const navigate = useNavigate();

  const handleLogout = () => {
    onLogout();
    navigate('/login');
  };

  const sidebarContent = (
    <>
      {/* Header */}
      <div style={{ padding: '20px 20px 8px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <Logo />
          <span className="font-heading" style={{ fontSize: 17, color: 'var(--color-text)' }}>FraudShield AI</span>
        </div>
        <p style={{ fontSize: '0.7rem', color: 'var(--color-muted)', marginTop: 4, paddingLeft: 40 }}>Fraud Detection Platform</p>
      </div>

      {/* Navigation */}
      <nav style={{ flex: 1, padding: '16px 12px', display: 'flex', flexDirection: 'column', gap: 4 }}>
        {navItems.map(item => (
          <NavLink key={item.to} to={item.to}
            onClick={() => setMobileOpen(false)}
            className={({ isActive }) => `sidebar-nav-item ${isActive ? 'active' : ''}`}>
            <item.icon size={18} />
            {item.label}
          </NavLink>
        ))}
      </nav>

      {/* Bottom */}
      <div style={{ padding: '16px 20px', borderTop: '1px solid var(--color-border)' }}>
        {user && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
            <div style={{
              width: 32, height: 32, borderRadius: '50%',
              background: 'linear-gradient(135deg, #0077b6, #00b4d8)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: '0.8rem', fontWeight: 700, color: 'var(--color-bg)'
            }}>
              {(user.username || 'U')[0].toUpperCase()}
            </div>
            <div style={{ flex: 1 }}>
              <p style={{ fontSize: '0.82rem', color: 'var(--color-text)', fontWeight: 500 }}>{user.username}</p>
              <p style={{ fontSize: '0.7rem', color: 'var(--color-muted)', textTransform: 'capitalize' }}>{user.role}</p>
            </div>
          </div>
        )}
        <div style={{ display: 'flex', gap: 8 }}>
          <button onClick={onToggleTheme} style={{
            width: 32, height: 32, borderRadius: '50%',
            background: 'var(--color-bg-raised)', border: 'none',
            color: 'var(--color-muted)', cursor: 'pointer', display: 'flex',
            alignItems: 'center', justifyContent: 'center'
          }}>
            {isDark ? <Sun size={16} /> : <Moon size={16} />}
          </button>
          <button onClick={handleLogout} style={{
            width: 32, height: 32, borderRadius: '50%',
            background: 'var(--color-bg-raised)', border: 'none',
            color: 'var(--color-muted)', cursor: 'pointer', display: 'flex',
            alignItems: 'center', justifyContent: 'center'
          }}>
            <LogOut size={16} />
          </button>
        </div>
        <p style={{
          fontSize: '0.7rem', color: 'var(--color-accent)', fontWeight: 600,
          marginTop: 12
        }}>Developed by Ganesh Patne</p>
      </div>
    </>
  );

  return (
    <>
      {/* Mobile toggle */}
      <button className="sidebar-mobile-toggle" onClick={() => setMobileOpen(!mobileOpen)}
        style={{
          position: 'fixed', top: 12, left: 12, zIndex: 50,
          background: 'var(--color-sidebar-bg)', border: '1px solid var(--color-border)',
          borderRadius: 8, padding: 8, color: 'var(--color-text)', cursor: 'pointer'
        }}>
        {mobileOpen ? <X size={20} /> : <Menu size={20} />}
      </button>

      {/* Backdrop (mobile) */}
      {mobileOpen && (
        <div onClick={() => setMobileOpen(false)}
          style={{
            position: 'fixed', inset: 0, background: 'rgba(8,14,26,0.6)',
            zIndex: 39
          }} className="sidebar-mobile-toggle" />
      )}

      {/* Sidebar */}
      <aside className={`sidebar ${mobileOpen ? 'open' : ''}`}>
        {sidebarContent}
      </aside>

      <style>{`
        .sidebar-mobile-toggle { display: none; }
        @media (max-width: 1023px) {
          .sidebar-mobile-toggle { display: block; }
        }
      `}</style>
    </>
  );
}

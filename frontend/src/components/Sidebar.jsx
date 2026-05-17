import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard, ArrowLeftRight, Bell, FlaskConical,
  FileText, Shield, Database, LogOut, User, Moon, Sun
} from 'lucide-react';

const navItems = [
  { path: '/', label: 'Datasets', icon: Database, roles: ['admin'] },
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard, roles: ['admin', 'analyst', 'user'] },
  { path: '/transactions', label: 'Transactions', icon: ArrowLeftRight, roles: ['admin', 'analyst', 'user'] },
  { path: '/alerts', label: 'Live Alerts', icon: Bell, roles: ['admin', 'analyst'] },
  { path: '/simulation', label: 'Fraud Simulation', icon: FlaskConical, roles: ['admin', 'analyst'] },
  { path: '/reports', label: 'Reports', icon: FileText, roles: ['admin', 'analyst'] },
];

export default function Sidebar({ user, onLogout, isDark, onToggleTheme }) {
  const location = useLocation();

  const visibleItems = navItems.filter(item =>
    !user?.role || item.roles.includes(user.role)
  );

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '4px' }}>
          <Shield size={22} color="#00b4d8" />
          <h1>FraudShield AI</h1>
        </div>
        <span>Fraud Detection Platform</span>
      </div>

      <nav className="sidebar-nav">
        {visibleItems.map(({ path, label, icon: Icon }) => (
          <NavLink
            key={path}
            to={path}
            className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
            end={path === '/'}
          >
            <Icon size={18} />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        {user && (
          <div className="user-info">
            <div className="user-avatar">
              <User size={14} />
            </div>
            <div className="user-details">
              <span className="user-name">{user.username}</span>
              <span className="user-role">{user.role}</span>
            </div>
            <button
              className="logout-btn"
              onClick={onToggleTheme}
              title={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
              style={{ marginRight: '2px' }}
            >
              {isDark ? <Sun size={15} /> : <Moon size={15} />}
            </button>
            <button className="logout-btn" onClick={onLogout} title="Sign out" id="logout-btn">
              <LogOut size={16} />
            </button>
          </div>
        )}

        <div style={{
          fontSize: '0.72rem',
          color: 'var(--text-muted)',
          lineHeight: 1.6,
          marginTop: '12px',
        }}>
          <div style={{ color: 'var(--accent-primary)', fontWeight: 600, marginBottom: '4px' }}>
            Powered by NVIDIA AI
          </div>
          Developed by Ganesh Patne,
          Sujal Surve &amp; Aditya Tambadkar
        </div>
      </div>
    </aside>
  );
}

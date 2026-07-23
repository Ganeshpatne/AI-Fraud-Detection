import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertTriangle, ShieldAlert, Bell } from 'lucide-react';
import { fetchAlerts, connectWebSocket } from '../api.js';

const severityConfig = {
  critical: { color: '#ef4444', label: 'Critical', bg: 'rgba(239,68,68,0.04)' },
  high: { color: '#f59e0b', label: 'High', bg: 'transparent' },
  medium: { color: '#00b4d8', label: 'Medium', bg: 'transparent' },
};

export default function LiveAlerts() {
  const [alerts, setAlerts] = useState([]);
  const [counts, setCounts] = useState({ critical: 0, high: 0, medium: 0 });

  useEffect(() => {
    fetchAlerts(50).then(data => {
      const list = Array.isArray(data) ? data : [];
      setAlerts(list);
      updateCounts(list);
    }).catch(console.error);

    const cleanup = connectWebSocket((alert) => {
      setAlerts(prev => {
        const next = [alert, ...prev].slice(0, 100);
        updateCounts(next);
        return next;
      });
    });

    return cleanup;
  }, []);

  const updateCounts = (list) => {
    setCounts({
      critical: list.filter(a => a.severity === 'critical').length,
      high: list.filter(a => a.severity === 'high').length,
      medium: list.filter(a => a.severity === 'medium' || !a.severity).length,
    });
  };

  return (
    <div>
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
        transition={{ ease: [0.22, 1, 0.36, 1], duration: 0.5 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24, flexWrap: 'wrap', gap: 12 }}>
          <h1 className="font-heading" style={{ fontSize: 'clamp(1.4rem,3vw,1.85rem)', color: 'var(--color-text)' }}>
            Live Fraud Alerts
          </h1>
          <div style={{
            display: 'inline-flex', alignItems: 'center', gap: 6,
            background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.3)',
            borderRadius: 50, padding: '4px 14px'
          }}>
            <span className="live-dot" />
            <span style={{ fontSize: '0.75rem', color: '#10b981', fontWeight: 600 }}>LIVE</span>
          </div>
        </div>
      </motion.div>

      {/* Stats bar */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem', marginBottom: 24 }}>
        {[
          { label: 'Critical', count: counts.critical, color: '#ef4444', icon: AlertTriangle },
          { label: 'High Priority', count: counts.high, color: '#f59e0b', icon: ShieldAlert },
          { label: 'Medium', count: counts.medium, color: '#00b4d8', icon: Bell },
        ].map((s, i) => (
          <motion.div key={s.label} initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.08 }}
            className="card" style={{ borderLeft: `3px solid ${s.color}` }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <p style={{ fontSize: '0.75rem', color: '#64748b' }}>{s.label}</p>
                <p className="font-heading" style={{ fontSize: '1.5rem', color: 'var(--color-text)' }}>{s.count}</p>
              </div>
              <s.icon size={24} color={s.color} style={{ opacity: 0.3 }} />
            </div>
          </motion.div>
        ))}
      </div>

      {/* Alert feed */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        <AnimatePresence initial={false}>
          {alerts.map((alert, i) => {
            const sev = severityConfig[alert.severity] || severityConfig.medium;
            return (
              <motion.div key={alert.id || i}
                initial={{ x: 32, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
                className={`alert-item ${alert.severity || 'medium'}`}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <span style={{
                    width: 8, height: 8, borderRadius: '50%', background: sev.color, flexShrink: 0
                  }} />
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                      <span className={`badge badge-${alert.severity || 'medium'}`}>
                        {sev.label}
                      </span>
                      <span style={{ fontSize: '0.82rem', color: 'var(--color-muted)', fontFamily: 'monospace' }}>
                        TXN #{alert.transaction_id || alert.id}
                      </span>
                    </div>
                    <p style={{ fontSize: '0.84rem', color: 'var(--color-text)', marginTop: 4 }}>
                      {alert.message || `Suspicious activity detected — Risk Score: ${alert.risk_score || 'N/A'}`}
                    </p>
                    <p style={{ fontSize: '0.72rem', color: 'var(--color-muted)', marginTop: 4 }}>
                      {alert.timestamp ? new Date(alert.timestamp).toLocaleString() : 'Just now'}
                    </p>
                  </div>
                  {alert.risk_score != null && (
                    <span className="font-heading" style={{
                      fontSize: '1.1rem',
                      color: alert.risk_score >= 80 ? '#ef4444' : alert.risk_score >= 50 ? '#f59e0b' : '#10b981'
                    }}>
                      {alert.risk_score}
                    </span>
                  )}
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>
        {alerts.length === 0 && (
          <div style={{ textAlign: 'center', padding: 60, color: '#64748b' }}>
            <Bell size={40} style={{ opacity: 0.2, margin: '0 auto 12px' }} />
            <p>No alerts yet. Monitoring for suspicious activity...</p>
          </div>
        )}
      </div>
    </div>
  );
}

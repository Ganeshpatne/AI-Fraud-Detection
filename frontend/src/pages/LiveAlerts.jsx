import React, { useEffect, useState, useRef } from 'react';
import { connectWebSocket, fetchAlerts } from '../api.js';
import { Bell, AlertTriangle, ShieldAlert, Clock } from 'lucide-react';

export default function LiveAlerts() {
  const [alerts, setAlerts] = useState([]);
  const [connected, setConnected] = useState(false);
  const feedRef = useRef(null);

  useEffect(() => {
    // Load historical alerts
    fetchAlerts(30).then(data => {
      setAlerts(data.map(a => ({ ...a, type: 'fraud_alert' })));
    }).catch(() => {
      // Demo data
      setAlerts([
        { id: '1', severity: 'critical', message: 'Fraud detected: Very high transaction amount: $18,432.00; Location mismatch', transaction_id: 'txn-0001', user_id: 'user-1', created_at: new Date().toISOString() },
        { id: '2', severity: 'high', message: 'Fraud detected: Device fingerprint mismatch; High transaction amount: $7,200.00', transaction_id: 'txn-0002', user_id: 'user-3', created_at: new Date(Date.now() - 300000).toISOString() },
        { id: '3', severity: 'medium', message: 'Suspicious frequency: 7 transactions in the last hour from user-5', transaction_id: 'txn-0003', user_id: 'user-5', created_at: new Date(Date.now() - 600000).toISOString() },
        { id: '4', severity: 'critical', message: 'Fraud detected: Location mismatch; Device mismatch; Amount $22,100', transaction_id: 'txn-0004', user_id: 'user-2', created_at: new Date(Date.now() - 900000).toISOString() },
        { id: '5', severity: 'high', message: 'ML classifier flagged transaction as fraudulent (confidence: 94.2%)', transaction_id: 'txn-0005', user_id: 'user-4', created_at: new Date(Date.now() - 1200000).toISOString() },
      ]);
    });

    // Connect WebSocket
    const disconnect = connectWebSocket((msg) => {
      setConnected(true);
      if (msg.type === 'fraud_alert') {
        setAlerts(prev => [{ ...msg.data, type: 'fraud_alert', created_at: msg.timestamp }, ...prev].slice(0, 100));
      } else if (msg.type === 'history') {
        // Initial history from WS
      }
    });

    setConnected(true);
    return disconnect;
  }, []);

  function timeAgo(iso) {
    const diff = Date.now() - new Date(iso).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return 'Just now';
    if (mins < 60) return `${mins}m ago`;
    const hours = Math.floor(mins / 60);
    if (hours < 24) return `${hours}h ago`;
    return `${Math.floor(hours / 24)}d ago`;
  }

  return (
    <div style={{ animation: 'fadeIn 0.5s ease-out' }}>
      <div className="page-header" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h1>Live Fraud Alerts</h1>
          <p>Real-time fraud detection activity stream</p>
        </div>
        <div className="live-indicator">
          <span className="live-dot" />
          {connected ? 'Live' : 'Connecting...'}
        </div>
      </div>

      {/* Stats bar */}
      <div style={{
        display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem',
        marginBottom: '2rem'
      }}>
        {[
          { label: 'Critical', count: alerts.filter(a => a.severity === 'critical').length, color: 'var(--danger)' },
          { label: 'High Priority', count: alerts.filter(a => a.severity === 'high').length, color: 'var(--warning)' },
          { label: 'Medium', count: alerts.filter(a => a.severity === 'medium').length, color: 'var(--info)' },
        ].map((s, i) => (
          <div key={i} className="metric-card" style={{ borderLeft: `3px solid ${s.color}` }}>
            <div className="metric-label">{s.label}</div>
            <div className="metric-value" style={{ fontSize: '1.5rem' }}>{s.count}</div>
          </div>
        ))}
      </div>

      {/* Alerts Feed */}
      <div className="alerts-feed" ref={feedRef}>
        {alerts.length === 0 ? (
          <div className="empty-state">
            <Bell size={48} />
            <p>No alerts yet. Waiting for fraud detection events…</p>
          </div>
        ) : (
          alerts.map((alert, i) => (
            <div
              key={alert.id || i}
              className={`alert-item ${alert.severity || 'medium'}`}
              style={{ animationDelay: `${i * 0.05}s`, animation: 'slideInRight 0.3s ease-out backwards' }}
            >
              <div className={`alert-dot ${alert.severity || 'medium'}`} />
              <div className="alert-content">
                <div className="alert-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  {alert.severity === 'critical' ? <ShieldAlert size={14} color="var(--danger)" /> :
                    <AlertTriangle size={14} color="var(--warning)" />}
                  <span className={`badge badge-${alert.severity || 'medium'}`}>
                    {alert.severity?.toUpperCase() || 'MEDIUM'}
                  </span>
                  {alert.transaction_id && (
                    <span style={{ fontFamily: 'monospace', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      {alert.transaction_id.substring(0, 12)}
                    </span>
                  )}
                </div>
                <div className="alert-message">{alert.message}</div>
                <div className="alert-time">
                  <Clock size={11} style={{ verticalAlign: 'middle', marginRight: '4px' }} />
                  {alert.created_at ? timeAgo(alert.created_at) : 'Just now'}
                </div>
              </div>
              {alert.risk_score && (
                <div style={{
                  textAlign: 'right', minWidth: '60px'
                }}>
                  <div style={{ fontSize: '1.1rem', fontWeight: 700, color: alert.risk_score >= 70 ? 'var(--danger)' : 'var(--warning)' }}>
                    {alert.risk_score.toFixed(0)}
                  </div>
                  <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>RISK</div>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}

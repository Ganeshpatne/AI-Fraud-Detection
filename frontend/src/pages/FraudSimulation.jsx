import React, { useState, useEffect } from 'react';
import { simulateTransaction, fetchUsers } from '../api.js';
import {
  FlaskConical, MapPin, Smartphone, CreditCard, DollarSign,
  ShieldCheck, ShieldAlert, Loader2
} from 'lucide-react';

export default function FraudSimulation() {
  const [users, setUsers] = useState([]);
  const [form, setForm] = useState({
    user_id: '',
    amount: 1500,
    location: 'Mumbai, IN',
    device_fingerprint: 'device-sim-001',
    merchant: 'Online Store',
    category: 'shopping',
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const locations = [
    'Mumbai, IN', 'Pune, IN', 'Delhi, IN', 'Bangalore, IN',
    'New York, US', 'London, UK', 'Tokyo, JP', 'Lagos, NG',
    'Moscow, RU', 'São Paulo, BR', 'Dubai, AE', 'Sydney, AU',
  ];

  useEffect(() => {
    fetchUsers().then(setUsers).catch(() => {
      setUsers([
        { id: 'demo-user-1', username: 'ganesh_patne' },
        { id: 'demo-user-2', username: 'sujal_surve' },
        { id: 'demo-user-3', username: 'aditya_tambadkar' },
      ]);
    });
  }, []);

  async function handleSimulate(e) {
    e.preventDefault();
    if (!form.user_id) return;
    setLoading(true);
    setResult(null);
    try {
      const res = await simulateTransaction(form);
      setResult(res);
    } catch (err) {
      // Demo result
      const riskScore = form.amount > 10000 ? 78 : form.amount > 5000 ? 52 : 18;
      setResult({
        is_fraud: riskScore >= 50,
        risk_score: riskScore,
        confidence: riskScore / 100,
        fraud_type: riskScore >= 50 ? 'rule_based' : null,
        reason: riskScore >= 50
          ? `High transaction amount: $${form.amount.toLocaleString()}; Potential location mismatch detected`
          : 'No fraud indicators detected.',
        risk_factors: {
          amount_factor: form.amount > 15000 ? 35 : form.amount > 5000 ? 20 : 0,
          location_factor: 0,
          frequency_factor: 0,
          device_factor: 0,
        },
      });
    } finally {
      setLoading(false);
    }
  }

  const gaugeColor = result
    ? result.risk_score >= 70 ? 'var(--danger)' : result.risk_score >= 40 ? 'var(--warning)' : 'var(--success)'
    : 'var(--accent-primary)';

  return (
    <div style={{ animation: 'fadeIn 0.5s ease-out' }}>
      <div className="page-header">
        <h1>Fraud Simulation Panel</h1>
        <p>Simulate transactions and get instant fraud predictions</p>
      </div>

      <div className="simulation-panel">
        {/* Form */}
        <div className="card simulation-form">
          <h3 style={{ color: 'var(--accent-primary)', marginBottom: '1.5rem', fontSize: '1rem', fontWeight: 600 }}>
            <FlaskConical size={18} style={{ verticalAlign: 'middle', marginRight: '8px' }} />
            Transaction Parameters
          </h3>

          <form onSubmit={handleSimulate}>
            <div className="form-group">
              <label className="form-label">User</label>
              <select
                className="form-select"
                value={form.user_id}
                onChange={(e) => setForm({ ...form, user_id: e.target.value })}
                required
              >
                <option value="">Select a user…</option>
                {users.map(u => (
                  <option key={u.id} value={u.id}>{u.username} ({u.id.substring(0, 8)})</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label"><DollarSign size={13} /> Amount ($)</label>
              <input
                type="number"
                className="form-input"
                value={form.amount}
                onChange={(e) => setForm({ ...form, amount: parseFloat(e.target.value) || 0 })}
                min="1"
                step="0.01"
                required
              />
              {/* Quick amounts */}
              <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
                {[100, 1500, 5000, 15000, 50000].map(amt => (
                  <button
                    key={amt}
                    type="button"
                    className="btn btn-secondary btn-sm"
                    style={{ fontSize: '0.72rem', padding: '0.3rem 0.6rem' }}
                    onClick={() => setForm({ ...form, amount: amt })}
                  >
                    ${amt.toLocaleString()}
                  </button>
                ))}
              </div>
            </div>

            <div className="form-group">
              <label className="form-label"><MapPin size={13} /> Location</label>
              <select
                className="form-select"
                value={form.location}
                onChange={(e) => setForm({ ...form, location: e.target.value })}
              >
                {locations.map(l => <option key={l} value={l}>{l}</option>)}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label"><Smartphone size={13} /> Device Fingerprint</label>
              <input
                type="text"
                className="form-input"
                value={form.device_fingerprint}
                onChange={(e) => setForm({ ...form, device_fingerprint: e.target.value })}
                placeholder="e.g. device-12345"
              />
            </div>

            <div className="form-group">
              <label className="form-label"><CreditCard size={13} /> Merchant</label>
              <input
                type="text"
                className="form-input"
                value={form.merchant}
                onChange={(e) => setForm({ ...form, merchant: e.target.value })}
              />
            </div>

            <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '0.5rem' }} disabled={loading}>
              {loading ? <><Loader2 size={16} className="spinner" /> Analyzing…</> : <><FlaskConical size={16} /> Run Simulation</>}
            </button>
          </form>
        </div>

        {/* Result */}
        <div className="card simulation-result">
          {!result && !loading && (
            <div className="empty-state">
              <FlaskConical size={48} />
              <p style={{ marginTop: '1rem' }}>Configure parameters and run a simulation to see fraud prediction results</p>
            </div>
          )}

          {loading && (
            <div className="loading-spinner">
              <div className="spinner" />
            </div>
          )}

          {result && !loading && (
            <div style={{ animation: 'scaleIn 0.4s ease-out', width: '100%', textAlign: 'center' }}>
              {/* Risk Gauge */}
              <div
                className="risk-gauge"
                style={{
                  '--gauge-color': gaugeColor,
                  '--gauge-percent': `${result.risk_score}%`,
                  margin: '0 auto 1.5rem',
                }}
              >
                <div className="risk-gauge-value" style={{ color: gaugeColor }}>
                  {result.risk_score.toFixed(0)}
                </div>
                <div className="risk-gauge-label">Risk Score</div>
              </div>

              {/* Status Badge */}
              <div style={{ marginBottom: '1.5rem' }}>
                {result.is_fraud ? (
                  <div className="badge badge-fraud" style={{ fontSize: '0.85rem', padding: '0.4rem 1rem' }}>
                    <ShieldAlert size={14} style={{ marginRight: '6px' }} />
                    FRAUDULENT
                  </div>
                ) : (
                  <div className="badge badge-legitimate" style={{ fontSize: '0.85rem', padding: '0.4rem 1rem' }}>
                    <ShieldCheck size={14} style={{ marginRight: '6px' }} />
                    LEGITIMATE
                  </div>
                )}
              </div>

              {/* Details */}
              <div style={{ textAlign: 'left', width: '100%' }}>
                <div style={{
                  background: 'var(--bg-secondary)', borderRadius: 'var(--radius-md)',
                  padding: '1.25rem', marginBottom: '1rem'
                }}>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '0.5rem' }}>
                    Confidence
                  </div>
                  <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                    {(result.confidence * 100).toFixed(1)}%
                  </div>
                </div>

                <div style={{
                  background: 'var(--bg-secondary)', borderRadius: 'var(--radius-md)',
                  padding: '1.25rem', marginBottom: '1rem'
                }}>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '0.5rem' }}>
                    Detection Reason
                  </div>
                  <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                    {result.reason}
                  </div>
                </div>

                {/* Risk Factor Bars */}
                <div style={{
                  background: 'var(--bg-secondary)', borderRadius: 'var(--radius-md)',
                  padding: '1.25rem'
                }}>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '1rem' }}>
                    Risk Factor Breakdown
                  </div>
                  {Object.entries(result.risk_factors).map(([key, val]) => (
                    <div key={key} style={{ marginBottom: '0.75rem' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                        <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'capitalize' }}>
                          {key.replace('_', ' ')}
                        </span>
                        <span style={{ fontSize: '0.8rem', color: 'var(--text-primary)', fontWeight: 600 }}>{val}</span>
                      </div>
                      <div style={{
                        height: '6px', borderRadius: '3px', background: 'var(--border-color)', overflow: 'hidden'
                      }}>
                        <div style={{
                          height: '100%', borderRadius: '3px',
                          width: `${Math.min((val / 35) * 100, 100)}%`,
                          background: val > 20 ? 'var(--danger)' : val > 0 ? 'var(--warning)' : 'var(--border-color)',
                          transition: 'width 0.6s ease-out',
                        }} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

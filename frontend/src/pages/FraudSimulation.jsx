import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { DollarSign, MapPin, Smartphone, CreditCard, FlaskConical, Loader2 } from 'lucide-react';
import { simulateTransaction, fetchUsers } from '../api.js';

const locations = ['New York', 'London', 'Tokyo', 'Mumbai', 'Lagos', 'São Paulo', 'Berlin', 'Sydney', 'Toronto', 'Dubai', 'Singapore', 'Paris'];

const RiskGauge = ({ score }) => {
  const angle = (score / 100) * 180;
  const color = score >= 80 ? '#ef4444' : score >= 50 ? '#f59e0b' : '#10b981';
  const r = 80, cx = 100, cy = 95;
  const startAngle = Math.PI;
  const endAngle = Math.PI - (angle * Math.PI / 180);
  const x1 = cx + r * Math.cos(startAngle);
  const y1 = cy + r * Math.sin(startAngle) * -1;
  const x2 = cx + r * Math.cos(endAngle);
  const y2 = cy + r * Math.sin(endAngle) * -1;
  const large = angle > 180 ? 1 : 0;

  return (
    <div className="gauge-container" style={{ width: 200, height: 120, margin: '0 auto 16px' }}>
      <svg viewBox="0 0 200 110" width="200" height="110">
        <path d={`M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}`}
          fill="none" stroke="var(--color-border)" strokeWidth="12" strokeLinecap="round" />
        <path d={`M ${x1} ${y1} A ${r} ${r} 0 ${large} 1 ${x2} ${y2}`}
          fill="none" stroke={color} strokeWidth="12" strokeLinecap="round" />
        <text x={cx} y={cy - 10} textAnchor="middle" fill={color}
          className="font-heading" style={{ fontSize: '2rem' }}>{score}</text>
        <text x={cx} y={cy + 10} textAnchor="middle" fill="#64748b" style={{ fontSize: '0.7rem' }}>
          RISK SCORE
        </text>
      </svg>
    </div>
  );
};

export default function FraudSimulation() {
  const [users, setUsers] = useState([]);
  const [form, setForm] = useState({
    user_id: '', amount: '', location: locations[0],
    device_fingerprint: '', merchant: '', category: ''
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  useEffect(() => {
    fetchUsers(0, 50).then(data => {
      setUsers(Array.isArray(data) ? data : data.users || []);
    }).catch(console.error);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    try {
      const res = await simulateTransaction({
        ...form, amount: parseFloat(form.amount),
        user_id: parseInt(form.user_id)
      });
      setResult(res);
    } catch (err) {
      setResult({ error: err.message });
    }
    setLoading(false);
  };

  const inputStyle = {
    width: '100%', padding: '10px 14px 10px 38px', borderRadius: 10,
    border: '1px solid var(--color-border)', background: 'var(--color-bg-raised)',
    color: 'var(--color-text)', fontSize: '0.88rem'
  };

  const factors = result && !result.error ? [
    { label: 'Amount Risk', score: Math.min(100, (result.risk_score || 0) * 1.1) },
    { label: 'Location Risk', score: Math.min(100, (result.risk_score || 0) * 0.8) },
    { label: 'Behavioral', score: Math.min(100, (result.risk_score || 0) * 0.9) },
    { label: 'Pattern Match', score: Math.min(100, (result.risk_score || 0) * 0.7) },
  ] : [];

  return (
    <div>
      <motion.h1 initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
        className="font-heading" style={{
          fontSize: 'clamp(1.4rem,3vw,1.85rem)', color: 'var(--color-text)', marginBottom: 24
        }}>Fraud Simulation Panel</motion.h1>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(380px, 1fr))', gap: '1.25rem' }}>
        {/* Form */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }} className="card" style={{ borderRadius: 14 }}>
          <form onSubmit={handleSubmit}>
            {[
              { label: 'User', icon: <Smartphone size={16} color="#64748b" />, field: (
                <select style={{ ...inputStyle, cursor: 'pointer' }} value={form.user_id}
                  onChange={e => setForm({ ...form, user_id: e.target.value })} required>
                  <option value="">Select user</option>
                  {users.map(u => <option key={u.id} value={u.id}>{u.username || `User ${u.id}`}</option>)}
                </select>
              )},
              { label: 'Amount ($)', icon: <DollarSign size={16} color="#64748b" />, field: (
                <input type="number" style={inputStyle} placeholder="0.00" value={form.amount}
                  onChange={e => setForm({ ...form, amount: e.target.value })} required />
              )},
              { label: 'Location', icon: <MapPin size={16} color="#64748b" />, field: (
                <select style={{ ...inputStyle, cursor: 'pointer' }} value={form.location}
                  onChange={e => setForm({ ...form, location: e.target.value })}>
                  {locations.map(l => <option key={l} value={l}>{l}</option>)}
                </select>
              )},
              { label: 'Device Fingerprint', icon: <Smartphone size={16} color="#64748b" />, field: (
                <input style={inputStyle} placeholder="e.g. iPhone-14-Pro" value={form.device_fingerprint}
                  onChange={e => setForm({ ...form, device_fingerprint: e.target.value })} />
              )},
              { label: 'Merchant', icon: <CreditCard size={16} color="#64748b" />, field: (
                <input style={inputStyle} placeholder="e.g. Amazon" value={form.merchant}
                  onChange={e => setForm({ ...form, merchant: e.target.value })} />
              )},
              { label: 'Category', icon: <FlaskConical size={16} color="#64748b" />, field: (
                <input style={inputStyle} placeholder="e.g. Electronics" value={form.category}
                  onChange={e => setForm({ ...form, category: e.target.value })} />
              )},
            ].map(({ label, icon, field }) => (
              <div key={label} style={{ marginBottom: 16 }}>
                <label style={{ fontSize: '0.8rem', color: '#94a3b8', marginBottom: 6, display: 'block' }}>{label}</label>
                <div style={{ position: 'relative' }}>
                  <span style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)' }}>{icon}</span>
                  {field}
                </div>
              </div>
            ))}

            <button type="submit" disabled={loading} style={{
              width: '100%', padding: 14, borderRadius: 12,
              background: 'linear-gradient(135deg, #0077b6, #00b4d8)',
              color: 'white', fontWeight: 700, border: 'none',
              cursor: loading ? 'wait' : 'pointer', fontSize: '0.95rem',
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
              opacity: loading ? 0.7 : 1
            }}>
              {loading && <Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} />}
              {loading ? 'Analyzing...' : 'Run Simulation'}
            </button>
          </form>
        </motion.div>

        {/* Result */}
        {result && !result.error && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
            className="card" style={{ borderRadius: 14 }}>
            <RiskGauge score={Math.round(result.risk_score || 0)} />

            <div style={{
              textAlign: 'center', padding: '16px 20px', borderRadius: 12, marginBottom: 20,
              background: result.is_fraud ? 'rgba(239,68,68,0.1)' : 'rgba(16,185,129,0.1)',
              border: `1px solid ${result.is_fraud ? 'rgba(239,68,68,0.3)' : 'rgba(16,185,129,0.3)'}`,
            }}>
              <p className="font-heading" style={{
                fontSize: '1.2rem',
                color: result.is_fraud ? '#ef4444' : '#10b981'
              }}>
                {result.is_fraud ? '⚠ FRAUD DETECTED' : '✓ LEGITIMATE'}
              </p>
            </div>

            {result.reason && (
              <p style={{ fontSize: '0.85rem', color: '#94a3b8', lineHeight: 1.6, marginBottom: 20 }}>
                {result.reason}
              </p>
            )}

            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {factors.map(f => (
                <div key={f.label}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                    <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>{f.label}</span>
                    <span style={{ fontSize: '0.8rem', color: 'var(--color-text)', fontWeight: 600 }}>{f.score.toFixed(0)}</span>
                  </div>
                  <div style={{ height: 6, background: 'var(--color-border)', borderRadius: 3 }}>
                    <div style={{
                      height: '100%', borderRadius: 3,
                      width: `${f.score}%`,
                      background: f.score >= 70 ? '#ef4444' : f.score >= 40 ? '#f59e0b' : '#10b981',
                      transition: 'width 0.5s ease'
                    }} />
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {result?.error && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
            className="card" style={{ borderRadius: 14, borderColor: 'rgba(239,68,68,0.3)' }}>
            <p style={{ color: '#ef4444', fontSize: '0.88rem' }}>Error: {result.error}</p>
          </motion.div>
        )}
      </div>
    </div>
  );
}

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Activity, ShieldAlert, CheckCircle, TrendingUp, Bell } from 'lucide-react';
import {
  BarChart, Bar, PieChart, Pie, Cell, LineChart, Line,
  XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid
} from 'recharts';
import {
  fetchDashboardStats, fetchFraudsByHour,
  fetchFraudsByLocation, fetchConfidenceDistribution
} from '../api.js';

const fadeUp = (i) => ({
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { delay: i * 0.08, ease: [0.22, 1, 0.36, 1], duration: 0.5 }
});

const PIE_COLORS = ['#00b4d8', '#0077b6', '#ef4444', '#f59e0b', '#10b981', '#8b5cf6'];

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: 'var(--color-bg-card)', border: '1px solid var(--color-border)',
      borderRadius: 8, padding: '10px 14px', color: 'var(--color-text)', fontSize: '0.82rem'
    }}>
      <p style={{ fontWeight: 600 }}>{label}</p>
      {payload.map((p, i) => (
        <p key={i} style={{ color: p.color }}>{p.name}: {p.value}</p>
      ))}
    </div>
  );
};

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [hourly, setHourly] = useState([]);
  const [locations, setLocations] = useState([]);
  const [confidence, setConfidence] = useState([]);
  const [trend, setTrend] = useState([]);

  const loadData = async () => {
    try {
      const [s, h, l, c] = await Promise.all([
        fetchDashboardStats(), fetchFraudsByHour(),
        fetchFraudsByLocation(), fetchConfidenceDistribution()
      ]);
      setStats(s);
      setHourly(Array.isArray(h) ? h : []);
      setLocations(Array.isArray(l) ? l : []);
      setConfidence(Array.isArray(c) ? c : []);
      setTrend(prev => {
        const next = [...prev, { time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }), frauds: s?.total_fraudulent || 0 }];
        return next.slice(-12);
      });
    } catch (e) { console.error(e); }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 3000);
    return () => clearInterval(interval);
  }, []);

  const metrics = stats ? [
    { label: 'Total Transactions', value: stats.total_transactions?.toLocaleString() || '0', icon: Activity, color: '#00b4d8' },
    { label: 'Fraudulent', value: stats.total_fraudulent?.toLocaleString() || '0', icon: ShieldAlert, color: '#ef4444' },
    { label: 'Legitimate', value: stats.total_legitimate?.toLocaleString() || '0', icon: CheckCircle, color: '#10b981' },
    { label: 'Avg Risk Score', value: (stats.avg_risk_score || 0).toFixed(1), icon: TrendingUp, color: '#00b4d8' },
    { label: 'Fraud Rate %', value: (stats.fraud_rate || 0).toFixed(1) + '%', icon: ShieldAlert, color: '#f59e0b' },
    { label: 'Alerts Today', value: stats.alerts_today?.toString() || '0', icon: Bell, color: '#00b4d8' },
  ] : [];

  return (
    <div>
      <motion.div {...fadeUp(0)}>
        <h1 className="font-heading" style={{ fontSize: 'clamp(1.4rem,3vw,1.85rem)', color: 'var(--color-text)', marginBottom: 4 }}>
          Fraud Analytics Dashboard
        </h1>
        <p style={{ fontSize: '0.88rem', color: '#64748b', marginBottom: 28 }}>Real-time monitoring and insights</p>
      </motion.div>

      {/* Metric cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: 28 }}>
        {metrics.map((m, i) => (
          <motion.div key={m.label} {...fadeUp(i + 1)} className="metric-card">
            <m.icon size={28} style={{ color: m.color, opacity: 0.22, position: 'absolute', top: 16, right: 16 }} />
            <p style={{ fontSize: '0.78rem', color: '#64748b', marginBottom: 4 }}>{m.label}</p>
            <p className="font-heading" style={{ fontSize: '1.7rem', color: 'var(--color-text)' }}>{m.value}</p>
          </motion.div>
        ))}
      </div>

      {/* Charts */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '1.25rem' }}>
        {/* Frauds Per Hour */}
        <motion.div {...fadeUp(7)} className="card" style={{ borderRadius: 14 }}>
          <h3 className="font-heading" style={{ fontSize: '0.95rem', color: 'var(--color-text)', marginBottom: 20 }}>Frauds Per Hour (24h)</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={hourly}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(26,42,64,0.5)" />
              <XAxis dataKey="hour" tick={{ fill: '#64748b', fontSize: 11 }} />
              <YAxis tick={{ fill: '#64748b', fontSize: 11 }} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="count" name="Frauds" fill="url(#barGrad)" radius={[4, 4, 0, 0]} />
              <defs>
                <linearGradient id="barGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#00b4d8" />
                  <stop offset="100%" stopColor="#0077b6" />
                </linearGradient>
              </defs>
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Frauds by Location */}
        <motion.div {...fadeUp(8)} className="card" style={{ borderRadius: 14 }}>
          <h3 className="font-heading" style={{ fontSize: '0.95rem', color: 'var(--color-text)', marginBottom: 20 }}>Frauds By Location</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie data={locations} dataKey="count" nameKey="location" cx="50%" cy="50%"
                innerRadius={55} outerRadius={90} paddingAngle={3}>
                {locations.map((_, i) => (
                  <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Model Confidence */}
        <motion.div {...fadeUp(9)} className="card" style={{ borderRadius: 14 }}>
          <h3 className="font-heading" style={{ fontSize: '0.95rem', color: 'var(--color-text)', marginBottom: 20 }}>Model Confidence Distribution</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={confidence}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(26,42,64,0.5)" />
              <XAxis dataKey="range" tick={{ fill: '#64748b', fontSize: 11 }} />
              <YAxis tick={{ fill: '#64748b', fontSize: 11 }} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="count" name="Transactions" fill="url(#confGrad)" radius={[4, 4, 0, 0]} />
              <defs>
                <linearGradient id="confGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#8b5cf6" />
                  <stop offset="100%" stopColor="#6d28d9" />
                </linearGradient>
              </defs>
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Fraud Trend */}
        <motion.div {...fadeUp(10)} className="card" style={{ borderRadius: 14 }}>
          <h3 className="font-heading" style={{ fontSize: '0.95rem', color: 'var(--color-text)', marginBottom: 20 }}>Fraud Activity Trend</h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={trend}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(26,42,64,0.5)" />
              <XAxis dataKey="time" tick={{ fill: '#64748b', fontSize: 11 }} />
              <YAxis tick={{ fill: '#64748b', fontSize: 11 }} />
              <Tooltip content={<CustomTooltip />} />
              <Line type="monotone" dataKey="frauds" stroke="#00b4d8" strokeWidth={2} dot={{ r: 3, fill: '#00b4d8' }} />
            </LineChart>
          </ResponsiveContainer>
        </motion.div>
      </div>
    </div>
  );
}

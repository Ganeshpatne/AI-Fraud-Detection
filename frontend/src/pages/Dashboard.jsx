import React, { useEffect, useState } from 'react';
import {
  BarChart, Bar, PieChart, Pie, Cell, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import { Activity, ShieldAlert, CheckCircle, TrendingUp } from 'lucide-react';
import {
  fetchDashboardStats, fetchFraudsByHour,
  fetchFraudsByLocation, fetchConfidenceDistribution
} from '../api.js';

const COLORS = ['#00b4d8', '#ef4444', '#f59e0b', '#00cc96', '#8b5cf6', '#ec4899'];

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [hourlyData, setHourlyData] = useState([]);
  const [locationData, setLocationData] = useState([]);
  const [confidenceData, setConfidenceData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
    const interval = setInterval(() => {
      Promise.all([
        fetchDashboardStats(),
        fetchFraudsByHour(24),
        fetchFraudsByLocation(8),
        fetchConfidenceDistribution(),
      ]).then(([s, h, l, c]) => {
        setStats(s);
        setHourlyData(h);
        setLocationData(l);
        setConfidenceData(c);
      }).catch(() => {});
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  async function loadData() {
    try {
      const [s, h, l, c] = await Promise.all([
        fetchDashboardStats(),
        fetchFraudsByHour(24),
        fetchFraudsByLocation(8),
        fetchConfidenceDistribution(),
      ]);
      setStats(s);
      setHourlyData(h);
      setLocationData(l);
      setConfidenceData(c);
    } catch (e) {
      console.error('Failed to load dashboard:', e);
      // Set fallback demo data
      setStats({
        total_transactions: 500, total_fraudulent: 73, total_legitimate: 427,
        fraud_rate: 14.6, avg_risk_score: 32.5, high_risk_users: 5, alerts_today: 12
      });
      setHourlyData([
        { hour: 0, count: 2 }, { hour: 3, count: 1 }, { hour: 6, count: 3 },
        { hour: 9, count: 5 }, { hour: 12, count: 8 }, { hour: 15, count: 6 },
        { hour: 18, count: 10 }, { hour: 21, count: 7 }
      ]);
      setLocationData([
        { location: 'Mumbai, IN', count: 18 }, { location: 'Lagos, NG', count: 12 },
        { location: 'Moscow, RU', count: 9 }, { location: 'New York, US', count: 7 },
        { location: 'London, UK', count: 5 }
      ]);
      setConfidenceData([
        { bucket: '0-20%', count: 5 }, { bucket: '20-40%', count: 8 },
        { bucket: '40-60%', count: 15 }, { bucket: '60-80%', count: 25 },
        { bucket: '80-100%', count: 20 }
      ]);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="loading-spinner">
        <div className="spinner" />
      </div>
    );
  }

  const metrics = [
    { label: 'Total Transactions', value: stats?.total_transactions?.toLocaleString() || '0', icon: Activity, change: null },
    { label: 'Fraudulent', value: stats?.total_fraudulent?.toLocaleString() || '0', icon: ShieldAlert, change: `${stats?.fraud_rate || 0}% rate`, changeType: 'negative' },
    { label: 'Legitimate', value: stats?.total_legitimate?.toLocaleString() || '0', icon: CheckCircle, change: null },
    { label: 'Avg Risk Score', value: stats?.avg_risk_score?.toFixed(1) || '0', icon: TrendingUp, change: `${stats?.high_risk_users || 0} high-risk users` },
    { label: 'Fraud Rate', value: `${stats?.fraud_rate || 0}%`, icon: ShieldAlert, change: null },
    { label: 'Alerts Today', value: stats?.alerts_today?.toLocaleString() || '0', icon: Activity, change: null },
  ];

  const tooltipStyle = {
    backgroundColor: '#ffffff',
    border: '1px solid #e2e8f0',
    borderRadius: '8px',
    color: '#1e293b',
    fontSize: '0.8rem',
    boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
  };

  return (
    <div style={{ animation: 'fadeIn 0.5s ease-out' }}>
      <div className="page-header">
        <h1>Fraud Analytics Dashboard</h1>
        <p>Real-time monitoring and insights into transaction fraud patterns</p>
      </div>

      {/* Metrics */}
      <div className="metrics-grid">
        {metrics.map((m, i) => (
          <div key={i} className="metric-card" style={{ animationDelay: `${i * 0.08}s`, animation: 'fadeInUp 0.5s ease-out backwards' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <div className="metric-label">{m.label}</div>
                <div className="metric-value">{m.value}</div>
                {m.change && (
                  <div className={`metric-change ${m.changeType || 'positive'}`}>{m.change}</div>
                )}
              </div>
              <m.icon size={28} style={{ color: 'var(--accent-primary)', opacity: 0.3 }} />
            </div>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="charts-grid">
        {/* Frauds Per Hour */}
        <div className="chart-card">
          <h3>Frauds Per Hour (24h)</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={hourlyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,180,216,0.08)" />
              <XAxis dataKey="hour" stroke="#5a6380" fontSize={11} tickFormatter={(h) => `${h}:00`} />
              <YAxis stroke="#5a6380" fontSize={11} />
              <Tooltip contentStyle={tooltipStyle} />
              <Bar dataKey="count" fill="url(#barGradient)" radius={[4, 4, 0, 0]} />
              <defs>
                <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#00b4d8" />
                  <stop offset="100%" stopColor="#0077b6" />
                </linearGradient>
              </defs>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Frauds Per Location */}
        <div className="chart-card">
          <h3>Frauds By Location</h3>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={locationData}
                dataKey="count"
                nameKey="location"
                cx="50%"
                cy="50%"
                innerRadius={55}
                outerRadius={100}
                paddingAngle={3}
                label={({ location, percent }) => `${location.split(',')[0]} ${(percent * 100).toFixed(0)}%`}
                labelLine={false}
              >
                {locationData.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip contentStyle={tooltipStyle} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Confidence Distribution */}
        <div className="chart-card">
          <h3>Model Confidence Distribution</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={confidenceData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,180,216,0.08)" />
              <XAxis dataKey="bucket" stroke="#5a6380" fontSize={11} />
              <YAxis stroke="#5a6380" fontSize={11} />
              <Tooltip contentStyle={tooltipStyle} />
              <Bar dataKey="count" fill="url(#confGradient)" radius={[4, 4, 0, 0]} />
              <defs>
                <linearGradient id="confGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#8b5cf6" />
                  <stop offset="100%" stopColor="#6d28d9" />
                </linearGradient>
              </defs>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Fraud Trend */}
        <div className="chart-card">
          <h3>Fraud Activity Trend</h3>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={hourlyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,180,216,0.08)" />
              <XAxis dataKey="hour" stroke="#5a6380" fontSize={11} tickFormatter={(h) => `${h}:00`} />
              <YAxis stroke="#5a6380" fontSize={11} />
              <Tooltip contentStyle={tooltipStyle} />
              <Line
                type="monotone"
                dataKey="count"
                stroke="#00b4d8"
                strokeWidth={2.5}
                dot={{ fill: '#00b4d8', r: 4 }}
                activeDot={{ r: 6, strokeWidth: 2, stroke: '#fff' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

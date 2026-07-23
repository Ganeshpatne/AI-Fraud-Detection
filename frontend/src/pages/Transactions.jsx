import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Filter, ChevronLeft, ChevronRight } from 'lucide-react';
import { fetchTransactions } from '../api.js';

export default function Transactions() {
  const [txns, setTxns] = useState([]);
  const [filter, setFilter] = useState('all');
  const [page, setPage] = useState(0);
  const limit = 20;

  const loadData = async () => {
    try {
      const data = await fetchTransactions(page * limit, limit, filter);
      setTxns(Array.isArray(data) ? data : data.transactions || []);
    } catch (e) { console.error(e); }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 2000);
    return () => clearInterval(interval);
  }, [page, filter]);

  const riskColor = (score) => {
    if (score >= 80) return '#ef4444';
    if (score >= 50) return '#f59e0b';
    return '#10b981';
  };

  return (
    <div>
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
        transition={{ ease: [0.22, 1, 0.36, 1], duration: 0.5 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24, flexWrap: 'wrap', gap: 12 }}>
          <h1 className="font-heading" style={{ fontSize: 'clamp(1.4rem,3vw,1.85rem)', color: 'var(--color-text)' }}>
            Transaction Monitor
          </h1>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Filter size={16} color="#64748b" />
            <select value={filter} onChange={e => { setFilter(e.target.value); setPage(0); }}
              style={{
                background: 'var(--color-bg-raised)', border: '1px solid var(--color-border)', color: 'var(--color-text)',
                borderRadius: 8, padding: '8px 12px', fontSize: '0.82rem', cursor: 'pointer'
              }}>
              <option value="all">All Transactions</option>
              <option value="fraud">Fraud Only</option>
              <option value="legit">Legit Only</option>
            </select>
          </div>
        </div>
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1, ease: [0.22, 1, 0.36, 1], duration: 0.5 }}
        style={{ borderRadius: 14, overflow: 'hidden', border: '1px solid var(--color-border)' }}>
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Amount</th>
                <th>Location</th>
                <th>Merchant</th>
                <th>Risk Score</th>
                <th>Confidence</th>
                <th>Status</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {txns.map(tx => (
                <tr key={tx.id}>
                  <td style={{ fontFamily: 'monospace', color: '#00b4d8', fontSize: '0.8rem' }}>
                    #{tx.id}
                  </td>
                  <td style={{ color: (tx.amount || 0) > 5000 ? '#ef4444' : 'var(--color-text)', fontWeight: 600 }}>
                    ${(tx.amount || 0).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                  </td>
                  <td style={{ color: 'var(--color-muted)' }}>{tx.location || '—'}</td>
                  <td style={{ color: 'var(--color-muted)' }}>{tx.merchant || '—'}</td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <div className="risk-bar-bg">
                        <div className="risk-bar-fill" style={{
                          width: `${tx.risk_score || 0}%`,
                          background: riskColor(tx.risk_score || 0)
                        }} />
                      </div>
                      <span style={{ fontSize: '0.8rem', color: riskColor(tx.risk_score || 0), fontWeight: 600 }}>
                        {(tx.risk_score || 0).toFixed(0)}
                      </span>
                    </div>
                  </td>
                  <td style={{ color: 'var(--color-muted)', fontSize: '0.82rem' }}>
                    {((tx.confidence || 0) * 100).toFixed(1)}%
                  </td>
                  <td>
                    <span className={`badge ${tx.is_fraud ? 'badge-fraud' : 'badge-legit'}`}>
                      {tx.is_fraud ? 'FRAUD' : 'LEGIT'}
                    </span>
                  </td>
                  <td style={{ color: '#64748b', fontSize: '0.78rem', whiteSpace: 'nowrap' }}>
                    {tx.timestamp ? new Date(tx.timestamp).toLocaleString() : '—'}
                  </td>
                </tr>
              ))}
              {txns.length === 0 && (
                <tr>
                  <td colSpan={8} style={{ textAlign: 'center', color: '#64748b', padding: 40 }}>
                    No transactions found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </motion.div>

      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 16, marginTop: 20 }}>
        <button onClick={() => setPage(Math.max(0, page - 1))} disabled={page === 0}
          style={{
            background: 'var(--color-bg-card)', border: '1px solid var(--color-border)',
            borderRadius: 8, padding: '8px 12px', color: 'var(--color-text)',
            cursor: page === 0 ? 'not-allowed' : 'pointer', opacity: page === 0 ? 0.4 : 1
          }}>
          <ChevronLeft size={16} />
        </button>
        <span style={{ fontSize: '0.82rem', color: 'var(--color-muted)' }}>Page {page + 1}</span>
        <button onClick={() => setPage(page + 1)} disabled={txns.length < limit}
          style={{
            background: 'var(--color-bg-card)', border: '1px solid var(--color-border)',
            borderRadius: 8, padding: '8px 12px', color: 'var(--color-text)',
            cursor: txns.length < limit ? 'not-allowed' : 'pointer',
            opacity: txns.length < limit ? 0.4 : 1
          }}>
          <ChevronRight size={16} />
        </button>
      </div>
    </div>
  );
}

import React, { useEffect, useState } from 'react';
import { fetchTransactions } from '../api.js';
import { Search, Filter, ChevronLeft, ChevronRight } from 'lucide-react';

export default function Transactions() {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterType, setFilterType] = useState('all');
  const [page, setPage] = useState(0);
  const limit = 20;

  useEffect(() => { 
    loadTransactions(); 
    const interval = setInterval(async () => {
      try {
        const data = await fetchTransactions(page * limit, limit, filterType);
        setTransactions(data);
      } catch (e) {}
    }, 2000);
    return () => clearInterval(interval);
  }, [page, filterType]);

  async function loadTransactions() {
    setLoading(true);
    try {
      const data = await fetchTransactions(page * limit, limit, filterType);
      setTransactions(data);
    } catch (e) {
      console.error('Failed to load transactions:', e);
      // Demo data
      setTransactions(Array.from({ length: 15 }, (_, i) => ({
        id: `txn-${String(i + 1).padStart(4, '0')}`,
        user_id: `user-${(i % 5) + 1}`,
        amount: Math.random() * 15000,
        location: ['Mumbai, IN', 'New York, US', 'Lagos, NG', 'London, UK', 'Tokyo, JP'][i % 5],
        is_fraud: Math.random() > 0.7,
        risk_score: Math.random() * 100,
        confidence: Math.random(),
        timestamp: new Date(Date.now() - Math.random() * 86400000 * 3).toISOString(),
        merchant: ['Amazon', 'Netflix', 'Uber', 'Flipkart', 'Crypto Exchange'][i % 5],
      })));
    } finally {
      setLoading(false);
    }
  }

  function formatDate(iso) {
    return new Date(iso).toLocaleString('en-IN', {
      day: '2-digit', month: 'short', year: 'numeric',
      hour: '2-digit', minute: '2-digit',
    });
  }

  return (
    <div style={{ animation: 'fadeIn 0.5s ease-out' }}>
      <div className="page-header">
        <h1>Transaction Monitor</h1>
        <p>Browse and analyze all processed transactions</p>
      </div>

      {/* Controls */}
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Filter size={16} color="var(--text-muted)" />
          <select 
            className="form-select" 
            style={{ 
              width: '220px', 
              fontWeight: 600, 
              color: filterType === 'fraud' ? 'var(--danger)' : filterType === 'legit' ? 'var(--success)' : 'var(--text-primary)',
              borderColor: filterType === 'fraud' ? 'var(--danger)' : filterType === 'legit' ? 'var(--success)' : undefined
            }}
            value={filterType} 
            onChange={(e) => { setFilterType(e.target.value); setPage(0); }}
          >
            <option value="all">🚦 All Transactions</option>
            <option value="fraud">🔴 Showing Fraud Only</option>
            <option value="legit">🟢 Showing Legit Only</option>
          </select>
        </div>
        <div style={{ marginLeft: 'auto', color: 'var(--text-muted)', fontSize: '0.82rem' }}>
          Page {page + 1} • {transactions.length} records
        </div>
      </div>

      {/* Table */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        {loading ? (
          <div className="loading-spinner"><div className="spinner" /></div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Transaction ID</th>
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
              {transactions.map((txn) => (
                <tr key={txn.id}>
                  <td style={{ fontFamily: 'monospace', fontSize: '0.72rem', color: 'var(--accent-primary)', userSelect: 'all' }}>
                    {txn.id}
                  </td>
                  <td style={{ fontWeight: 600, color: txn.amount > 5000 ? 'var(--danger)' : 'var(--text-primary)' }}>
                    ${txn.amount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </td>
                  <td>{txn.location || '—'}</td>
                  <td>{txn.merchant || '—'}</td>
                  <td>
                    <div style={{
                      display: 'flex', alignItems: 'center', gap: '8px'
                    }}>
                      <div style={{
                        width: '50px', height: '5px', borderRadius: '3px',
                        background: 'var(--border-color)', overflow: 'hidden'
                      }}>
                        <div style={{
                          height: '100%', borderRadius: '3px',
                          width: `${Math.min(txn.risk_score, 100)}%`,
                          background: txn.risk_score >= 70 ? 'var(--danger)' :
                            txn.risk_score >= 40 ? 'var(--warning)' : 'var(--success)',
                        }} />
                      </div>
                      <span style={{ fontSize: '0.78rem' }}>{txn.risk_score.toFixed(1)}</span>
                    </div>
                  </td>
                  <td style={{ fontSize: '0.82rem' }}>{(txn.confidence * 100).toFixed(1)}%</td>
                  <td>
                    <span className={`badge ${txn.is_fraud ? 'badge-fraud' : 'badge-legitimate'}`}>
                      {txn.is_fraud ? 'Fraud' : 'Legit'}
                    </span>
                  </td>
                  <td style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                    {formatDate(txn.timestamp)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Pagination */}
      <div style={{
        display: 'flex', justifyContent: 'center', gap: '0.75rem',
        marginTop: '1.5rem', alignItems: 'center'
      }}>
        <button className="btn btn-secondary btn-sm" onClick={() => setPage(Math.max(0, page - 1))} disabled={page === 0}>
          <ChevronLeft size={14} /> Previous
        </button>
        <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Page {page + 1}</span>
        <button className="btn btn-secondary btn-sm" onClick={() => setPage(page + 1)} disabled={transactions.length < limit}>
          Next <ChevronRight size={14} />
        </button>
      </div>
    </div>
  );
}

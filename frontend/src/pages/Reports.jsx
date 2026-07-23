import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FileText, Search, CheckCircle, Download, Loader2 } from 'lucide-react';
import { generateReport, downloadReport, fetchTransactions } from '../api.js';

export default function Reports() {
  const [txnId, setTxnId] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(null);
  const [error, setError] = useState('');
  const [reports, setReports] = useState([]);
  const [fraudTxns, setFraudTxns] = useState([]);

  useEffect(() => {
    fetchTransactions(0, 20, 'fraud').then(data => {
      setFraudTxns(Array.isArray(data) ? data : data.transactions || []);
    }).catch(console.error);
  }, []);

  const handleGenerate = async (e) => {
    e.preventDefault();
    if (!txnId) return;
    setLoading(true);
    setError('');
    setSuccess(null);
    try {
      const res = await generateReport(txnId);
      setSuccess(res);
      setReports(prev => [{
        id: `RPT-${Date.now()}`, transaction_id: txnId,
        generated_at: new Date().toISOString()
      }, ...prev]);
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  };

  return (
    <div>
      <motion.h1 initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
        className="font-heading" style={{
          fontSize: 'clamp(1.4rem,3vw,1.85rem)', color: 'var(--color-text)', marginBottom: 24
        }}>Investigation Reports</motion.h1>

      {/* Generator */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }} className="card" style={{ borderRadius: 14, marginBottom: 24 }}>
        <form onSubmit={handleGenerate} style={{ display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'flex-end' }}>
          <div style={{ flex: 1, minWidth: 200 }}>
            <label style={{ fontSize: '0.8rem', color: '#94a3b8', display: 'block', marginBottom: 6 }}>Transaction ID</label>
            <div style={{ position: 'relative' }}>
              <Search size={16} color="#64748b" style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)' }} />
              <input value={txnId} onChange={e => setTxnId(e.target.value)}
                placeholder="Enter transaction ID"
                style={{
                  width: '100%', padding: '10px 14px 10px 38px', borderRadius: 10,
                  border: '1px solid var(--color-border)', background: 'var(--color-bg-raised)',
                  color: 'var(--color-text)', fontSize: '0.88rem'
                }} />
            </div>
          </div>
          <div style={{ minWidth: 200 }}>
            <label style={{ fontSize: '0.8rem', color: '#94a3b8', display: 'block', marginBottom: 6 }}>Quick Select</label>
            <select onChange={e => setTxnId(e.target.value)} value=""
              style={{
                width: '100%', padding: '10px 14px', borderRadius: 10,
                border: '1px solid var(--color-border)', background: 'var(--color-bg-raised)',
                color: 'var(--color-text)', fontSize: '0.88rem', cursor: 'pointer'
              }}>
              <option value="">Select fraud transaction</option>
              {fraudTxns.map(t => (
                <option key={t.id} value={t.id}>TXN #{t.id} — ${t.amount?.toFixed(2)}</option>
              ))}
            </select>
          </div>
          <button type="submit" disabled={loading || !txnId} style={{
            padding: '10px 24px', borderRadius: 10,
            background: 'linear-gradient(135deg, #0077b6, #00b4d8)',
            color: 'white', fontWeight: 700, border: 'none',
            cursor: loading || !txnId ? 'not-allowed' : 'pointer',
            fontSize: '0.88rem', display: 'flex', alignItems: 'center', gap: 8,
            opacity: loading || !txnId ? 0.5 : 1, whiteSpace: 'nowrap'
          }}>
            {loading ? <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} /> : <FileText size={16} />}
            {loading ? 'Generating...' : 'Generate PDF'}
          </button>
        </form>

        {error && (
          <div style={{
            marginTop: 16, padding: '10px 14px', borderRadius: 10,
            background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)',
            color: '#ef4444', fontSize: '0.82rem'
          }}>{error}</div>
        )}

        {success && (
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
            style={{
              marginTop: 16, padding: '14px 18px', borderRadius: 10,
              background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.3)',
              display: 'flex', alignItems: 'center', justifyContent: 'space-between'
            }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <CheckCircle size={20} color="#10b981" />
              <span style={{ color: '#10b981', fontSize: '0.88rem', fontWeight: 500 }}>
                Report generated successfully
              </span>
            </div>
            <a href={downloadReport(txnId)} target="_blank" rel="noreferrer"
              style={{
                display: 'flex', alignItems: 'center', gap: 6,
                background: 'rgba(16,185,129,0.2)', padding: '6px 14px',
                borderRadius: 8, color: '#10b981', fontWeight: 600,
                fontSize: '0.82rem', textDecoration: 'none'
              }}>
              <Download size={14} /> Download
            </a>
          </motion.div>
        )}
      </motion.div>

      {/* History table */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        style={{ borderRadius: 14, overflow: 'hidden', border: '1px solid var(--color-border)' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th>Report ID</th>
              <th>Transaction ID</th>
              <th>Generated At</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {reports.map(r => (
              <tr key={r.id}>
                <td style={{ fontFamily: 'monospace', color: 'var(--color-accent)', fontSize: '0.82rem' }}>{r.id}</td>
                <td style={{ fontFamily: 'monospace', color: 'var(--color-muted)' }}>#{r.transaction_id}</td>
                <td style={{ color: 'var(--color-muted)', fontSize: '0.82rem' }}>
                  {new Date(r.generated_at).toLocaleString()}
                </td>
                <td>
                  <a href={downloadReport(r.transaction_id)} target="_blank" rel="noreferrer"
                    style={{
                      display: 'inline-flex', alignItems: 'center', gap: 4,
                      padding: '4px 12px', borderRadius: 6,
                      background: 'rgba(0,180,216,0.1)', color: '#00b4d8',
                      fontSize: '0.78rem', fontWeight: 600, textDecoration: 'none'
                    }}>
                    <Download size={12} /> Download
                  </a>
                </td>
              </tr>
            ))}
            {reports.length === 0 && (
              <tr>
                <td colSpan={4} style={{ textAlign: 'center', padding: 48, color: '#64748b' }}>
                  <FileText size={40} style={{ opacity: 0.15, margin: '0 auto 12px', display: 'block' }} />
                  <p>No reports generated yet. Select a transaction to get started.</p>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </motion.div>
    </div>
  );
}

import React, { useState, useEffect } from 'react';
import { generateReport, downloadReport, fetchTransactions } from '../api.js';
import { FileText, Download, Loader2, CheckCircle, Search, AlertTriangle } from 'lucide-react';

export default function Reports() {
  const [transactionId, setTransactionId] = useState('');
  const [reportResult, setReportResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [generatedReports, setGeneratedReports] = useState([]);
  const [recentFrauds, setRecentFrauds] = useState([]);

  useEffect(() => {
    // Fetch recent fraudulent transactions for quick filtering/selection
    fetchTransactions(0, 10, true)
      .then(data => setRecentFrauds(data))
      .catch(console.error);
  }, []);

  async function handleGenerate(e) {
    e.preventDefault();
    if (!transactionId.trim()) return;
    setLoading(true);
    setError('');
    try {
      const res = await generateReport(transactionId);
      setReportResult(res);
      setGeneratedReports(prev => [res, ...prev]);
    } catch (err) {
      setError(err.message || 'Failed to generate report');
      // Demo
      const demoReport = {
        id: `rpt-${Date.now()}`,
        transaction_id: transactionId,
        file_path: 'reports/demo_report.pdf',
        generated_at: new Date().toISOString(),
      };
      setReportResult(demoReport);
      setGeneratedReports(prev => [demoReport, ...prev]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ animation: 'fadeIn 0.5s ease-out' }}>
      <div className="page-header">
        <h1>Investigation Reports</h1>
        <p>Generate and download PDF fraud investigation reports</p>
      </div>

      {/* Generator */}
      <div className="card" style={{ marginBottom: '2rem' }}>
        <h3 style={{
          color: 'var(--accent-primary)', fontSize: '1rem', fontWeight: 600,
          marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '8px'
        }}>
          <FileText size={18} /> Generate Report
        </h3>

        <form onSubmit={handleGenerate} style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', alignItems: 'flex-end' }}>
          <div className="form-group" style={{ flex: 1, minWidth: '250px', marginBottom: 0 }}>
            <label className="form-label">Transaction ID</label>
            <input
              type="text"
              className="form-input"
              value={transactionId}
              onChange={(e) => setTransactionId(e.target.value)}
              placeholder="Enter the transaction ID to generate report for…"
              required
            />
          </div>
          <div className="form-group" style={{ flex: 1, minWidth: '250px', marginBottom: 0 }}>
            <label className="form-label" style={{ color: 'var(--danger)' }}>
              <AlertTriangle size={12} style={{ display: 'inline', marginRight: '4px' }}/> 
              Quick Select Recent Fraud
            </label>
            <select 
              className="form-select" 
              onChange={(e) => setTransactionId(e.target.value)}
              value=""
            >
              <option value="" disabled>Select a flagged transaction...</option>
              {recentFrauds.map(txn => (
                <option key={txn.id} value={txn.id}>
                  ${txn.amount} - {new Date(txn.timestamp).toLocaleTimeString()} ({txn.id.substring(0, 8)})
                </option>
              ))}
            </select>
          </div>
          <button type="submit" className="btn btn-primary" disabled={loading} style={{ height: '40px' }}>
            {loading ? <><Loader2 size={16} className="spinner" /> Generating…</> : <><FileText size={16} /> Generate PDF</>}
          </button>
        </form>

        {error && (
          <div style={{
            marginTop: '1rem', padding: '0.75rem 1rem',
            background: 'var(--danger-bg)', border: '1px solid rgba(239,68,68,0.2)',
            borderRadius: 'var(--radius-sm)', color: 'var(--danger)', fontSize: '0.85rem'
          }}>
            {error}
          </div>
        )}

        {reportResult && (
          <div style={{
            marginTop: '1rem', padding: '1rem 1.25rem',
            background: 'var(--success-bg)', border: '1px solid rgba(0,204,150,0.2)',
            borderRadius: 'var(--radius-md)',
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
            animation: 'fadeInUp 0.4s ease-out'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <CheckCircle size={18} color="var(--success)" />
              <div>
                <div style={{ color: 'var(--success)', fontWeight: 600, fontSize: '0.88rem' }}>
                  Report Generated Successfully
                </div>
                <div style={{ color: 'var(--text-muted)', fontSize: '0.78rem', marginTop: '2px' }}>
                  Transaction: {reportResult.transaction_id?.substring(0, 16)}
                </div>
              </div>
            </div>
            <a
              href={downloadReport(reportResult.transaction_id)}
              target="_blank"
              rel="noreferrer"
              className="btn btn-primary btn-sm"
              style={{ textDecoration: 'none' }}
            >
              <Download size={14} /> Download PDF
            </a>
          </div>
        )}
      </div>

      {/* Generated Reports History */}
      <div className="card">
        <h3 style={{
          color: 'var(--accent-primary)', fontSize: '1rem', fontWeight: 600,
          marginBottom: '1.25rem'
        }}>
          Generated Reports
        </h3>

        {generatedReports.length === 0 ? (
          <div className="empty-state">
            <FileText size={48} />
            <p style={{ marginTop: '1rem' }}>No reports generated yet. Enter a transaction ID above to create one.</p>
          </div>
        ) : (
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
              {generatedReports.map((rpt) => (
                <tr key={rpt.id}>
                  <td style={{ fontFamily: 'monospace', fontSize: '0.78rem', color: 'var(--accent-primary)' }}>
                    {rpt.id?.substring(0, 12)}
                  </td>
                  <td style={{ fontFamily: 'monospace', fontSize: '0.78rem' }}>
                    {rpt.transaction_id?.substring(0, 16)}
                  </td>
                  <td style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                    {new Date(rpt.generated_at).toLocaleString()}
                  </td>
                  <td>
                    <a
                      href={downloadReport(rpt.transaction_id)}
                      target="_blank"
                      rel="noreferrer"
                      className="btn btn-secondary btn-sm"
                      style={{ textDecoration: 'none' }}
                    >
                      <Download size={12} /> Download
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

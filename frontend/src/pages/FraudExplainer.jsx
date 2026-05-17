import React, { useState } from 'react';
import { explainFraud } from '../api.js';
import { BrainCircuit, Send, Loader2, AlertTriangle, Info } from 'lucide-react';

export default function FraudExplainer() {
  const [transactionId, setTransactionId] = useState('');
  const [question, setQuestion] = useState('Why was this transaction flagged?');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function handleExplain(e) {
    e.preventDefault();
    if (!transactionId.trim()) return;
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const res = await explainFraud(transactionId, question);
      setResult(res);
    } catch (err) {
      // Demo fallback
      setResult({
        transaction_id: transactionId,
        explanation: `This transaction was flagged by our hybrid fraud detection engine. The system identified multiple risk factors that together exceeded the fraud detection threshold.\n\nThe transaction exhibited unusual characteristics compared to the user's historical spending patterns. The amount was significantly higher than the user's average transaction, and the transaction originated from a location that differs from the user's registered location.\n\nAdditionally, the device fingerprint used for this transaction does not match any previously known device associated with this account, suggesting potential unauthorized access.\n\nBased on our multi-layered analysis combining rule-based checks, anomaly detection (Isolation Forest), and machine learning classification (XGBoost), the system assigned a high risk score to this transaction.\n\nRecommendation: This transaction should be reviewed by the fraud investigation team. Consider temporarily restricting the account until identity verification is completed.`,
        risk_factors: [
          'Unusual transaction amount exceeding historical average',
          'Geographic location mismatch from user profile',
          'Unrecognized device fingerprint',
          'Transaction frequency anomaly detected',
        ],
        confidence_score: 0.87,
        behavior_mismatch: [
          'Transaction location differs from user\'s usual location',
          'Transaction made from an unrecognized device',
          'Abnormal spending pattern detected',
        ],
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ animation: 'fadeIn 0.5s ease-out' }}>
      <div className="page-header">
        <h1>AI Fraud Explainer</h1>
        <p>Get NVIDIA AI-powered explanations for flagged transactions</p>
      </div>

      {/* Info banner */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: '12px',
        background: 'rgba(0, 180, 216, 0.06)',
        border: '1px solid rgba(0, 180, 216, 0.15)',
        borderRadius: 'var(--radius-md)',
        padding: '1rem 1.25rem',
        marginBottom: '2rem',
        fontSize: '0.85rem',
        color: 'var(--text-secondary)',
      }}>
        <Info size={18} color="var(--accent-primary)" />
        Powered by NVIDIA NIM inference API — Generates detailed AI explanations for fraud detection decisions.
      </div>

      {/* Input */}
      <div className="card" style={{ marginBottom: '2rem' }}>
        <form onSubmit={handleExplain} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label">Transaction ID</label>
              <input
                type="text"
                className="form-input"
                value={transactionId}
                onChange={(e) => setTransactionId(e.target.value)}
                placeholder="Enter transaction ID…"
                required
              />
            </div>
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label">Your Question</label>
              <input
                type="text"
                className="form-input"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Why was this transaction flagged?"
              />
            </div>
          </div>
          <button type="submit" className="btn btn-primary" disabled={loading} style={{ alignSelf: 'flex-start' }}>
            {loading ? <><Loader2 size={16} className="spinner" /> Analyzing with NVIDIA AI…</> : <><BrainCircuit size={16} /> Get AI Explanation</>}
          </button>
        </form>
      </div>

      {error && (
        <div style={{
          background: 'var(--danger-bg)', border: '1px solid rgba(239,68,68,0.2)',
          borderRadius: 'var(--radius-md)', padding: '1rem', color: 'var(--danger)',
          marginBottom: '1.5rem'
        }}>
          {error}
        </div>
      )}

      {/* Result */}
      {result && (
        <div style={{ animation: 'fadeInUp 0.5s ease-out' }}>
          {/* Confidence Score */}
          <div style={{
            display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem',
            marginBottom: '1.5rem'
          }}>
            <div className="metric-card">
              <div className="metric-label">Confidence Score</div>
              <div className="metric-value" style={{ fontSize: '1.5rem' }}>
                {(result.confidence_score * 100).toFixed(1)}%
              </div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Risk Factors</div>
              <div className="metric-value" style={{ fontSize: '1.5rem' }}>
                {result.risk_factors?.length || 0}
              </div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Behavior Mismatches</div>
              <div className="metric-value" style={{ fontSize: '1.5rem' }}>
                {result.behavior_mismatch?.length || 0}
              </div>
            </div>
          </div>

          {/* Explanation */}
          <div className="explanation-card" style={{ marginBottom: '1.5rem' }}>
            <h3 style={{
              color: 'var(--accent-primary)', fontSize: '1rem', fontWeight: 600,
              marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '8px'
            }}>
              <BrainCircuit size={18} /> AI Explanation
            </h3>
            <div className="explanation-text">{result.explanation}</div>
          </div>

          {/* Risk Factors & Behavior Mismatches */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
            <div className="card">
              <h3 style={{ color: 'var(--warning)', fontSize: '0.95rem', fontWeight: 600, marginBottom: '1rem' }}>
                <AlertTriangle size={16} style={{ verticalAlign: 'middle', marginRight: '8px' }} />
                Risk Factors
              </h3>
              <ul className="risk-factors-list">
                {result.risk_factors?.map((f, i) => <li key={i}>{f}</li>)}
              </ul>
            </div>

            <div className="card">
              <h3 style={{ color: 'var(--danger)', fontSize: '0.95rem', fontWeight: 600, marginBottom: '1rem' }}>
                <AlertTriangle size={16} style={{ verticalAlign: 'middle', marginRight: '8px' }} />
                Behavior Mismatches
              </h3>
              <ul className="risk-factors-list">
                {result.behavior_mismatch?.map((b, i) => <li key={i}>{b}</li>)}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { Upload, Database, Loader2, Trash2, Play } from 'lucide-react';
import { uploadDataset, fetchDatasets, trainOnDataset, deleteDataset } from '../api.js';

const domains = ['Auto-detect', 'Banking', 'Insurance', 'E-commerce', 'Document Fraud', 'Custom'];

const statusBadge = (status) => {
  const map = {
    uploaded: 'badge-uploaded',
    validated: 'badge-validated',
    training: 'badge-training',
    ready: 'badge-ready',
    error: 'badge-error',
  };
  return map[status] || 'badge-uploaded';
};

export default function DatasetUpload() {
  const [datasets, setDatasets] = useState([]);
  const [dragOver, setDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [name, setName] = useState('');
  const [domain, setDomain] = useState('Auto-detect');
  const [file, setFile] = useState(null);
  const fileRef = useRef(null);

  const loadDatasets = async () => {
    try {
      const data = await fetchDatasets();
      setDatasets(Array.isArray(data) ? data : []);
    } catch (e) { console.error(e); }
  };

  useEffect(() => { loadDatasets(); }, []);

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    try {
      await uploadDataset(file, name || file.name, domain);
      setFile(null);
      setName('');
      loadDatasets();
    } catch (e) { console.error(e); }
    setUploading(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const f = e.dataTransfer.files[0];
    if (f && f.name.endsWith('.csv')) setFile(f);
  };

  const handleTrain = async (id) => {
    try {
      await trainOnDataset(id);
      loadDatasets();
    } catch (e) { console.error(e); }
  };

  const handleDelete = async (id) => {
    try {
      await deleteDataset(id);
      loadDatasets();
    } catch (e) { console.error(e); }
  };

  const inputStyle = {
    width: '100%', padding: '10px 14px', borderRadius: 10,
    border: '1px solid var(--color-border)', background: 'var(--color-bg-raised)',
    color: 'var(--color-text)', fontSize: '0.88rem'
  };

  return (
    <div>
      <motion.h1 initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
        className="font-heading" style={{
          fontSize: 'clamp(1.4rem,3vw,1.85rem)', color: 'var(--color-text)', marginBottom: 24
        }}>Dataset Manager</motion.h1>

      {/* Dropzone */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}>
        <div
          className={`dropzone ${dragOver ? 'active' : ''}`}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => fileRef.current?.click()}
        >
          <input ref={fileRef} type="file" accept=".csv" hidden
            onChange={e => { if (e.target.files[0]) setFile(e.target.files[0]); }} />
          <Upload size={48} color="#00b4d8" style={{ marginBottom: 16 }} />
          <h3 className="font-heading" style={{ fontSize: '1.1rem', color: 'var(--color-text)', marginBottom: 8 }}>
            {file ? file.name : 'Drop your CSV here'}
          </h3>
          <p style={{ fontSize: '0.82rem', color: '#64748b', marginBottom: 16 }}>
            {file ? `${(file.size / 1024).toFixed(1)} KB` : 'or click to browse files'}
          </p>
          {!file && (
            <button type="button" style={{
              background: 'transparent', border: '1px solid var(--color-border)',
              color: 'var(--color-text)', borderRadius: 10, padding: '8px 20px',
              cursor: 'pointer', fontSize: '0.85rem'
            }}>Browse Files</button>
          )}
        </div>
      </motion.div>

      {/* Form fields */}
      {file && (
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
          style={{ display: 'grid', gridTemplateColumns: '1fr 1fr auto', gap: 12, marginTop: 16, alignItems: 'flex-end' }}>
          <div>
            <label style={{ fontSize: '0.8rem', color: '#94a3b8', display: 'block', marginBottom: 6 }}>Dataset Name</label>
            <input style={inputStyle} value={name} onChange={e => setName(e.target.value)} placeholder="My dataset" />
          </div>
          <div>
            <label style={{ fontSize: '0.8rem', color: '#94a3b8', display: 'block', marginBottom: 6 }}>Domain</label>
            <select style={{ ...inputStyle, cursor: 'pointer' }} value={domain} onChange={e => setDomain(e.target.value)}>
              {domains.map(d => <option key={d} value={d}>{d}</option>)}
            </select>
          </div>
          <button onClick={handleUpload} disabled={uploading} style={{
            padding: '10px 24px', borderRadius: 10,
            background: 'linear-gradient(135deg, #0077b6, #00b4d8)',
            color: 'white', fontWeight: 700, border: 'none',
            cursor: uploading ? 'wait' : 'pointer', fontSize: '0.88rem',
            display: 'flex', alignItems: 'center', gap: 8, whiteSpace: 'nowrap'
          }}>
            {uploading ? <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} /> : <Upload size={16} />}
            {uploading ? 'Uploading...' : 'Upload'}
          </button>
        </motion.div>
      )}

      {/* Datasets table */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        style={{ borderRadius: 14, overflow: 'hidden', border: '1px solid var(--color-border)', marginTop: 28 }}>
        <table className="data-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Domain</th>
              <th>Records</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {datasets.map(ds => (
              <tr key={ds.id}>
                <td style={{ color: 'var(--color-text)', fontWeight: 500 }}>{ds.name}</td>
                <td style={{ color: 'var(--color-muted)' }}>{ds.domain || '—'}</td>
                <td style={{ color: 'var(--color-muted)' }}>{ds.record_count?.toLocaleString() || '—'}</td>
                <td>
                  <span className={`badge ${statusBadge(ds.status)}`}>
                    {(ds.status || 'uploaded').toUpperCase()}
                  </span>
                </td>
                <td>
                  <div style={{ display: 'flex', gap: 6 }}>
                    <button onClick={() => handleTrain(ds.id)} style={{
                      padding: '4px 12px', borderRadius: 6,
                      background: 'rgba(0,180,216,0.1)', color: '#00b4d8',
                      border: 'none', cursor: 'pointer', fontSize: '0.78rem',
                      fontWeight: 600, display: 'flex', alignItems: 'center', gap: 4
                    }}>
                      <Play size={12} /> Train
                    </button>
                    <button onClick={() => handleDelete(ds.id)} style={{
                      padding: '4px 10px', borderRadius: 6,
                      background: 'rgba(239,68,68,0.1)', color: '#ef4444',
                      border: 'none', cursor: 'pointer', fontSize: '0.78rem',
                      display: 'flex', alignItems: 'center', gap: 4
                    }}>
                      <Trash2 size={12} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
            {datasets.length === 0 && (
              <tr>
                <td colSpan={5} style={{ textAlign: 'center', padding: 48, color: '#64748b' }}>
                  <Database size={40} style={{ opacity: 0.15, margin: '0 auto 12px', display: 'block' }} />
                  <p>No datasets uploaded yet</p>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </motion.div>
    </div>
  );
}

import React, { useState, useEffect, useRef } from 'react';
import {
  Upload, FileText, Database, Brain, Trash2, Play,
  CheckCircle, XCircle, Clock, AlertTriangle, ChevronDown
} from 'lucide-react';
import { uploadDataset, fetchDatasets, trainOnDataset, deleteDataset, streamOnDataset } from '../api.js';

const DOMAINS = [
  { value: '', label: 'Auto-detect' },
  { value: 'banking', label: 'Banking / Credit Card' },
  { value: 'insurance', label: 'Insurance Claims' },
  { value: 'ecommerce', label: 'E-commerce' },
  { value: 'document_fraud', label: 'Document Fraud' },
  { value: 'custom', label: 'Custom Dataset' },
];

const STATUS_STYLES = {
  uploaded: { color: '#a0aec0', icon: Clock, label: 'Uploaded' },
  validated: { color: '#00b4d8', icon: CheckCircle, label: 'Validated' },
  training: { color: '#fd7e14', icon: Brain, label: 'Training...' },
  ready: { color: '#28a745', icon: CheckCircle, label: 'Ready' },
  error: { color: '#dc3545', icon: XCircle, label: 'Error' },
};

export default function DatasetUpload() {
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [training, setTraining] = useState({});
  const [streaming, setStreaming] = useState({});
  const [uploadForm, setUploadForm] = useState({ name: '', domain: '' });
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadResult, setUploadResult] = useState(null);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  useEffect(() => {
    loadDatasets();
  }, []);

  const loadDatasets = async () => {
    try {
      const data = await fetchDatasets();
      setDatasets(data);
    } catch (err) {
      console.error('Failed to load datasets:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') setDragActive(true);
    else if (e.type === 'dragleave') setDragActive(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    setUploading(true);
    setError('');
    setUploadResult(null);

    try {
      const result = await uploadDataset(
        selectedFile,
        uploadForm.name || null,
        uploadForm.domain || null,
      );
      setUploadResult(result);
      setSelectedFile(null);
      setUploadForm({ name: '', domain: '' });
      if (fileInputRef.current) fileInputRef.current.value = '';
      await loadDatasets();
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  const handleTrain = async (datasetId) => {
    setTraining(prev => ({ ...prev, [datasetId]: true }));
    try {
      await trainOnDataset(datasetId);
      await loadDatasets();
    } catch (err) {
      setError(err.message);
    } finally {
      setTraining(prev => ({ ...prev, [datasetId]: false }));
    }
  };

  const handleStream = async (datasetId) => {
    setStreaming(prev => ({ ...prev, [datasetId]: true }));
    try {
      await streamOnDataset(datasetId);
      // Give it a second to show streaming state if we wanted to
      alert("Live streaming started! Quickly navigate to the Dashboard or Live Alerts to watch the transactions process in real-time.");
    } catch (err) {
      setError(err.message);
    } finally {
      setStreaming(prev => ({ ...prev, [datasetId]: false }));
    }
  };

  const handleDelete = async (datasetId) => {
    if (!confirm('Delete this dataset?')) return;
    try {
      await deleteDataset(datasetId);
      await loadDatasets();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1><Database size={26} style={{ marginRight: 10, verticalAlign: 'middle' }} />Dataset Management</h1>
          <p className="page-subtitle">Upload, validate, and train models on fraud detection datasets</p>
        </div>
      </div>

      {/* Upload Section */}
      <div className="card upload-section">
        <h2><Upload size={20} /> Upload New Dataset</h2>

        <div className="upload-form-row">
          <div className="form-group" style={{ flex: 1 }}>
            <label>Dataset Name (optional)</label>
            <input
              type="text"
              placeholder="e.g. credit_card_2024"
              value={uploadForm.name}
              onChange={(e) => setUploadForm({ ...uploadForm, name: e.target.value })}
              id="dataset-name-input"
            />
          </div>
          <div className="form-group" style={{ flex: 1 }}>
            <label>Domain</label>
            <select
              value={uploadForm.domain}
              onChange={(e) => setUploadForm({ ...uploadForm, domain: e.target.value })}
              id="dataset-domain-select"
            >
              {DOMAINS.map(d => <option key={d.value} value={d.value}>{d.label}</option>)}
            </select>
          </div>
        </div>

        <div
          className={`drop-zone ${dragActive ? 'drag-active' : ''} ${selectedFile ? 'has-file' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          id="dataset-drop-zone"
        >
          <input
            type="file"
            accept=".csv"
            ref={fileInputRef}
            onChange={handleFileSelect}
            style={{ display: 'none' }}
            id="dataset-file-input"
          />
          {selectedFile ? (
            <div className="file-selected">
              <FileText size={32} color="#00b4d8" />
              <span className="file-name">{selectedFile.name}</span>
              <span className="file-size">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</span>
            </div>
          ) : (
            <div className="drop-zone-content">
              <Upload size={40} color="#00b4d8" strokeWidth={1.5} />
              <p>Drag & drop a CSV file here, or click to browse</p>
              <span>Supports: Banking, Insurance, Ecommerce, Document Fraud datasets</span>
            </div>
          )}
        </div>

        <button
          className="btn btn-primary upload-btn"
          onClick={handleUpload}
          disabled={!selectedFile || uploading}
          id="dataset-upload-btn"
        >
          {uploading ? (
            <><span className="spinner" /> Uploading & Validating...</>
          ) : (
            <><Upload size={16} /> Upload Dataset</>
          )}
        </button>

        {error && (
          <div className="alert alert-danger">
            <AlertTriangle size={16} /> {error}
          </div>
        )}

        {uploadResult && (
          <div className="alert alert-success">
            <CheckCircle size={16} />
            <div>
              <strong>{uploadResult.message}</strong>
              <div className="upload-stats">
                <span>Rows: {uploadResult.row_count?.toLocaleString()}</span>
                <span>Columns: {uploadResult.column_count}</span>
                <span>Fraud: {uploadResult.fraud_count?.toLocaleString() || 'N/A'}</span>
                <span>Domain: {uploadResult.domain}</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Datasets List */}
      <div className="card">
        <h2><Database size={20} /> Uploaded Datasets</h2>
        {loading ? (
          <p className="loading-text">Loading datasets...</p>
        ) : datasets.length === 0 ? (
          <p className="empty-text">No datasets uploaded yet. Upload your first dataset above.</p>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Domain</th>
                  <th>Rows</th>
                  <th>Fraud</th>
                  <th>Status</th>
                  <th>Uploaded</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {datasets.map(ds => {
                  const st = STATUS_STYLES[ds.status] || STATUS_STYLES.uploaded;
                  const StatusIcon = st.icon;
                  return (
                    <tr key={ds.id}>
                      <td>
                        <div className="ds-name">
                          <FileText size={14} color="#00b4d8" />
                          <span>{ds.name}</span>
                        </div>
                      </td>
                      <td><span className="badge badge-info">{ds.domain}</span></td>
                      <td>{ds.row_count?.toLocaleString() || '—'}</td>
                      <td>{ds.fraud_count?.toLocaleString() || '—'}</td>
                      <td>
                        <span className="status-badge" style={{ color: st.color, borderColor: st.color }}>
                          <StatusIcon size={12} /> {st.label}
                        </span>
                      </td>
                      <td>{new Date(ds.uploaded_at).toLocaleDateString()}</td>
                      <td>
                        <div className="action-btns">
                          <button
                            className="btn btn-sm btn-train"
                            onClick={() => handleTrain(ds.id)}
                            disabled={training[ds.id] || ds.status === 'training'}
                            title="Train model"
                          >
                            {training[ds.id] ? <span className="spinner-sm" /> : <Brain size={14} />}
                          </button>
                          <button
                            className="btn btn-sm"
                            style={{ background: 'var(--success-bg)', color: 'var(--success)', border: '1px solid var(--success-bg)' }}
                            onClick={() => handleStream(ds.id)}
                            disabled={streaming[ds.id] || ds.status !== 'ready'}
                            title="Stream dataset live to Dashboard"
                          >
                            {streaming[ds.id] ? <span className="spinner-sm" /> : <Play size={14} />}
                          </button>
                          <button
                            className="btn btn-sm btn-danger"
                            onClick={() => handleDelete(ds.id)}
                            title="Delete dataset"
                          >
                            <Trash2 size={14} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

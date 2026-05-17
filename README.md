# 🛡️ AI Fraud Detection System v3.0

A production-grade, AI-powered fraud detection platform built with **FastAPI**, **React**, and **NVIDIA AI** inference. Supports multi-domain dataset upload, real-time fraud analysis, role-based access control, and automated ML model training.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React + Vite)               │
│  ┌──────────┬──────────┬──────────┬──────────┬────────┐ │
│  │Dashboard │Transact. │Alerts   │Simulation│Datasets│ │
│  │          │          │(WebSocket)│         │Upload  │ │
│  └──────────┴──────────┴──────────┴──────────┴────────┘ │
│                         ↕ REST API / WebSocket           │
├─────────────────────────────────────────────────────────┤
│                    Backend (FastAPI)                      │
│  ┌──────────┬──────────┬──────────┬──────────┐          │
│  │Auth (JWT)│Fraud     │Dataset   │Analytics │          │
│  │RBAC      │Engine    │Pipeline  │Dashboard │          │
│  └──────────┴──────────┴──────────┴──────────┘          │
│  ┌──────────┬──────────┬──────────┬──────────┐          │
│  │NVIDIA AI │Behavioral│Report    │Model     │          │
│  │Explainer │Analyzer  │Generator │Trainer   │          │
│  └──────────┴──────────┴──────────┴──────────┘          │
├─────────────────────────────────────────────────────────┤
│  SQLite (dev) / PostgreSQL (prod) │ NVIDIA NIM API       │
└─────────────────────────────────────────────────────────┘
```

---

## ✨ Features

### Core Detection
- **Hybrid Fraud Engine**: Rules + Anomaly Detection (Isolation Forest) + ML Classification (XGBoost, Random Forest)
- **Risk Score Engine**: 0-100 scoring based on amount, location, device, and frequency factors
- **Real-time Alerts**: WebSocket-based live fraud alert stream

### AI-Powered
- **NVIDIA AI Explainer**: Natural language fraud explanations via NVIDIA NIM inference API
- **Behavioral Analysis**: Detects location switching, device switching, frequency spikes, timing anomalies
- **PDF Report Generator**: Professional investigation reports with AI-powered explanation sections

### Data Management
- **Multi-Domain Dataset Upload**: Supports banking, insurance, ecommerce, and document fraud datasets
- **Auto Schema Detection**: Automatically maps columns using `dataset_schema.json`
- **Training Pipeline**: Upload → Validate → Preprocess → Train → Evaluate → Save

### Security
- **JWT Authentication**: Register/Login with token-based auth
- **Role-Based Access Control (RBAC)**:
  - **Admin**: Full access — upload datasets, train models, view analytics
  - **Analyst**: View alerts, generate reports, explain fraud
  - **User**: View own transactions

### Monitoring
- **7 Log Categories**: app, predictions, alerts, errors, reports, uploads, training
- **Rotating File Handlers**: Auto-rotation at 10MB per log file

---

## 📁 Project Structure

```
AI-Fraud-Detection-main/
├── backend/
│   ├── main.py                  # FastAPI app entrypoint
│   ├── config.py                # App configuration
│   ├── database.py              # Async SQLAlchemy engine
│   ├── seed_data.py             # Database seeder
│   ├── dataset_schema.json      # Multi-domain schema mapping config
│   ├── celery_worker.py         # Async task worker
│   ├── routes/
│   │   ├── auth.py              # POST /register, /login, GET /profile
│   │   ├── transactions.py      # Transaction CRUD + fraud analysis
│   │   ├── users.py             # User management
│   │   ├── fraud_intelligence.py # Explain fraud, reports, behavioral analysis
│   │   ├── analytics.py         # Dashboard stats, charts
│   │   └── datasets.py          # Dataset upload, training trigger
│   ├── services/
│   │   ├── fraud_engine.py      # Hybrid detection engine
│   │   ├── nvidia_ai_service.py # NVIDIA NIM inference client
│   │   ├── model_trainer.py     # ML training pipeline
│   │   ├── report_generator.py  # PDF report generation
│   │   ├── schema_mapper.py     # Dataset schema auto-mapping
│   │   ├── behavioral_analyzer.py # Behavioral anomaly detection
│   │   └── websocket_manager.py # Real-time alert broadcasting
│   ├── models/
│   │   └── database_models.py   # SQLAlchemy ORM (7 tables)
│   ├── schemas/
│   │   └── schemas.py           # Pydantic request/response models
│   ├── utils/
│   │   ├── auth.py              # JWT + bcrypt + RBAC utilities
│   │   └── logging_config.py    # Multi-handler logging setup
│   ├── ml_models/               # Trained model files (.pkl)
│   ├── datasets/                # Uploaded dataset CSV files
│   └── reports/                 # Generated PDF reports
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Root component with auth routing
│   │   ├── api.js               # API service layer (auth + all endpoints)
│   │   ├── main.jsx             # React entry point
│   │   ├── index.css            # Complete design system
│   │   ├── components/
│   │   │   └── Sidebar.jsx      # Navigation with role-based filtering
│   │   └── pages/
│   │       ├── Login.jsx        # Auth page (register/login)
│   │       ├── Dashboard.jsx    # Analytics dashboard
│   │       ├── Transactions.jsx # Transaction listing
│   │       ├── LiveAlerts.jsx   # Real-time WebSocket alerts
│   │       ├── FraudSimulation.jsx # Transaction simulator
│   │       ├── FraudExplainer.jsx  # AI explanation UI
│   │       ├── Reports.jsx      # PDF report management
│   │       └── DatasetUpload.jsx # Dataset upload & training
│   └── vite.config.js           # Vite dev server with proxy
├── data/                        # Training data directory
├── logs/                        # Application logs
├── .env                         # Environment variables
├── requirements.txt             # Python dependencies
└── README.md
```

---

## 🚀 Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+
- NVIDIA API Key (from [build.nvidia.com](https://build.nvidia.com))

### 1. Backend Setup

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Delete old database (required for schema upgrade)
del fraud_detection.db         # Windows
# rm fraud_detection.db        # Mac/Linux

# Seed the database with demo data
python -m backend.seed_data

# Start the backend server
uvicorn backend.main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### 3. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API docs**: http://localhost:8000/docs
- **Default Logins**:
  - Admin: `admin` / `admin123`
  - Analyst: `analyst` / `analyst123`
  - User: `priya_sharma` / `priya123`

---

## 📡 API Documentation

### Authentication
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register` | Register new user | No |
| POST | `/api/auth/login` | Login and get JWT | No |
| GET | `/api/auth/profile` | Get current user profile | Yes |

### Transactions
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/transactions/` | Create transaction + fraud analysis | No |
| GET | `/api/transactions/` | List transactions | No |
| GET | `/api/transactions/{id}` | Get single transaction | No |
| POST | `/api/transactions/simulate` | Simulate without persisting | No |

### Fraud Intelligence
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/explain-fraud` | AI-powered fraud explanation | No |
| GET | `/api/generate-report/{id}` | Generate PDF report | No |
| GET | `/api/download-report/{id}` | Download PDF report | No |
| GET | `/api/behavioral-analysis/{user_id}` | Behavioral anomaly check | No |

### Datasets
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/datasets/upload` | Upload CSV dataset | No |
| GET | `/api/datasets/` | List all datasets | No |
| POST | `/api/datasets/train/{id}` | Train models on dataset | No |
| DELETE | `/api/datasets/{id}` | Delete dataset | No |

### Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analytics/dashboard-stats` | Dashboard statistics |
| GET | `/api/analytics/frauds-per-hour` | Fraud count by hour |
| GET | `/api/analytics/frauds-per-location` | Fraud by geography |
| GET | `/api/analytics/frauds-per-user` | Top fraud users |
| GET | `/api/analytics/confidence-distribution` | Model confidence |
| GET | `/api/analytics/alerts` | Recent alerts |
| GET | `/api/analytics/model-training` | Trigger model training |

---

## 📊 Dataset Upload Instructions

### Supported Formats

The system supports multiple fraud detection dataset types:

| Domain | Label Column | Amount Column | Example |
|--------|-------------|---------------|---------|
| Banking | `Class` | `Amount` | Kaggle Credit Card dataset |
| Insurance | `fraud_reported` | `total_claim_amount` | Insurance fraud dataset |
| Ecommerce | `is_fraud` | `purchase_value` | Online transaction fraud |
| Document | `is_forged` | `document_value` | Document fraud detection |
| Custom | (user-defined) | (user-defined) | Any CSV with binary labels |

### Upload Steps

1. Navigate to **Datasets** page (Admin only)
2. Select domain or leave as "Auto-detect"
3. Drag & drop your CSV file (max 500MB)
4. System validates schema and shows stats
5. Click **Train** to trigger model training

### Schema Configuration

Edit `backend/dataset_schema.json` to add new dataset formats:

```json
{
  "my_custom_domain": {
    "label_column": "fraud_flag",
    "amount_column": "txn_amount",
    "timestamp_column": "txn_date",
    "location_column": "city",
    "description": "My custom fraud dataset"
  }
}
```

---

## 🔒 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `USE_SQLITE` | Use SQLite for local dev | `true` |
| `DATABASE_URL` | PostgreSQL connection string | — |
| `NVIDIA_API_KEY` | NVIDIA NIM API key | — |
| `NVIDIA_MODEL` | NVIDIA model name | `meta/llama-3.1-8b-instruct` |
| `SECRET_KEY` | JWT signing secret | (change in production!) |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `JWT_EXPIRATION_HOURS` | Token expiry | `24` |
| `CORS_ORIGINS` | Allowed origins | `http://localhost:5173,...` |

---

## 🧠 Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite 5, Recharts, Lucide Icons |
| Backend | FastAPI, Uvicorn, SQLAlchemy (async) |
| AI/ML | XGBoost, Scikit-learn, NVIDIA NIM API |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Auth | JWT (PyJWT), bcrypt (Passlib) |
| Reports | ReportLab (PDF generation) |
| Real-time | WebSockets |

---

## 👥 Team

- **Ganesh Patne** — Developer
- **Sujal Surve** — Developer
- **Aditya Tambadkar** — Developer

---

*Powered by NVIDIA AI • Built with FastAPI & React*

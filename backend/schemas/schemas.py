"""
Pydantic schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ─── Authentication Schemas ───────────────────────────────────
class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=100)
    email: str
    password: str = Field(..., min_length=6)
    role: Optional[str] = "user"  # admin, analyst, user
    device_fingerprint: Optional[str] = None
    location: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str
    role: str
    expires_in: int


class ProfileResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    device_fingerprint: Optional[str]
    location: Optional[str]
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


# ─── User Schemas ──────────────────────────────────────────────
class UserCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=100)
    email: str
    device_fingerprint: Optional[str] = None
    location: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    device_fingerprint: Optional[str]
    location: Optional[str]
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


# ─── Transaction Schemas ──────────────────────────────────────
class TransactionCreate(BaseModel):
    user_id: str
    amount: float = Field(..., gt=0)
    location: Optional[str] = None
    device_fingerprint: Optional[str] = None
    merchant: Optional[str] = None
    category: Optional[str] = None
    features_json: Optional[str] = None  # JSON string of V1-V28


class TransactionResponse(BaseModel):
    id: str
    user_id: str
    amount: float
    location: Optional[str]
    device_fingerprint: Optional[str]
    merchant: Optional[str]
    category: Optional[str]
    is_fraud: bool
    risk_score: float
    confidence: float
    timestamp: datetime

    class Config:
        from_attributes = True


# ─── Fraud Analysis Result ────────────────────────────────────
class FraudAnalysisResult(BaseModel):
    transaction_id: str
    is_fraud: bool
    risk_score: float = Field(..., ge=0, le=100)
    confidence: float = Field(..., ge=0, le=1)
    fraud_type: Optional[str] = None
    reason: str
    risk_factors: dict


# ─── Risk Score Schemas ────────────────────────────────────────
class RiskScoreResponse(BaseModel):
    score: float
    amount_factor: float
    location_factor: float
    frequency_factor: float
    device_factor: float
    calculated_at: datetime

    class Config:
        from_attributes = True


# ─── Alert Schemas ─────────────────────────────────────────────
class AlertResponse(BaseModel):
    id: str
    user_id: str
    transaction_id: Optional[str]
    severity: str
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Explain Fraud Request/Response ───────────────────────────
class ExplainFraudRequest(BaseModel):
    transaction_id: str
    question: Optional[str] = "Why was this transaction flagged?"


class ExplainFraudResponse(BaseModel):
    transaction_id: str
    explanation: str
    risk_factors: List[str]
    confidence_score: float
    behavior_mismatch: List[str]


# ─── Simulation Schemas ───────────────────────────────────────
class SimulationRequest(BaseModel):
    user_id: str
    amount: float = Field(..., gt=0)
    location: Optional[str] = "New York, US"
    device_fingerprint: Optional[str] = "device-default"
    merchant: Optional[str] = "Online Store"
    category: Optional[str] = "shopping"


class SimulationResponse(BaseModel):
    is_fraud: bool
    risk_score: float
    confidence: float
    fraud_type: Optional[str]
    reason: str
    risk_factors: dict


# ─── Report Schemas ────────────────────────────────────────────
class ReportResponse(BaseModel):
    id: str
    transaction_id: str
    file_path: str
    generated_at: datetime

    class Config:
        from_attributes = True


# ─── Dataset Upload Schemas ───────────────────────────────────
class DatasetUploadResponse(BaseModel):
    id: str
    name: str
    original_filename: str
    domain: str
    row_count: Optional[int]
    column_count: Optional[int]
    fraud_count: Optional[int]
    legitimate_count: Optional[int]
    label_column: Optional[str]
    status: str
    uploaded_at: datetime
    message: str


class DatasetListResponse(BaseModel):
    id: str
    name: str
    original_filename: str
    domain: str
    row_count: Optional[int]
    fraud_count: Optional[int]
    status: str
    uploaded_at: datetime

    class Config:
        from_attributes = True


class DatasetTrainResponse(BaseModel):
    dataset_id: str
    status: str
    results: Optional[dict] = None
    message: str


# ─── Dashboard Analytics ──────────────────────────────────────
class DashboardStats(BaseModel):
    total_transactions: int
    total_fraudulent: int
    total_legitimate: int
    fraud_rate: float
    avg_risk_score: float
    high_risk_users: int
    alerts_today: int


class FraudByHour(BaseModel):
    hour: int
    count: int


class FraudByLocation(BaseModel):
    location: str
    count: int


class FraudByUser(BaseModel):
    user_id: str
    username: str
    count: int


class ConfidenceDistribution(BaseModel):
    bucket: str
    count: int

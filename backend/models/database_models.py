"""
SQLAlchemy ORM models for the fraud detection database.
Tables: users, transactions, fraud_logs, risk_scores, alerts, reports, datasets
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Float, Integer, Boolean, DateTime, Text, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from backend.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_uuid)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=True)
    role = Column(String(20), nullable=False, default="user")  # admin, analyst, user
    device_fingerprint = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    transactions = relationship("Transaction", back_populates="user", lazy="selectin")
    alerts = relationship("Alert", back_populates="user", lazy="selectin")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    location = Column(String(255), nullable=True)
    device_fingerprint = Column(String(255), nullable=True)
    merchant = Column(String(255), nullable=True)
    category = Column(String(100), nullable=True)
    is_fraud = Column(Boolean, default=False)
    risk_score = Column(Float, default=0.0)
    confidence = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # PCA features V1-V28 stored as a JSON-compatible text (for ML)
    features_json = Column(Text, nullable=True)

    user = relationship("User", back_populates="transactions")
    fraud_log = relationship("FraudLog", back_populates="transaction", uselist=False, lazy="selectin")
    risk_score_record = relationship("RiskScore", back_populates="transaction", uselist=False, lazy="selectin")
    report = relationship("Report", back_populates="transaction", uselist=False, lazy="selectin")

    __table_args__ = (
        Index("idx_transactions_user_time", "user_id", "timestamp"),
    )


class FraudLog(Base):
    __tablename__ = "fraud_logs"

    id = Column(String, primary_key=True, default=gen_uuid)
    transaction_id = Column(String, ForeignKey("transactions.id"), nullable=False, unique=True)
    fraud_type = Column(String(100), nullable=True)  # rule_based, anomaly, classification
    classification_result = Column(String(50), nullable=True)
    reason = Column(Text, nullable=True)
    model_version = Column(String(50), nullable=True)
    detected_at = Column(DateTime, default=datetime.utcnow)

    transaction = relationship("Transaction", back_populates="fraud_log")


class RiskScore(Base):
    __tablename__ = "risk_scores"

    id = Column(String, primary_key=True, default=gen_uuid)
    transaction_id = Column(String, ForeignKey("transactions.id"), nullable=False, unique=True)
    score = Column(Float, nullable=False)  # 0 – 100
    amount_factor = Column(Float, default=0.0)
    location_factor = Column(Float, default=0.0)
    frequency_factor = Column(Float, default=0.0)
    device_factor = Column(Float, default=0.0)
    calculated_at = Column(DateTime, default=datetime.utcnow)

    transaction = relationship("Transaction", back_populates="risk_score_record")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    transaction_id = Column(String, ForeignKey("transactions.id"), nullable=True)
    severity = Column(String(20), nullable=False, default="medium")  # low, medium, high, critical
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="alerts")


class Report(Base):
    __tablename__ = "reports"

    id = Column(String, primary_key=True, default=gen_uuid)
    transaction_id = Column(String, ForeignKey("transactions.id"), nullable=False, unique=True)
    file_path = Column(String(500), nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)

    transaction = relationship("Transaction", back_populates="report")


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String(255), nullable=False)
    original_filename = Column(String(500), nullable=False)
    file_path = Column(String(500), nullable=False)
    domain = Column(String(50), nullable=False, default="banking")  # banking, insurance, ecommerce, etc.
    row_count = Column(Integer, nullable=True)
    column_count = Column(Integer, nullable=True)
    fraud_count = Column(Integer, nullable=True)
    legitimate_count = Column(Integer, nullable=True)
    label_column = Column(String(100), nullable=True)
    amount_column = Column(String(100), nullable=True)
    timestamp_column = Column(String(100), nullable=True)
    status = Column(String(20), nullable=False, default="uploaded")  # uploaded, validated, preprocessing, training, ready, error
    error_message = Column(Text, nullable=True)
    uploaded_by = Column(String, ForeignKey("users.id"), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    trained_at = Column(DateTime, nullable=True)

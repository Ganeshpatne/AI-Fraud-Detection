"""
Transaction & Fraud Detection API routes.
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from backend.database import get_db
from backend.models.database_models import (
    User, Transaction, FraudLog, RiskScore, Alert
)
from backend.schemas.schemas import (
    TransactionCreate, TransactionResponse, FraudAnalysisResult,
    SimulationRequest, SimulationResponse
)
from backend.services.fraud_engine import fraud_engine
from backend.services.websocket_manager import ws_manager

logger = logging.getLogger("fraud_detection")
pred_logger = logging.getLogger("fraud_detection.predictions")
alert_logger = logging.getLogger("fraud_detection.alerts")

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])


@router.post("/", response_model=TransactionResponse)
async def create_transaction(txn: TransactionCreate, db: AsyncSession = Depends(get_db)):
    """Create a new transaction and run fraud analysis."""

    # Fetch user info for comparison
    user = None
    result = await db.execute(select(User).where(User.id == txn.user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail=f"User {txn.user_id} not found")

    # Count recent transactions (last 1 hour) for frequency spike detection
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    count_result = await db.execute(
        select(func.count(Transaction.id)).where(
            and_(
                Transaction.user_id == txn.user_id,
                Transaction.timestamp >= one_hour_ago
            )
        )
    )
    recent_txn_count = count_result.scalar() or 0

    # ── Run fraud detection engine ──
    analysis = fraud_engine.analyze(
        amount=txn.amount,
        user_location=user.location,
        txn_location=txn.location,
        user_device=user.device_fingerprint,
        txn_device=txn.device_fingerprint,
        recent_txn_count=recent_txn_count,
        features_json=txn.features_json,
    )

    # ── Persist transaction ──
    new_txn = Transaction(
        user_id=txn.user_id,
        amount=txn.amount,
        location=txn.location,
        device_fingerprint=txn.device_fingerprint,
        merchant=txn.merchant,
        category=txn.category,
        is_fraud=analysis["is_fraud"],
        risk_score=analysis["risk_score"],
        confidence=analysis["confidence"],
        features_json=txn.features_json,
    )
    db.add(new_txn)
    await db.flush()

    # ── Persist fraud log ──
    fraud_log = FraudLog(
        transaction_id=new_txn.id,
        fraud_type=analysis["fraud_type"],
        classification_result="fraudulent" if analysis["is_fraud"] else "legitimate",
        reason=analysis["reason"],
        model_version="v2.0",
    )
    db.add(fraud_log)

    # ── Persist risk score breakdown ──
    risk_record = RiskScore(
        transaction_id=new_txn.id,
        score=analysis["risk_score"],
        amount_factor=analysis["risk_factors"]["amount_factor"],
        location_factor=analysis["risk_factors"]["location_factor"],
        frequency_factor=analysis["risk_factors"]["frequency_factor"],
        device_factor=analysis["risk_factors"]["device_factor"],
    )
    db.add(risk_record)

    # ── Create alert if fraud detected ──
    if analysis["is_fraud"]:
        severity = "critical" if analysis["risk_score"] >= 70 else (
            "high" if analysis["risk_score"] >= 50 else "medium"
        )
        alert = Alert(
            user_id=txn.user_id,
            transaction_id=new_txn.id,
            severity=severity,
            message=f"Fraud detected: {analysis['reason'][:200]}",
        )
        db.add(alert)
        alert_logger.warning(
            "FRAUD ALERT [%s] user=%s txn=%s amount=%.2f score=%.1f",
            severity.upper(), txn.user_id, new_txn.id, txn.amount, analysis["risk_score"]
        )

        # ── Broadcast via WebSocket ──
        await ws_manager.broadcast_alert({
            "transaction_id": new_txn.id,
            "user_id": txn.user_id,
            "amount": txn.amount,
            "risk_score": analysis["risk_score"],
            "severity": severity,
            "reason": analysis["reason"][:200],
            "fraud_type": analysis["fraud_type"],
        })

    await db.commit()
    await db.refresh(new_txn)

    pred_logger.info(
        "Transaction %s analyzed: fraud=%s score=%.1f confidence=%.4f",
        new_txn.id, analysis["is_fraud"], analysis["risk_score"], analysis["confidence"]
    )

    return new_txn


@router.get("/", response_model=list[TransactionResponse])
async def list_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    fraud_only: bool = Query(False),
    legit_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
):
    """List transactions with optional fraud/legit filter."""
    query = select(Transaction).order_by(Transaction.timestamp.desc())
    if fraud_only:
        query = query.where(Transaction.is_fraud == True)
    elif legit_only:
        query = query.where(Transaction.is_fraud == False)
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: str, db: AsyncSession = Depends(get_db)):
    """Get a single transaction by ID."""
    result = await db.execute(
        select(Transaction).where(Transaction.id == transaction_id)
    )
    txn = result.scalar_one_or_none()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return txn


@router.post("/simulate", response_model=SimulationResponse)
async def simulate_transaction(sim: SimulationRequest, db: AsyncSession = Depends(get_db)):
    """
    Simulate a transaction without persisting it.
    Returns fraud prediction instantly.
    """
    # Fetch user
    result = await db.execute(select(User).where(User.id == sim.user_id))
    user = result.scalar_one_or_none()

    user_location = user.location if user else None
    user_device = user.device_fingerprint if user else None

    # Count recent transactions
    recent_count = 0
    if user:
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        count_result = await db.execute(
            select(func.count(Transaction.id)).where(
                and_(
                    Transaction.user_id == sim.user_id,
                    Transaction.timestamp >= one_hour_ago
                )
            )
        )
        recent_count = count_result.scalar() or 0

    analysis = fraud_engine.analyze(
        amount=sim.amount,
        user_location=user_location,
        txn_location=sim.location,
        user_device=user_device,
        txn_device=sim.device_fingerprint,
        recent_txn_count=recent_count,
    )

    # Broadcast simulation activity via WebSocket
    await ws_manager.broadcast_activity({
        "type": "simulation",
        "user_id": sim.user_id,
        "amount": sim.amount,
        "result": "fraudulent" if analysis["is_fraud"] else "legitimate",
        "risk_score": analysis["risk_score"],
    })

    return SimulationResponse(**analysis)

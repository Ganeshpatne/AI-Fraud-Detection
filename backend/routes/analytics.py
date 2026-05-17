"""
Dashboard analytics API routes.
Charts: frauds per hour, per location, per user, confidence distribution.
"""
import logging
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, case, text, literal_column

from backend.config import USE_SQLITE
from backend.database import get_db
from backend.models.database_models import Transaction, Alert, User, RiskScore
from backend.schemas.schemas import (
    DashboardStats, FraudByHour, FraudByLocation,
    FraudByUser, ConfidenceDistribution
)

logger = logging.getLogger("fraud_detection")

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/dashboard-stats", response_model=DashboardStats)
async def dashboard_stats(db: AsyncSession = Depends(get_db)):
    """Get high-level dashboard statistics."""
    total_result = await db.execute(select(func.count(Transaction.id)))
    total = total_result.scalar() or 0

    fraud_result = await db.execute(
        select(func.count(Transaction.id)).where(Transaction.is_fraud == True)
    )
    fraudulent = fraud_result.scalar() or 0
    legitimate = total - fraudulent
    fraud_rate = (fraudulent / total * 100) if total > 0 else 0.0

    avg_result = await db.execute(select(func.avg(Transaction.risk_score)))
    avg_risk = avg_result.scalar() or 0.0

    high_risk_result = await db.execute(
        select(func.count(func.distinct(Transaction.user_id))).where(
            Transaction.is_fraud == True
        )
    )
    high_risk_users = high_risk_result.scalar() or 0

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    alerts_result = await db.execute(
        select(func.count(Alert.id)).where(Alert.created_at >= today_start)
    )
    alerts_today = alerts_result.scalar() or 0

    return DashboardStats(
        total_transactions=total,
        total_fraudulent=fraudulent,
        total_legitimate=legitimate,
        fraud_rate=round(fraud_rate, 2),
        avg_risk_score=round(float(avg_risk), 2),
        high_risk_users=high_risk_users,
        alerts_today=alerts_today,
    )


def _hour_expr():
    """Return the SQL expression for extracting hour, compatible with both SQLite and PG."""
    if USE_SQLITE:
        return func.cast(func.strftime("%H", Transaction.timestamp), Integer)
    else:
        from sqlalchemy import extract
        return extract("hour", Transaction.timestamp)


from sqlalchemy import Integer


@router.get("/frauds-per-hour", response_model=list[FraudByHour])
async def frauds_per_hour(
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db),
):
    """Get fraud count per hour for the last N hours."""
    since = datetime.utcnow() - timedelta(hours=hours)
    hour_col = _hour_expr().label("hour")

    result = await db.execute(
        select(
            hour_col,
            func.count(Transaction.id).label("count"),
        )
        .where(
            and_(
                Transaction.is_fraud == True,
                Transaction.timestamp >= since,
            )
        )
        .group_by(hour_col)
        .order_by(hour_col)
    )

    rows = result.all()
    return [FraudByHour(hour=int(r.hour), count=r.count) for r in rows]


@router.get("/frauds-per-location", response_model=list[FraudByLocation])
async def frauds_per_location(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Get fraud count per location."""
    result = await db.execute(
        select(
            Transaction.location.label("location"),
            func.count(Transaction.id).label("count"),
        )
        .where(
            and_(
                Transaction.is_fraud == True,
                Transaction.location.isnot(None),
            )
        )
        .group_by(Transaction.location)
        .order_by(func.count(Transaction.id).desc())
        .limit(limit)
    )

    rows = result.all()
    return [FraudByLocation(location=r.location or "Unknown", count=r.count) for r in rows]


@router.get("/frauds-per-user", response_model=list[FraudByUser])
async def frauds_per_user(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Get top users by fraud count."""
    result = await db.execute(
        select(
            Transaction.user_id,
            User.username,
            func.count(Transaction.id).label("count"),
        )
        .join(User, User.id == Transaction.user_id)
        .where(Transaction.is_fraud == True)
        .group_by(Transaction.user_id, User.username)
        .order_by(func.count(Transaction.id).desc())
        .limit(limit)
    )

    rows = result.all()
    return [FraudByUser(user_id=r.user_id, username=r.username, count=r.count) for r in rows]


@router.get("/confidence-distribution", response_model=list[ConfidenceDistribution])
async def confidence_distribution(db: AsyncSession = Depends(get_db)):
    """Get distribution of model confidence scores."""
    result = await db.execute(
        select(
            case(
                (Transaction.confidence < 0.2, "0-20%"),
                (Transaction.confidence < 0.4, "20-40%"),
                (Transaction.confidence < 0.6, "40-60%"),
                (Transaction.confidence < 0.8, "60-80%"),
                else_="80-100%",
            ).label("bucket"),
            func.count(Transaction.id).label("count"),
        )
        .where(Transaction.is_fraud == True)
        .group_by("bucket")
        .order_by("bucket")
    )

    rows = result.all()
    return [ConfidenceDistribution(bucket=r.bucket, count=r.count) for r in rows]


@router.get("/alerts", response_model=list)
async def recent_alerts(
    limit: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
):
    """Get recent alerts."""
    query = select(Alert).order_by(Alert.created_at.desc())
    if unread_only:
        query = query.where(Alert.is_read == False)
    query = query.limit(limit)

    result = await db.execute(query)
    alerts = result.scalars().all()

    return [
        {
            "id": a.id,
            "user_id": a.user_id,
            "transaction_id": a.transaction_id,
            "severity": a.severity,
            "message": a.message,
            "is_read": a.is_read,
            "created_at": a.created_at.isoformat(),
        }
        for a in alerts
    ]


@router.get("/model-training")
async def train_models():
    """Trigger model training pipeline (for admin use)."""
    from backend.services.model_trainer import model_trainer
    try:
        results = model_trainer.train_all()
        return {"status": "success", "results": results}
    except FileNotFoundError:
        return {
            "status": "error",
            "message": "Training data not found. Place creditcard.csv in data/ directory."
        }
    except Exception as e:
        logger.error("Model training failed: %s", str(e))
        return {"status": "error", "message": str(e)}

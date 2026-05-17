"""
Behavioral Analysis Module.
Detects anomalies in user behavior:
  - Login timing changes
  - Location switching patterns
  - Device switching patterns
  - Transaction frequency spikes
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from backend.models.database_models import Transaction, User

logger = logging.getLogger("fraud_detection.predictions")


class BehavioralAnalyzer:
    """Analyzes user transaction behavior to detect anomalous patterns."""

    # ── Thresholds ─────────────────────────────────────────────
    LOCATION_SWITCH_THRESHOLD = 3       # > 3 unique locations in 24h = suspicious
    DEVICE_SWITCH_THRESHOLD = 2         # > 2 unique devices in 24h = suspicious
    FREQUENCY_SPIKE_MULTIPLIER = 3.0    # 3x average frequency = spike
    TIME_WINDOW_HOURS = 24
    BASELINE_WINDOW_DAYS = 30

    async def analyze_user_behavior(
        self, user_id: str, db: AsyncSession
    ) -> dict:
        """
        Run full behavioral analysis for a user.
        Returns dict with anomaly flags and details.
        """
        anomalies = []
        risk_contribution = 0.0

        # Get user
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return {"anomalies": [], "risk_contribution": 0.0, "summary": "User not found"}

        # Run each check
        location_result = await self._check_location_switching(user_id, db)
        if location_result["is_anomalous"]:
            anomalies.append(location_result)
            risk_contribution += location_result["risk_score"]

        device_result = await self._check_device_switching(user_id, db)
        if device_result["is_anomalous"]:
            anomalies.append(device_result)
            risk_contribution += device_result["risk_score"]

        frequency_result = await self._check_frequency_spike(user_id, db)
        if frequency_result["is_anomalous"]:
            anomalies.append(frequency_result)
            risk_contribution += frequency_result["risk_score"]

        timing_result = await self._check_timing_anomaly(user_id, db)
        if timing_result["is_anomalous"]:
            anomalies.append(timing_result)
            risk_contribution += timing_result["risk_score"]

        summary_parts = [a["description"] for a in anomalies]
        summary = "; ".join(summary_parts) if summary_parts else "No behavioral anomalies detected"

        result = {
            "user_id": user_id,
            "anomalies": anomalies,
            "anomaly_count": len(anomalies),
            "risk_contribution": min(risk_contribution, 100.0),
            "summary": summary,
            "analyzed_at": datetime.utcnow().isoformat(),
        }

        if anomalies:
            logger.warning(
                "Behavioral anomalies for user %s: %d detected (risk: %.1f)",
                user_id, len(anomalies), risk_contribution
            )
        else:
            logger.info("No behavioral anomalies for user %s", user_id)

        return result

    async def _check_location_switching(self, user_id: str, db: AsyncSession) -> dict:
        """Detect rapid location switching."""
        since = datetime.utcnow() - timedelta(hours=self.TIME_WINDOW_HOURS)

        result = await db.execute(
            select(Transaction.location).where(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.timestamp >= since,
                    Transaction.location.isnot(None),
                )
            ).distinct()
        )
        unique_locations = [r[0] for r in result.all()]
        count = len(unique_locations)

        is_anomalous = count > self.LOCATION_SWITCH_THRESHOLD
        risk_score = min(25.0, (count - self.LOCATION_SWITCH_THRESHOLD) * 8.0) if is_anomalous else 0.0

        return {
            "type": "location_switching",
            "is_anomalous": is_anomalous,
            "risk_score": risk_score,
            "description": f"Transactions from {count} different locations in {self.TIME_WINDOW_HOURS}h",
            "details": {"unique_locations": unique_locations, "threshold": self.LOCATION_SWITCH_THRESHOLD},
        }

    async def _check_device_switching(self, user_id: str, db: AsyncSession) -> dict:
        """Detect rapid device switching."""
        since = datetime.utcnow() - timedelta(hours=self.TIME_WINDOW_HOURS)

        result = await db.execute(
            select(Transaction.device_fingerprint).where(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.timestamp >= since,
                    Transaction.device_fingerprint.isnot(None),
                )
            ).distinct()
        )
        unique_devices = [r[0] for r in result.all()]
        count = len(unique_devices)

        is_anomalous = count > self.DEVICE_SWITCH_THRESHOLD
        risk_score = min(20.0, (count - self.DEVICE_SWITCH_THRESHOLD) * 10.0) if is_anomalous else 0.0

        return {
            "type": "device_switching",
            "is_anomalous": is_anomalous,
            "risk_score": risk_score,
            "description": f"Transactions from {count} different devices in {self.TIME_WINDOW_HOURS}h",
            "details": {"unique_devices": unique_devices, "threshold": self.DEVICE_SWITCH_THRESHOLD},
        }

    async def _check_frequency_spike(self, user_id: str, db: AsyncSession) -> dict:
        """Detect transaction frequency spikes vs. baseline."""
        now = datetime.utcnow()
        recent_window = now - timedelta(hours=self.TIME_WINDOW_HOURS)
        baseline_start = now - timedelta(days=self.BASELINE_WINDOW_DAYS)

        # Recent count
        recent_result = await db.execute(
            select(func.count(Transaction.id)).where(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.timestamp >= recent_window,
                )
            )
        )
        recent_count = recent_result.scalar() or 0

        # Baseline average per day
        baseline_result = await db.execute(
            select(func.count(Transaction.id)).where(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.timestamp >= baseline_start,
                    Transaction.timestamp < recent_window,
                )
            )
        )
        baseline_count = baseline_result.scalar() or 0
        avg_daily = baseline_count / max(self.BASELINE_WINDOW_DAYS, 1)

        # Compare
        expected_in_window = avg_daily * (self.TIME_WINDOW_HOURS / 24.0)
        is_anomalous = (recent_count > self.FREQUENCY_SPIKE_MULTIPLIER * max(expected_in_window, 1))
        risk_score = 0.0
        if is_anomalous and expected_in_window > 0:
            ratio = recent_count / expected_in_window
            risk_score = min(25.0, ratio * 5.0)

        return {
            "type": "frequency_spike",
            "is_anomalous": is_anomalous,
            "risk_score": risk_score,
            "description": f"Transaction frequency spike: {recent_count} in {self.TIME_WINDOW_HOURS}h vs avg {expected_in_window:.1f}",
            "details": {
                "recent_count": recent_count,
                "baseline_avg_daily": round(avg_daily, 2),
                "expected_in_window": round(expected_in_window, 2),
                "multiplier_threshold": self.FREQUENCY_SPIKE_MULTIPLIER,
            },
        }

    async def _check_timing_anomaly(self, user_id: str, db: AsyncSession) -> dict:
        """
        Detect unusual transaction timing.
        Compares recent transaction hours against user's typical pattern.
        """
        now = datetime.utcnow()

        # Get recent transactions (last 24h)
        recent_result = await db.execute(
            select(Transaction.timestamp).where(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.timestamp >= now - timedelta(hours=self.TIME_WINDOW_HOURS),
                )
            )
        )
        recent_timestamps = [r[0] for r in recent_result.all()]

        if not recent_timestamps:
            return {
                "type": "timing_anomaly",
                "is_anomalous": False,
                "risk_score": 0.0,
                "description": "No recent transactions to analyze",
                "details": {},
            }

        # Get baseline hour distribution (last 30 days)
        baseline_result = await db.execute(
            select(Transaction.timestamp).where(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.timestamp >= now - timedelta(days=self.BASELINE_WINDOW_DAYS),
                    Transaction.timestamp < now - timedelta(hours=self.TIME_WINDOW_HOURS),
                )
            )
        )
        baseline_timestamps = [r[0] for r in baseline_result.all()]

        if len(baseline_timestamps) < 5:
            return {
                "type": "timing_anomaly",
                "is_anomalous": False,
                "risk_score": 0.0,
                "description": "Insufficient baseline data for timing analysis",
                "details": {},
            }

        # Build hour distributions
        baseline_hours = set()
        for ts in baseline_timestamps:
            if ts:
                baseline_hours.add(ts.hour)

        # Check for off-pattern hours (e.g., transactions at 3 AM if user only transacts 9-5)
        unusual_hours = []
        for ts in recent_timestamps:
            if ts and ts.hour not in baseline_hours:
                unusual_hours.append(ts.hour)

        unusual_count = len(unusual_hours)
        is_anomalous = unusual_count > 0 and (unusual_count / max(len(recent_timestamps), 1)) > 0.5

        risk_score = min(15.0, unusual_count * 5.0) if is_anomalous else 0.0

        return {
            "type": "timing_anomaly",
            "is_anomalous": is_anomalous,
            "risk_score": risk_score,
            "description": f"Transactions at unusual hours: {unusual_hours}" if is_anomalous else "Transaction timing within normal range",
            "details": {
                "unusual_hours": unusual_hours,
                "baseline_active_hours": sorted(list(baseline_hours)),
                "unusual_ratio": round(unusual_count / max(len(recent_timestamps), 1), 2),
            },
        }


# Singleton
behavioral_analyzer = BehavioralAnalyzer()

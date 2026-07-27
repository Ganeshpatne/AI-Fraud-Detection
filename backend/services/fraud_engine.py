"""
Hybrid Fraud Detection Engine.
Combines:
  1. Rule-based detection
  2. Anomaly detection (Isolation Forest)
  3. Classification model (XGBoost / Random Forest)
"""
import json
import logging
from pathlib import Path
from typing import Optional, Tuple

try:
    import numpy as np
    import joblib
    from sklearn.ensemble import IsolationForest, RandomForestClassifier
    from xgboost import XGBClassifier
    HAS_ML = True
except ImportError:
    np = None
    joblib = None
    IsolationForest = None
    RandomForestClassifier = None
    XGBClassifier = None
    HAS_ML = False


from backend.config import MODELS_DIR

logger = logging.getLogger("fraud_detection.predictions")

# ─── Thresholds ────────────────────────────────────────────────
AMOUNT_HIGH = 5000.0
AMOUNT_VERY_HIGH = 15000.0
FREQUENCY_SPIKE_COUNT = 5       # > 5 txns in 1 hour → suspicious
FREQUENCY_SPIKE_WINDOW = 3600   # seconds


class FraudDetectionEngine:
    """Hybrid fraud detection combining rules, anomaly, and ML classification."""

    def __init__(self):
        self.xgb_model: Optional[XGBClassifier] = None
        self.rf_model: Optional[RandomForestClassifier] = None
        self.isolation_forest: Optional[IsolationForest] = None
        self._load_models()

    # ── Model loading ──────────────────────────────────────────
    def _load_models(self):
        """Load pre-trained models from disk if they exist."""
        xgb_path = MODELS_DIR / "xgb_fraud_model.pkl"
        rf_path = MODELS_DIR / "rf_fraud_model.pkl"
        iso_path = MODELS_DIR / "isolation_forest.pkl"

        if xgb_path.exists():
            try:
                self.xgb_model = joblib.load(xgb_path)
                logger.info("XGBoost model loaded from %s", xgb_path)
            except Exception as e:
                logger.error("Failed to load XGBoost model: %s", e)

        if rf_path.exists():
            try:
                self.rf_model = joblib.load(rf_path)
                logger.info("Random Forest model loaded from %s", rf_path)
            except Exception as e:
                logger.error("Failed to load Random Forest model: %s", e)

        if iso_path.exists():
            try:
                self.isolation_forest = joblib.load(iso_path)
                logger.info("Isolation Forest model loaded from %s", iso_path)
            except Exception as e:
                logger.error("Failed to load Isolation Forest model: %s", e)

    # ── 1. Rule-based detection ────────────────────────────────
    def rule_based_check(
        self,
        amount: float,
        user_location: Optional[str],
        txn_location: Optional[str],
        user_device: Optional[str],
        txn_device: Optional[str],
        recent_txn_count: int = 0,
    ) -> Tuple[bool, float, list]:
        """
        Apply deterministic rules. Returns (is_suspicious, score_contribution, reasons).
        """
        score = 0.0
        reasons = []

        # High amount
        if amount > AMOUNT_VERY_HIGH:
            score += 35.0
            reasons.append(f"Very high transaction amount: ${amount:,.2f}")
        elif amount > AMOUNT_HIGH:
            score += 20.0
            reasons.append(f"High transaction amount: ${amount:,.2f}")

        # Location mismatch
        if user_location and txn_location and user_location.lower() != txn_location.lower():
            score += 25.0
            reasons.append(
                f"Location mismatch: user in '{user_location}', transaction from '{txn_location}'"
            )

        # Device mismatch
        if user_device and txn_device and user_device != txn_device:
            score += 20.0
            reasons.append("Device fingerprint mismatch detected")

        # Frequency spike
        if recent_txn_count > FREQUENCY_SPIKE_COUNT:
            score += 20.0
            reasons.append(
                f"Frequency spike: {recent_txn_count} transactions in the last hour"
            )

        return score > 30, min(score, 100.0), reasons

    # ── 2. Anomaly detection ───────────────────────────────────
    def anomaly_check(self, features: np.ndarray) -> Tuple[bool, float]:
        """
        Use Isolation Forest for unsupervised anomaly detection.
        Returns (is_anomaly, anomaly_score 0-100).
        """
        if self.isolation_forest is None:
            return False, 0.0

        try:
            score_raw = self.isolation_forest.decision_function(features.reshape(1, -1))[0]
            prediction = self.isolation_forest.predict(features.reshape(1, -1))[0]
            # Convert score: more negative → more anomalous → higher risk
            anomaly_score = max(0.0, min(100.0, (0.5 - score_raw) * 100))
            return prediction == -1, anomaly_score
        except Exception as e:
            logger.error("Anomaly detection error: %s", e)
            return False, 0.0

    # ── 3. ML classification ───────────────────────────────────
    def classification_check(self, features: np.ndarray) -> Tuple[bool, float]:
        """
        Use XGBoost (primary) or Random Forest (fallback) classifier.
        Returns (is_fraud, confidence 0-1).
        """
        model = self.xgb_model or self.rf_model
        if model is None:
            return False, 0.0

        try:
            features_2d = features.reshape(1, -1)
            prediction = model.predict(features_2d)[0]
            proba = model.predict_proba(features_2d)[0]
            confidence = float(max(proba))
            return bool(prediction == 1), confidence
        except Exception as e:
            logger.error("Classification error: %s", e)
            return False, 0.0

    def get_shap_explanation(self, features: np.ndarray, feature_names=None) -> list:
        """Generate SHAP explanation for the prediction."""
        if self.xgb_model is None:
            return []
            
        try:
            import shap
            explainer = shap.TreeExplainer(self.xgb_model)
            shap_values = explainer.shap_values(features.reshape(1, -1))
            
            # Handle different SHAP outputs (binary vs multi-class)
            if isinstance(shap_values, list):
                shap_vals = shap_values[1][0] if len(shap_values) > 1 else shap_values[0][0]
            else:
                shap_vals = shap_values[0]
                
            explanations = []
            for i, val in enumerate(shap_vals):
                feat_name = feature_names[i] if feature_names and i < len(feature_names) else f"F_{i}"
                explanations.append({"feature": feat_name, "impact": float(val)})
                
            # Sort by absolute impact
            return sorted(explanations, key=lambda x: abs(x["impact"]), reverse=True)[:10]
        except Exception as e:
            logger.error("SHAP explanation error: %s", e)
            return []

    # ── Composite analysis ─────────────────────────────────────
    def analyze(
        self,
        amount: float,
        user_location: Optional[str] = None,
        txn_location: Optional[str] = None,
        user_device: Optional[str] = None,
        txn_device: Optional[str] = None,
        recent_txn_count: int = 0,
        features_json: Optional[str] = None,
    ) -> dict:
        """
        Run all three detection layers and aggregate results.
        Returns a dict with is_fraud, risk_score, confidence, fraud_type, reason, risk_factors.
        """
        all_reasons = []
        risk_factors = {
            "amount_factor": 0.0,
            "location_factor": 0.0,
            "frequency_factor": 0.0,
            "device_factor": 0.0,
        }

        # ── Layer 1 – Rules ────────────────
        rule_flag, rule_score, rule_reasons = self.rule_based_check(
            amount, user_location, txn_location, user_device, txn_device, recent_txn_count
        )
        all_reasons.extend(rule_reasons)

        # Break down rule score into factors
        if amount > AMOUNT_VERY_HIGH:
            risk_factors["amount_factor"] = 35.0
        elif amount > AMOUNT_HIGH:
            risk_factors["amount_factor"] = 20.0

        if user_location and txn_location and user_location.lower() != txn_location.lower():
            risk_factors["location_factor"] = 25.0

        if user_device and txn_device and user_device != txn_device:
            risk_factors["device_factor"] = 20.0

        if recent_txn_count > FREQUENCY_SPIKE_COUNT:
            risk_factors["frequency_factor"] = 20.0

        # ── Layer 2 – Anomaly ──────────────
        anomaly_flag = False
        anomaly_score = 0.0
        features = None
        if features_json:
            try:
                feat_list = json.loads(features_json)
                features = np.array(feat_list, dtype=float)
                anomaly_flag, anomaly_score = self.anomaly_check(features)
                if anomaly_flag:
                    all_reasons.append("Anomaly detected by Isolation Forest model")
            except Exception as e:
                logger.warning("Could not parse features for anomaly check: %s", e)

        # ── Layer 3 – Classification ───────
        class_flag = False
        class_confidence = 0.0
        shap_explanation = []
        if features is not None:
            class_flag, class_confidence = self.classification_check(features)
            shap_explanation = self.get_shap_explanation(features)
            if class_flag:
                all_reasons.append(
                    f"ML classifier flagged as fraudulent (confidence: {class_confidence:.2%})"
                )

        # ── Aggregate ─────────────────────
        # Weighted average of scores
        final_score = min(100.0, (
            rule_score * 0.4
            + anomaly_score * 0.3
            + (class_confidence * 100) * 0.3
        ))

        is_fraud = rule_flag or anomaly_flag or class_flag or final_score >= 50

        fraud_type = None
        if class_flag:
            fraud_type = "classification"
        elif anomaly_flag:
            fraud_type = "anomaly"
        elif rule_flag:
            fraud_type = "rule_based"

        reason = "; ".join(all_reasons) if all_reasons else "No fraud indicators detected."
        confidence = max(class_confidence, final_score / 100.0)

        result = {
            "is_fraud": is_fraud,
            "risk_score": round(final_score, 2),
            "confidence": round(confidence, 4),
            "fraud_type": fraud_type,
            "reason": reason,
            "risk_factors": risk_factors,
            "shap_explanation": shap_explanation,
        }

        logger.info("Fraud analysis result: %s", json.dumps(result))
        return result


# Singleton
fraud_engine = FraudDetectionEngine()

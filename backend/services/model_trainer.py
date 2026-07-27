"""
ML Model Training Pipeline.
Train → Evaluate → Save → Reload
Supports: XGBoost, Random Forest, Isolation Forest
Schema-aware: uses dataset_schema.json for multi-domain datasets.
"""
import logging
import json
from datetime import datetime
from pathlib import Path

try:
    import pandas as pd
    import numpy as np
    import joblib
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, roc_auc_score, accuracy_score
    from sklearn.ensemble import IsolationForest, RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    from xgboost import XGBClassifier
    HAS_ML_TRAINER = True
except ImportError:
    pd = None
    np = None
    joblib = None
    HAS_ML_TRAINER = False

from backend.config import MODELS_DIR, DATA_DIR


logger = logging.getLogger("fraud_detection")
training_logger = logging.getLogger("fraud_detection.training")


class ModelTrainer:
    """End-to-end training pipeline for fraud detection models."""

    def __init__(self):
        self.models_dir = MODELS_DIR
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.scaler = StandardScaler()

    def load_data(self, csv_path: str = None) -> pd.DataFrame:
        """Load dataset from file."""
        if csv_path is None:
            csv_path = DATA_DIR / "creditcard.csv"
        df = pd.read_csv(csv_path)
        logger.info("Loaded dataset: %d rows, %d columns", len(df), len(df.columns))
        training_logger.info("Dataset loaded: %s (%d rows, %d cols)", csv_path, len(df), len(df.columns))
        return df

    def preprocess(self, df: pd.DataFrame, domain: str = "banking") -> tuple:
        """
        Prepare features and labels using schema-aware column mapping.
        Supports multiple dataset types via dataset_schema.json.
        """
        from backend.services.schema_mapper import schema_mapper

        try:
            X, y = schema_mapper.prepare_for_training(df, domain)
            training_logger.info(
                "Preprocessing complete (domain=%s): %d features, %d samples, fraud_rate=%.2f%%",
                domain, X.shape[1], len(y), (y.sum() / len(y) * 100)
            )
        except Exception as e:
            logger.warning("Schema-aware preprocessing failed (%s), falling back to default: %s", domain, e)
            # Fallback: try standard 'Class' column
            if "Class" not in df.columns:
                raise ValueError(
                    f"Dataset must contain a label column. Error: {e}. "
                    "Check dataset_schema.json for supported formats."
                )
            X = df.drop("Class", axis=1)
            y = df["Class"]

        # Scale Amount and Time if present
        if "Amount" in X.columns:
            X["Amount_Scaled"] = self.scaler.fit_transform(X[["Amount"]])
        if "Time" in X.columns:
            X["Time_Scaled"] = self.scaler.fit_transform(X[["Time"]])

        return X, y

    def train_xgboost(self, X, y, test_size=0.2) -> dict:
        """Train XGBoost classifier."""
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )

        model = XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            scale_pos_weight=len(y_train[y_train == 0]) / max(len(y_train[y_train == 1]), 1),
            use_label_encoder=False,
            eval_metric="logloss",
            random_state=42,
        )
        model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)

        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]

        accuracy = accuracy_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_proba)
        report = classification_report(y_test, y_pred, output_dict=True)

        # Save model
        model_path = self.models_dir / "xgb_fraud_model.pkl"
        joblib.dump(model, model_path)
        training_logger.info("XGBoost model saved to %s (AUC: %.4f, Accuracy: %.4f)", model_path, auc, accuracy)

        return {
            "model": "XGBoost",
            "accuracy": round(accuracy, 4),
            "auc_roc": round(auc, 4),
            "classification_report": report,
            "model_path": str(model_path),
            "trained_at": datetime.now().isoformat(),
        }

    def train_random_forest(self, X, y, test_size=0.2) -> dict:
        """Train Random Forest classifier."""
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )

        model = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        )
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]

        accuracy = accuracy_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_proba)
        report = classification_report(y_test, y_pred, output_dict=True)

        model_path = self.models_dir / "rf_fraud_model.pkl"
        joblib.dump(model, model_path)
        training_logger.info("Random Forest model saved to %s (AUC: %.4f, Accuracy: %.4f)", model_path, auc, accuracy)

        return {
            "model": "Random Forest",
            "accuracy": round(accuracy, 4),
            "auc_roc": round(auc, 4),
            "classification_report": report,
            "model_path": str(model_path),
            "trained_at": datetime.now().isoformat(),
        }

    def train_isolation_forest(self, X) -> dict:
        """Train Isolation Forest for anomaly detection."""
        model = IsolationForest(
            n_estimators=200,
            contamination=0.01,
            random_state=42,
            n_jobs=-1,
        )
        model.fit(X)

        scores = model.decision_function(X)
        predictions = model.predict(X)
        anomaly_count = (predictions == -1).sum()

        model_path = self.models_dir / "isolation_forest.pkl"
        joblib.dump(model, model_path)
        training_logger.info(
            "Isolation Forest saved to %s (anomalies detected: %d)", model_path, anomaly_count
        )

        return {
            "model": "Isolation Forest",
            "anomalies_detected": int(anomaly_count),
            "total_samples": len(X),
            "contamination_rate": round(anomaly_count / len(X), 4),
            "model_path": str(model_path),
            "trained_at": datetime.now().isoformat(),
        }

    def train_all(self, csv_path: str = None, domain: str = "banking") -> dict:
        """Run the full training pipeline for all models."""
        df = self.load_data(csv_path)
        X, y = self.preprocess(df, domain=domain)

        results = {}

        training_logger.info("Training XGBoost (domain: %s)...", domain)
        results["xgboost"] = self.train_xgboost(X, y)

        training_logger.info("Training Random Forest (domain: %s)...", domain)
        results["random_forest"] = self.train_random_forest(X, y)

        training_logger.info("Training Isolation Forest (domain: %s)...", domain)
        results["isolation_forest"] = self.train_isolation_forest(X)

        # Save scaler
        scaler_path = self.models_dir / "scaler.pkl"
        joblib.dump(self.scaler, scaler_path)

        training_logger.info("All models trained successfully (domain: %s).", domain)
        return results


# Singleton
model_trainer = ModelTrainer()

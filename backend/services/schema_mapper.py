"""
Dataset schema mapper service.
Reads dataset_schema.json and auto-maps columns for different fraud domains
(banking, insurance, ecommerce, document fraud).
"""
import json
import logging
from pathlib import Path
from typing import Optional

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    pd = None
    HAS_PANDAS = False


logger = logging.getLogger("fraud_detection")

SCHEMA_CONFIG_PATH = Path(__file__).resolve().parent.parent / "dataset_schema.json"


class DatasetSchemaMapper:
    """Maps uploaded dataset columns to internal schema based on domain config."""

    def __init__(self):
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load the dataset_schema.json configuration."""
        try:
            with open(SCHEMA_CONFIG_PATH, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error("dataset_schema.json not found at %s", SCHEMA_CONFIG_PATH)
            return {"schema_mappings": {}, "validation_rules": {}}

    def get_supported_domains(self) -> list:
        """Return list of supported dataset domains."""
        return list(self.config.get("schema_mappings", {}).keys())

    def get_mapping(self, domain: str) -> dict:
        """Get column mapping for a specific domain."""
        mappings = self.config.get("schema_mappings", {})
        return mappings.get(domain, mappings.get("custom", {}))

    def detect_domain(self, df: pd.DataFrame) -> str:
        """
        Auto-detect the dataset domain based on column names.
        Returns the best matching domain.
        """
        columns = set(col.lower() for col in df.columns)
        mappings = self.config.get("schema_mappings", {})

        scores = {}
        for domain, mapping in mappings.items():
            if domain == "custom":
                continue
            score = 0
            for key in ["label_column", "amount_column", "timestamp_column", "location_column"]:
                col_name = mapping.get(key)
                if col_name and col_name.lower() in columns:
                    score += 1
            scores[domain] = score

        if not scores:
            return "custom"

        best_domain = max(scores, key=scores.get)
        if scores[best_domain] == 0:
            return "custom"

        logger.info("Auto-detected dataset domain: %s (score: %d)", best_domain, scores[best_domain])
        return best_domain

    def validate_dataset(self, df: pd.DataFrame, domain: str) -> tuple[bool, str]:
        """
        Validate dataset against schema rules.
        Returns (is_valid, error_message).
        """
        rules = self.config.get("validation_rules", {})

        # Check minimum rows
        min_rows = rules.get("min_rows", 100)
        if len(df) < min_rows:
            return False, f"Dataset too small: {len(df)} rows (minimum: {min_rows})"

        # Get column mapping
        mapping = self.get_mapping(domain)
        label_col = mapping.get("label_column")

        if not label_col:
            return False, f"No label column configured for domain '{domain}'"

        # Check label column exists
        if label_col not in df.columns:
            # Try case-insensitive match
            col_map = {c.lower(): c for c in df.columns}
            if label_col.lower() in col_map:
                label_col = col_map[label_col.lower()]
            else:
                return False, f"Label column '{label_col}' not found in dataset. Available: {list(df.columns)}"

        # Check label values
        unique_labels = df[label_col].dropna().unique()
        if len(unique_labels) < 2:
            return False, f"Label column '{label_col}' must have at least 2 unique values, found: {list(unique_labels)}"

        return True, "Dataset validated successfully"

    def map_columns(self, df: pd.DataFrame, domain: str) -> dict:
        """
        Map dataset columns to internal schema.
        Returns dict with resolved column names.
        """
        mapping = self.get_mapping(domain)
        resolved = {}

        for key in ["label_column", "amount_column", "timestamp_column", "location_column"]:
            configured_col = mapping.get(key)
            if configured_col and configured_col in df.columns:
                resolved[key] = configured_col
            elif configured_col:
                # Try case-insensitive
                col_map = {c.lower(): c for c in df.columns}
                if configured_col.lower() in col_map:
                    resolved[key] = col_map[configured_col.lower()]
                else:
                    resolved[key] = None
            else:
                resolved[key] = None

        # Detect feature columns
        pattern = mapping.get("feature_columns_pattern")
        if pattern and pattern == "V*":
            resolved["feature_columns"] = [c for c in df.columns if c.startswith("V") and c[1:].isdigit()]
        else:
            # Use all numeric columns except label and known columns
            known = set(v for v in resolved.values() if v)
            resolved["feature_columns"] = [
                c for c in df.columns
                if c not in known and df[c].dtype in ["int64", "float64", "int32", "float32"]
            ]

        return resolved

    def prepare_for_training(self, df: pd.DataFrame, domain: str) -> tuple[pd.DataFrame, pd.Series]:
        """
        Prepare features (X) and labels (y) from a dataset using schema mapping.
        Returns (X, y).
        """
        col_map = self.map_columns(df, domain)
        label_col = col_map["label_column"]

        if not label_col:
            raise ValueError("Cannot determine label column from schema mapping")

        y = df[label_col].copy()

        # Convert non-numeric labels to binary
        unique_labels = y.unique()
        if y.dtype == object:
            # Try common mappings
            label_mapping = {}
            for val in unique_labels:
                val_lower = str(val).lower()
                if val_lower in ("yes", "y", "true", "1", "fraud", "fraudulent"):
                    label_mapping[val] = 1
                else:
                    label_mapping[val] = 0
            y = y.map(label_mapping)

        # Build feature matrix
        feature_cols = col_map.get("feature_columns", [])
        if feature_cols:
            X = df[feature_cols].copy()
        else:
            # Use all numeric columns except label
            exclude = {label_col}
            X = df.select_dtypes(include=["int64", "float64", "int32", "float32"]).drop(
                columns=[c for c in exclude if c in df.columns], errors="ignore"
            )

        # Fill NaN with 0
        X = X.fillna(0)
        y = y.fillna(0).astype(int)

        return X, y


    def auto_detect_schema(self, df: pd.DataFrame) -> dict:
        """
        Auto-detect generic schema columns for label, amount, timestamp, location, device, IP.
        """
        columns = df.columns.tolist()
        schema = {
            "Label Column": None,
            "Amount Column": None,
            "Timestamp Column": None,
            "Location Column": None,
            "Device Column": None,
            "IP Column": None
        }
        
        for col in columns:
            col_lower = col.lower()
            if not schema["Label Column"] and any(x in col_lower for x in ['class', 'is_fraud', 'fraud', 'label']):
                schema["Label Column"] = col
            elif not schema["Amount Column"] and any(x in col_lower for x in ['amount', 'amt', 'value', 'transactionamount']):
                schema["Amount Column"] = col
            elif not schema["Timestamp Column"] and any(x in col_lower for x in ['time', 'date', 'timestamp', 'created_at']):
                schema["Timestamp Column"] = col
            elif not schema["Location Column"] and any(x in col_lower for x in ['loc', 'city', 'state', 'country', 'region', 'zip']):
                schema["Location Column"] = col
            elif not schema["Device Column"] and any(x in col_lower for x in ['device', 'browser', 'os', 'platform']):
                schema["Device Column"] = col
            elif not schema["IP Column"] and any(x in col_lower for x in ['ip', 'address']):
                schema["IP Column"] = col
                
        return schema


# Singleton
schema_mapper = DatasetSchemaMapper()

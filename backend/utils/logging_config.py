"""
Logging configuration for the fraud detection system.
Logs predictions, alerts, errors, dataset uploads, model training, and PDF generation.
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from backend.config import LOGS_DIR


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configure application-wide logging."""
    logger = logging.getLogger("fraud_detection")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler – general
    file_handler = RotatingFileHandler(
        LOGS_DIR / "app.log", maxBytes=10_000_000, backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # File handler – predictions
    pred_handler = RotatingFileHandler(
        LOGS_DIR / "predictions.log", maxBytes=10_000_000, backupCount=3
    )
    pred_handler.setFormatter(formatter)
    pred_logger = logging.getLogger("fraud_detection.predictions")
    pred_logger.addHandler(pred_handler)

    # File handler – alerts
    alert_handler = RotatingFileHandler(
        LOGS_DIR / "alerts.log", maxBytes=10_000_000, backupCount=3
    )
    alert_handler.setFormatter(formatter)
    alert_logger = logging.getLogger("fraud_detection.alerts")
    alert_logger.addHandler(alert_handler)

    # File handler – errors
    error_handler = RotatingFileHandler(
        LOGS_DIR / "errors.log", maxBytes=10_000_000, backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)

    # File handler – reports
    report_handler = RotatingFileHandler(
        LOGS_DIR / "reports.log", maxBytes=10_000_000, backupCount=3
    )
    report_handler.setFormatter(formatter)
    report_logger = logging.getLogger("fraud_detection.reports")
    report_logger.addHandler(report_handler)

    # File handler – dataset uploads
    upload_handler = RotatingFileHandler(
        LOGS_DIR / "uploads.log", maxBytes=10_000_000, backupCount=3
    )
    upload_handler.setFormatter(formatter)
    upload_logger = logging.getLogger("fraud_detection.uploads")
    upload_logger.addHandler(upload_handler)

    # File handler – model training
    training_handler = RotatingFileHandler(
        LOGS_DIR / "training.log", maxBytes=10_000_000, backupCount=3
    )
    training_handler.setFormatter(formatter)
    training_logger = logging.getLogger("fraud_detection.training")
    training_logger.addHandler(training_handler)

    return logger


logger = setup_logging()
pred_logger = logging.getLogger("fraud_detection.predictions")
alert_logger = logging.getLogger("fraud_detection.alerts")
report_logger = logging.getLogger("fraud_detection.reports")
upload_logger = logging.getLogger("fraud_detection.uploads")
training_logger = logging.getLogger("fraud_detection.training")

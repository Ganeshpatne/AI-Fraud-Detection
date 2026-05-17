"""
Dataset upload, validation, and training trigger routes.
"""
import logging
import shutil
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

import pandas as pd
import asyncio
import random
import uuid

from backend.database import get_db, async_session
from backend.config import DATASETS_DIR
from backend.models.database_models import Dataset, User, Transaction, FraudLog, RiskScore, Alert
from backend.services.schema_mapper import schema_mapper
from backend.services.fraud_engine import fraud_engine
from backend.services.websocket_manager import ws_manager
from backend.schemas.schemas import DatasetUploadResponse, DatasetListResponse, DatasetTrainResponse
from backend.services.schema_mapper import schema_mapper

logger = logging.getLogger("fraud_detection")
upload_logger = logging.getLogger("fraud_detection.uploads")
training_logger = logging.getLogger("fraud_detection.training")

router = APIRouter(prefix="/api/datasets", tags=["Datasets"])

# Track active streaming simulations for cancellation
active_streams = set()


@router.post("/upload", response_model=DatasetUploadResponse)
async def upload_dataset(
    file: UploadFile = File(...),
    name: str = Form(None),
    domain: str = Form(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a CSV dataset for fraud detection.
    Validates schema, stores the file, and auto-detects domain if not specified.
    """
    # Validate file type
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")

    # Read into DataFrame
    try:
        contents = await file.read()
        # Check file size (500MB limit)
        if len(contents) > 500 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large. Maximum: 500MB")

        import io
        df = pd.read_csv(io.BytesIO(contents))
    except pd.errors.ParserError as e:
        raise HTTPException(status_code=400, detail=f"Invalid CSV format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")

    # Auto-detect domain if not specified
    if not domain:
        domain = schema_mapper.detect_domain(df)

    # Validate dataset against schema
    is_valid, validation_msg = schema_mapper.validate_dataset(df, domain)
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Validation failed: {validation_msg}")

    # Get column mapping
    col_map = schema_mapper.map_columns(df, domain)
    label_col = col_map.get("label_column")

    # Calculate stats
    fraud_count = None
    legit_count = None
    if label_col and label_col in df.columns:
        label_series = df[label_col]
        if label_series.dtype == object:
            fraud_keywords = {"yes", "y", "true", "1", "fraud", "fraudulent"}
            fraud_count = int(label_series.apply(lambda x: str(x).lower() in fraud_keywords).sum())
        else:
            fraud_count = int((label_series == 1).sum())
        legit_count = len(df) - fraud_count

    # Save file
    dataset_name = name or file.filename.rsplit(".", 1)[0]
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{dataset_name}_{timestamp_str}.csv"
    file_path = DATASETS_DIR / safe_filename

    with open(file_path, "wb") as f:
        f.write(contents)

    # Save to database
    dataset = Dataset(
        name=dataset_name,
        original_filename=file.filename,
        file_path=str(file_path),
        domain=domain,
        row_count=len(df),
        column_count=len(df.columns),
        fraud_count=fraud_count,
        legitimate_count=legit_count,
        label_column=label_col,
        amount_column=col_map.get("amount_column"),
        timestamp_column=col_map.get("timestamp_column"),
        status="validated",
    )
    db.add(dataset)
    await db.commit()
    await db.refresh(dataset)

    upload_logger.info(
        "Dataset uploaded: %s (domain=%s, rows=%d, fraud=%s)",
        dataset_name, domain, len(df), fraud_count
    )

    return DatasetUploadResponse(
        id=dataset.id,
        name=dataset.name,
        original_filename=dataset.original_filename,
        domain=dataset.domain,
        row_count=dataset.row_count,
        column_count=dataset.column_count,
        fraud_count=dataset.fraud_count,
        legitimate_count=dataset.legitimate_count,
        label_column=dataset.label_column,
        status=dataset.status,
        uploaded_at=dataset.uploaded_at,
        message=f"Dataset uploaded and validated successfully. Domain: {domain}. "
                f"{len(df)} rows, {fraud_count or 0} fraudulent.",
    )


@router.get("/", response_model=list[DatasetListResponse])
async def list_datasets(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List all uploaded datasets."""
    result = await db.execute(
        select(Dataset).order_by(Dataset.uploaded_at.desc()).offset(skip).limit(limit)
    )
    return result.scalars().all()


@router.post("/train/{dataset_id}", response_model=DatasetTrainResponse)
async def train_on_dataset(dataset_id: str, db: AsyncSession = Depends(get_db)):
    """
    Trigger model training on a specific uploaded dataset.
    Uses schema mapping to auto-configure the training pipeline.
    """
    # Fetch dataset
    result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    if dataset.status == "training":
        raise HTTPException(status_code=409, detail="Training already in progress")

    # Update status
    dataset.status = "training"
    await db.commit()

    try:
        from backend.services.model_trainer import model_trainer

        training_logger.info("Training started on dataset: %s (domain: %s)", dataset.name, dataset.domain)

        # Train using schema-aware pipeline
        results = model_trainer.train_all(
            csv_path=dataset.file_path,
            domain=dataset.domain,
        )

        dataset.status = "ready"
        dataset.trained_at = datetime.utcnow()
        await db.commit()

        training_logger.info("Training completed for dataset: %s", dataset.name)

        return DatasetTrainResponse(
            dataset_id=dataset_id,
            status="success",
            results=results,
            message=f"Model training completed on dataset '{dataset.name}'",
        )

    except Exception as e:
        dataset.status = "error"
        dataset.error_message = str(e)
        await db.commit()

        training_logger.error("Training failed for dataset %s: %s", dataset.name, str(e))

        return DatasetTrainResponse(
            dataset_id=dataset_id,
            status="error",
            message=f"Training failed: {str(e)}",
        )


@router.delete("/{dataset_id}")
async def delete_dataset(dataset_id: str, db: AsyncSession = Depends(get_db)):
    """
    Delete an uploaded dataset, its file, and CLEAR all transactions/logs.
    Also stops any active streaming for this dataset.
    """
    # 1. Stop active stream if running
    if dataset_id in active_streams:
        active_streams.remove(dataset_id)
        logger.info(f"Stream cancellation requested for dataset {dataset_id}")

    # 2. Fetch dataset
    result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # 3. Delete file
    file_path = Path(dataset.file_path)
    if file_path.exists():
        file_path.unlink()

    # 4. CLEAR ALL TRANSACTION DATA (The "Clean Slate" feature)
    from sqlalchemy import delete
    from backend.models.database_models import Report
    
    await db.execute(delete(Alert))
    await db.execute(delete(RiskScore))
    await db.execute(delete(FraudLog))
    await db.execute(delete(Report))
    await db.execute(delete(Transaction))
    
    # 5. Delete the dataset itself
    await db.delete(dataset)
    await db.commit()

    upload_logger.info("Dataset deleted and all transaction data cleared: %s", dataset.name)
    return {"status": "deleted", "dataset_id": dataset_id, "message": "Dataset and all system data cleared."}


@router.post("/clear-all")
async def clear_all_data(db: AsyncSession = Depends(get_db)):
    """
    NUCLEAR OPTION: Clear ALL transactions, alerts, logs, and scores.
    Leaves users and datasets intact.
    """
    from sqlalchemy import delete
    from backend.models.database_models import Report

    try:
        await db.execute(delete(Alert))
        await db.execute(delete(RiskScore))
        await db.execute(delete(FraudLog))
        await db.execute(delete(Report))
        await db.execute(delete(Transaction))
        await db.commit()
        
        logger.info("Nuclear Clear: All transaction data has been wiped.")
        return {"status": "success", "message": "All transaction data cleared successfully."}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to clear data: {str(e)}")


async def stream_dataset_task(dataset_id: str, file_path: str, domain: str):
    """Background task to simulate live traffic from a dataset."""
    try:
        df = pd.read_csv(file_path)
        
        col_map = schema_mapper.map_columns(df, domain)
        label_col = col_map.get("label_column")
        amount_col = col_map.get("amount_column") or "Amount"

        # Shuffle the full dataset for an authentic real-time stream
        df = df.sample(frac=1).reset_index(drop=True)

        
        async with async_session() as db:
            # Get available users
            result = await db.execute(select(User))
            users = result.scalars().all()
            if not users:
                logger.error("No users found for streaming simulation.")
                return

            training_logger.info(f"Starting live stream for dataset {dataset_id}")
            
            for _, row in df.iterrows():
                # Check for cancellation
                if dataset_id not in active_streams:
                    training_logger.info(f"Streaming task for {dataset_id} cancelled.")
                    return

                user = random.choice(users)
                amount = float(row[amount_col]) if amount_col in row else random.uniform(10, 500)
                
                # Check if it's supposed to be fraud based on dataset label
                label_col = col_map.get("label_column")
                is_fraud_label = False
                if label_col and label_col in row:
                    val = str(row[label_col]).lower().strip()
                    is_fraud_label = val in ("1", "1.0", "true", "yes", "fraud")
                
                txn_location = random.choice(["Mumbai, IN", "New York, US", "London, UK"]) if is_fraud_label else user.location
                txn_device = f"dev-unknown-{random.randint(100,999)}" if is_fraud_label else user.device_fingerprint
                
                # Run through engine
                analysis = fraud_engine.analyze(
                    amount=amount,
                    user_location=user.location,
                    txn_location=txn_location,
                    user_device=user.device_fingerprint,
                    txn_device=txn_device,
                    recent_txn_count=random.randint(0, 5)
                )
                
                timestamp = datetime.utcnow()
                txn_id = str(uuid.uuid4())
                
                # We can force the analysis risk score slightly higher if the dataset says it's fraud
                if is_fraud_label and not analysis["is_fraud"]:
                    analysis["is_fraud"] = True
                    analysis["risk_score"] = max(75.0, analysis["risk_score"] + 30.0)
                    analysis["fraud_type"] = "classification"
                    analysis["reason"] += " | Flagged by dataset ML label."
                
                # Save transaction
                txn = Transaction(
                    id=txn_id,
                    user_id=user.id,
                    amount=round(amount, 2),
                    location=txn_location,
                    device_fingerprint=txn_device,
                    merchant=random.choice(["Amazon", "Uber", "Walmart", "Netflix", "Crypto Exchange"]),
                    category=random.choice(["shopping", "travel", "entertainment", "crypto"]),
                    is_fraud=analysis["is_fraud"],
                    risk_score=analysis["risk_score"],
                    confidence=analysis["confidence"],
                    timestamp=timestamp,
                )
                db.add(txn)
                await db.flush()
                
                # Save Fraud Log & Risk Score
                db.add(FraudLog(
                    id=str(uuid.uuid4()), transaction_id=txn_id,
                    fraud_type=analysis["fraud_type"],
                    classification_result="fraudulent" if analysis["is_fraud"] else "legitimate",
                    reason=analysis["reason"], detected_at=timestamp
                ))
                db.add(RiskScore(
                    id=str(uuid.uuid4()), transaction_id=txn_id, score=analysis["risk_score"],
                    amount_factor=analysis["risk_factors"]["amount_factor"],
                    location_factor=analysis["risk_factors"]["location_factor"],
                    frequency_factor=analysis["risk_factors"]["frequency_factor"],
                    device_factor=analysis["risk_factors"]["device_factor"],
                    calculated_at=timestamp
                ))
                
                # Generate Alert & Broadcast
                if analysis["is_fraud"]:
                    severity = "critical" if analysis["risk_score"] >= 70 else "high"
                    alert = Alert(
                        id=str(uuid.uuid4()), user_id=user.id, transaction_id=txn_id,
                        severity=severity, message=f"Fraud detected: {analysis['reason'][:100]}",
                        created_at=timestamp
                    )
                    db.add(alert)
                    await db.flush()
                    await ws_manager.broadcast_alert({
                        "id": alert.id, "transaction_id": txn.id, "severity": alert.severity,
                        "message": alert.message, "amount": txn.amount, "user": user.username,
                        "timestamp": timestamp.isoformat()
                    })

                await db.commit()
                # Sleep briefly to simulate live traffic
                await asyncio.sleep(0.8)
                
            training_logger.info(f"Finished live stream for dataset {dataset_id}")
    except Exception as e:
        logger.error(f"Error in stream_dataset_task: {str(e)}")


@router.post("/stream/{dataset_id}")
async def stream_dataset(dataset_id: str, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    """Trigger a live simulation using rows from the dataset."""
    result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
        
    if not Path(dataset.file_path).exists():
        raise HTTPException(status_code=404, detail="Dataset file missing")

    active_streams.add(dataset.id)
    background_tasks.add_task(stream_dataset_task, dataset.id, dataset.file_path, dataset.domain)
    
    return {"status": "streaming", "message": f"Live streaming started for {dataset.name}. Check the Dashboard!"}

"""
Fraud explanation (NVIDIA AI), behavioral analysis, and report generation routes.
"""
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.database import get_db
from backend.models.database_models import Transaction, FraudLog, RiskScore, Report
from backend.schemas.schemas import ExplainFraudRequest, ExplainFraudResponse, ReportResponse
from backend.services.nvidia_ai_service import nvidia_ai_service
from backend.services.report_generator import report_generator
from backend.services.behavioral_analyzer import behavioral_analyzer

logger = logging.getLogger("fraud_detection")
report_logger = logging.getLogger("fraud_detection.reports")

router = APIRouter(prefix="/api", tags=["Fraud Intelligence"])


@router.post("/explain-fraud", response_model=ExplainFraudResponse)
async def explain_fraud(req: ExplainFraudRequest, db: AsyncSession = Depends(get_db)):
    """
    Explain why a transaction was flagged as fraudulent.
    Uses NVIDIA inference API for AI-powered explanations.
    """
    # Fetch transaction
    result = await db.execute(
        select(Transaction).where(Transaction.id == req.transaction_id)
    )
    txn = result.scalar_one_or_none()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Fetch risk score breakdown
    risk_result = await db.execute(
        select(RiskScore).where(RiskScore.transaction_id == req.transaction_id)
    )
    risk = risk_result.scalar_one_or_none()

    risk_factors = {}
    if risk:
        risk_factors = {
            "amount_factor": risk.amount_factor,
            "location_factor": risk.location_factor,
            "frequency_factor": risk.frequency_factor,
            "device_factor": risk.device_factor,
        }

    # Fetch fraud log for reason
    log_result = await db.execute(
        select(FraudLog).where(FraudLog.transaction_id == req.transaction_id)
    )
    fraud_log = log_result.scalar_one_or_none()
    reason = fraud_log.reason if fraud_log else "No detection reason recorded."
    fraud_type = fraud_log.fraud_type if fraud_log else None

    # Call NVIDIA AI service
    explanation = await nvidia_ai_service.explain_fraud(
        transaction_id=req.transaction_id,
        amount=txn.amount,
        risk_score=txn.risk_score,
        confidence=txn.confidence,
        fraud_type=fraud_type,
        reason=reason,
        risk_factors=risk_factors,
        user_question=req.question,
    )

    logger.info("Fraud explanation generated for transaction %s", req.transaction_id)
    return ExplainFraudResponse(**explanation)


@router.get("/generate-report/{transaction_id}", response_model=ReportResponse)
async def generate_report(transaction_id: str, db: AsyncSession = Depends(get_db)):
    """
    Generate a PDF fraud investigation report for a transaction.
    """
    # Fetch transaction
    result = await db.execute(
        select(Transaction).where(Transaction.id == transaction_id)
    )
    txn = result.scalar_one_or_none()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Fetch risk score
    risk_result = await db.execute(
        select(RiskScore).where(RiskScore.transaction_id == transaction_id)
    )
    risk = risk_result.scalar_one_or_none()
    risk_factors = {}
    if risk:
        risk_factors = {
            "amount_factor": risk.amount_factor,
            "location_factor": risk.location_factor,
            "frequency_factor": risk.frequency_factor,
            "device_factor": risk.device_factor,
        }

    # Fetch fraud log
    log_result = await db.execute(
        select(FraudLog).where(FraudLog.transaction_id == transaction_id)
    )
    fraud_log = log_result.scalar_one_or_none()
    reason = fraud_log.reason if fraud_log else "No detection details available."
    fraud_type = fraud_log.fraud_type if fraud_log else "unknown"

    # Get AI explanation for the report
    explanation_data = await nvidia_ai_service.explain_fraud(
        transaction_id=transaction_id,
        amount=txn.amount,
        risk_score=txn.risk_score,
        confidence=txn.confidence,
        fraud_type=fraud_type,
        reason=reason,
        risk_factors=risk_factors,
    )

    # Check if report already exists to prevent UniqueViolation error
    report_record = await db.execute(select(Report).where(Report.transaction_id == transaction_id))
    existing_report = report_record.scalar_one_or_none()

    # Clean the explanation of any stray markdown asterisks the LLM may have sneaked in
    clean_explanation = explanation_data["explanation"].replace("**", "").replace("*", "")

    # Generate PDF
    file_path = report_generator.generate(
        transaction_id=txn.id,
        user_id=txn.user_id,
        amount=txn.amount,
        risk_score=txn.risk_score,
        confidence=txn.confidence,
        fraud_type=fraud_type,
        reason=reason,
        explanation=clean_explanation,
        risk_factors=risk_factors,
        timestamp=txn.timestamp,
    )

    if existing_report:
        existing_report.file_path = file_path
        existing_report.generated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(existing_report)
        return_record = existing_report
    else:
        # Save new report record
        new_report = Report(
            transaction_id=txn.id,
            file_path=file_path,
        )
        db.add(new_report)
        await db.commit()
        await db.refresh(new_report)
        return_record = new_report

    report_logger.info("Report generated for transaction %s: %s", transaction_id, file_path)

    return return_record


@router.get("/download-report/{transaction_id}")
async def download_report(transaction_id: str, db: AsyncSession = Depends(get_db)):
    """Download the PDF report for a transaction."""
    result = await db.execute(
        select(Report).where(Report.transaction_id == transaction_id)
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found. Generate it first.")

    return FileResponse(
        path=report.file_path,
        media_type="application/pdf",
        filename=f"fraud_report_{transaction_id[:8]}.pdf",
    )


@router.get("/behavioral-analysis/{user_id}")
async def get_behavioral_analysis(user_id: str, db: AsyncSession = Depends(get_db)):
    """
    Run behavioral analysis for a user.
    Detects location switching, device switching, frequency spikes, and timing anomalies.
    """
    result = await behavioral_analyzer.analyze_user_behavior(user_id, db)
    return result

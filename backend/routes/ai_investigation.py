from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List

from backend.workflows.fraud_investigation import fraud_workflow

router = APIRouter(prefix="/api/ai-investigation", tags=["AI Investigation"])

class TransactionRequest(BaseModel):
    id: str
    amount: float
    merchant: str
    location: str
    device_id: str
    timestamp: str

class InvestigationResponse(BaseModel):
    transaction_id: str
    decision: str
    risk_level: str
    explanation: str

@router.post("/", response_model=InvestigationResponse)
async def investigate_transaction(transaction: TransactionRequest):
    """
    Run a transaction through the complete AI Fraud Investigation workflow
    (ML Analysis -> Postgres RAG Context -> NVIDIA LLM Decision).
    """
    try:
        # Convert the incoming pydantic model to a dict for the workflow state
        transaction_data = transaction.model_dump()

        # Invoke the LangGraph workflow
        result = await fraud_workflow.ainvoke({
            "transaction_data": transaction_data
        })

        return InvestigationResponse(
            transaction_id=transaction.id,
            decision=result["final_decision"],
            risk_level=result.get("risk_level", "Unknown"),
            explanation=result["explanation"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

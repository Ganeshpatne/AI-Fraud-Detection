"""
LangGraph workflow for multi-step fraud investigation.
Steps: ML Analysis -> RAG Context -> Final Decision.
"""
from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph import StateGraph, END
from backend.services.rag_service import rag_service
from backend.services.fraud_engine import fraud_engine # Assuming this exists for ML

class InvestigationState(TypedDict):
    """The state maintained throughout the fraud investigation."""
    transaction_data: Dict[str, Any]
    ml_risk_score: float
    similar_cases: List[str]
    risk_level: str
    final_decision: str
    explanation: str

class FraudWorkflow:
    def __init__(self):
        self.rag = rag_service
        self.llm = rag_service.llm

    async def ml_analysis_node(self, state: InvestigationState):
        """Node 1: Get the risk score from the traditional ML model."""
        # For now, we simulate or call the existing fraud engine
        # In a real scenario, you'd call your XGBoost/RandomForest model here
        try:
            # Simple simulation if engine is complex
            score = state["transaction_data"].get("amount", 0) / 1000.0 * 50
            if score > 100: score = 99
        except:
            score = 50.0
            
        return {"ml_risk_score": score}

    async def rag_context_node(self, state: InvestigationState):
        """Node 2: Retrieve similar historical fraud cases from Postgres."""
        query = f"Transaction amount {state['transaction_data'].get('amount')} at {state['transaction_data'].get('merchant')}"
        cases = self.rag.query_similar_patterns(query)
        
        return {"similar_cases": [c["content"] for c in cases]}

    async def final_decision_node(self, state: InvestigationState):
        """Node 3: Use NVIDIA LLM to combine ML score + RAG cases into a decision."""
        prompt = f"""
        Final Fraud Investigation Report:
        
        Transaction: {state['transaction_data']}
        ML Risk Score: {state['ml_risk_score']}/100
        Similar Historical Cases: {state['similar_cases']}
        
        Based on this data, provide:
        1. FINAL DECISION: (APPROVE / REJECT / FLAG FOR REVIEW)
        2. RISK LEVEL: (Low / Medium / High / Critical)
        3. EXPLANATION: A concise reason for the decision.
        """
        
        response = await self.llm.ainvoke(prompt)
        content = response.content
        
        # Extraction logic
        content_upper = content.upper()
        decision = "FLAG FOR REVIEW"
        if "APPROVE" in content_upper: decision = "APPROVE"
        elif "REJECT" in content_upper or "BLOCK" in content_upper: decision = "REJECT"

        risk_level = "Medium"
        if "CRITICAL" in content_upper: risk_level = "Critical"
        elif "HIGH" in content_upper: risk_level = "High"
        elif "LOW" in content_upper: risk_level = "Low"
        elif decision == "REJECT": risk_level = "High" # Default for rejections
        
        return {
            "final_decision": decision,
            "risk_level": risk_level,
            "explanation": content
        }

    def build(self):
        """Build the state graph."""
        workflow = StateGraph(InvestigationState)

        # Add Nodes
        workflow.add_node("ml_analysis", self.ml_analysis_node)
        workflow.add_node("rag_context", self.rag_context_node)
        workflow.add_node("make_final_decision", self.final_decision_node)

        # Define Edges
        workflow.add_edge("ml_analysis", "rag_context")
        workflow.add_edge("rag_context", "make_final_decision")
        workflow.add_edge("make_final_decision", END)

        # Set Entry Point
        workflow.set_entry_point("ml_analysis")

        return workflow.compile()

# Instance
fraud_workflow = FraudWorkflow().build()

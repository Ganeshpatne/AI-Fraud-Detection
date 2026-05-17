"""
NVIDIA AI inference service for Explainable AI fraud explanations.
Uses NVIDIA NIM / inference endpoints (chat completions API).
"""
import logging
import httpx
from typing import List, Optional
from backend.config import NVIDIA_API_KEY, NVIDIA_API_BASE_URL, NVIDIA_MODEL

logger = logging.getLogger("fraud_detection")

SYSTEM_PROMPT = """You are a helpful and expert AI fraud analyst. 
Your primary goal is to analyze fraud data and provide professional, structured explanations. 
However, you should also be friendly and respond naturally to general greetings (like 'Hi', 'Hello', 'Who are you?') or questions about how this system works.

When explaining transactions, always include:
1. A summary of the transaction's status (Fraudulent or Legitimate)
2. Specific risk factors identified (if any)
3. Behavioral mismatches detected (if any)
4. Recommendation

Keep responses concise but informative. Produce purely PLAIN TEXT. DO NOT use asterisks (**) or markdown formatting."""



class NvidiaAIService:
    """Wrapper around NVIDIA inference API for fraud explanation generation."""

    def __init__(self):
        self.api_key = NVIDIA_API_KEY
        self.base_url = NVIDIA_API_BASE_URL
        self.model = NVIDIA_MODEL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def explain_fraud(
        self,
        transaction_id: str,
        amount: float,
        risk_score: float,
        confidence: float,
        fraud_type: Optional[str],
        reason: str,
        risk_factors: dict,
        user_question: str = "Why was this transaction flagged?",
    ) -> dict:
        """
        Generate an AI-powered fraud explanation using NVIDIA inference API.
        """
        # Build the prompt with transaction context
        context = f"""
Transaction Analysis Data:
- Transaction ID: {transaction_id}
- Amount: ${amount:,.2f}
- Risk Score: {risk_score}/100
- Confidence Score: {confidence:.2%}
- Detection Method: {fraud_type or 'N/A'}
- Detection Reason: {reason}
- Risk Factor Breakdown:
  * Amount Factor: {risk_factors.get('amount_factor', 0)}/35
  * Location Factor: {risk_factors.get('location_factor', 0)}/25
  * Device Factor: {risk_factors.get('device_factor', 0)}/20
  * Frequency Factor: {risk_factors.get('frequency_factor', 0)}/20

User Question: {user_question}
Risk status: {'FLAGGED AS FRAUDULENT' if risk_score >= 50 else 'SAFE / LEGITIMATE'}

Please provide a detailed yet concise explanation of the security status of this transaction based on the Risk status above.
If it is safe, clearly state that. If it is fraudulent, explain the risk factors and behavioral anomalies.
Do not use markdown syntax.
"""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": context},
                        ],
                        "temperature": 0.3,
                        "max_tokens": 1024,
                        "top_p": 0.9,
                    },
                )

                if response.status_code == 200:
                    data = response.json()
                    explanation = data["choices"][0]["message"]["content"]

                    # Extract structured info
                    risk_factor_list = []
                    behavior_mismatch = []

                    if risk_factors.get("amount_factor", 0) > 0:
                        risk_factor_list.append(
                            f"Unusual transaction amount (factor: {risk_factors['amount_factor']})"
                        )
                    if risk_factors.get("location_factor", 0) > 0:
                        risk_factor_list.append(
                            f"Geographic location mismatch (factor: {risk_factors['location_factor']})"
                        )
                        behavior_mismatch.append("Transaction location differs from user's usual location")
                    if risk_factors.get("device_factor", 0) > 0:
                        risk_factor_list.append(
                            f"Device fingerprint mismatch (factor: {risk_factors['device_factor']})"
                        )
                        behavior_mismatch.append("Transaction made from an unrecognized device")
                    if risk_factors.get("frequency_factor", 0) > 0:
                        risk_factor_list.append(
                            f"Transaction frequency spike (factor: {risk_factors['frequency_factor']})"
                        )
                        behavior_mismatch.append("Abnormal number of transactions in short time window")

                    logger.info(
                        "NVIDIA AI explanation generated for transaction %s", transaction_id
                    )

                    return {
                        "transaction_id": transaction_id,
                        "explanation": explanation,
                        "risk_factors": risk_factor_list,
                        "confidence_score": confidence,
                        "behavior_mismatch": behavior_mismatch,
                    }
                else:
                    error_msg = response.text
                    logger.error(
                        "NVIDIA API error (status %d): %s", response.status_code, error_msg
                    )
                    # Fallback to local explanation
                    return self._fallback_explanation(
                        transaction_id, amount, risk_score, confidence,
                        fraud_type, reason, risk_factors
                    )

        except Exception as e:
            logger.error("NVIDIA API request failed: %s", str(e))
            return self._fallback_explanation(
                transaction_id, amount, risk_score, confidence,
                fraud_type, reason, risk_factors
            )

    def _fallback_explanation(
        self,
        transaction_id: str,
        amount: float,
        risk_score: float,
        confidence: float,
        fraud_type: Optional[str],
        reason: str,
        risk_factors: dict,
    ) -> dict:
        """Generate a local explanation when the NVIDIA API is unavailable."""
        parts = [f"Transaction {transaction_id} was flagged with a risk score of {risk_score}/100."]
        risk_factor_list = []
        behavior_mismatch = []

        if risk_factors.get("amount_factor", 0) > 0:
            parts.append(f"The transaction amount of ${amount:,.2f} exceeds normal thresholds.")
            risk_factor_list.append("Abnormally high transaction amount")

        if risk_factors.get("location_factor", 0) > 0:
            parts.append("A geographic location mismatch was detected between the user's usual location and the transaction origin.")
            risk_factor_list.append("Geographic location mismatch")
            behavior_mismatch.append("Transaction location differs from user profile")

        if risk_factors.get("device_factor", 0) > 0:
            parts.append("The device used for this transaction does not match the user's known device fingerprint.")
            risk_factor_list.append("Device fingerprint mismatch")
            behavior_mismatch.append("Unknown device used")

        if risk_factors.get("frequency_factor", 0) > 0:
            parts.append("An unusual spike in transaction frequency was detected.")
            risk_factor_list.append("Transaction frequency anomaly")
            behavior_mismatch.append("Abnormal transaction frequency")

        if fraud_type:
            parts.append(f"Detection method: {fraud_type}.")

        return {
            "transaction_id": transaction_id,
            "explanation": " ".join(parts),
            "risk_factors": risk_factor_list,
            "confidence_score": confidence,
            "behavior_mismatch": behavior_mismatch,
        }


    async def generate_explanation(self, prompt: str, context: dict) -> str:
        """Generic text generation for the chatbot."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": "You are a helpful Fraud Detection AI Assistant."},
                            {"role": "user", "content": prompt},
                        ],
                        "temperature": 0.5,
                        "max_tokens": 1024,
                    },
                )
                if response.status_code == 200:
                    return response.json()["choices"][0]["message"]["content"]
                return f"Error from AI: {response.text}"
        except Exception as e:
            return f"Service error: {str(e)}"

# Singleton
nvidia_ai_service = NvidiaAIService()

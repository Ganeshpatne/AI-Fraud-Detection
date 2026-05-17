"""
LangGraph-powered Chatbot Agent for Fraud Detection.
Implements:
  - Greeting Router (skips DB queries for casual chat)
  - Query Decomposition
  - 8+ Database Tools
  - Conversation Memory
  - Multi-step Reasoning
"""
from typing import List, Dict, TypedDict, Annotated, Optional
import json
import operator
import re
from datetime import datetime, timedelta
from langgraph.graph import StateGraph, END
from backend.services.nvidia_ai_service import nvidia_ai_service
from backend.database import async_session
from sqlalchemy import select, func, and_, desc
from backend.models.database_models import Transaction, Alert, User, RiskScore

# ─── State Definition ──────────────────────────────────────────
class AgentState(TypedDict):
    query: str
    sub_queries: List[str]
    context: Annotated[List[Dict], operator.add]
    answer: str
    is_greeting: bool
    chat_history: List[Dict]

# ─── Greeting Patterns ─────────────────────────────────────────
GREETING_PATTERNS = [
    r"^(hi|hello|hey|howdy|greetings|good\s?(morning|afternoon|evening)|sup|yo)[\s!?.,]*$",
    r"^(who are you|what can you do|help|what is this|how are you)[\s!?.,]*$",
    r"^(thanks|thank you|bye|goodbye|see you|ok|okay|cool|great|nice)[\s!?.,]*$",
]

def _is_greeting(text: str) -> bool:
    """Check if the input is a greeting or casual chat."""
    clean = text.strip().lower()
    for pattern in GREETING_PATTERNS:
        if re.match(pattern, clean, re.IGNORECASE):
            return True
    return len(clean.split()) <= 3 and not any(
        kw in clean for kw in ["fraud", "transaction", "alert", "risk", "user", "how many", "show", "list", "count", "total"]
    )

# ─── Node 1: Router ────────────────────────────────────────────
async def router_node(state: AgentState):
    """Routes greetings directly to answer, skipping decompose+execute."""
    return {"is_greeting": _is_greeting(state["query"])}

# ─── Node 2: Decompose ─────────────────────────────────────────
async def decompose_query_node(state: AgentState):
    """Decomposes a complex query into simpler sub-queries."""
    # Build conversation context for better decomposition
    history_context = ""
    if state.get("chat_history"):
        recent = state["chat_history"][-3:]  # Last 3 messages
        history_context = "\n".join([f"{m['role']}: {m['content']}" for m in recent])

    prompt = f"""You are a Fraud Detection Expert. Decompose the following user query into simple, data-retrieval sub-queries.

Previous conversation:
{history_context}

Current Query: {state['query']}

Return a JSON list of strings ONLY. Each string should be a simple question.
Example: ["What is the total number of transactions?", "How many are fraudulent?"]
"""
    response = await nvidia_ai_service.generate_explanation(prompt, {})
    try:
        # Extract JSON array from response
        match = re.search(r'\[.*?\]', response, re.DOTALL)
        if match:
            queries = json.loads(match.group())
        else:
            queries = [state['query']]
    except (json.JSONDecodeError, ValueError):
        queries = [state['query']]

    return {"sub_queries": queries}

# ─── Node 3: Execute Tools ─────────────────────────────────────
async def execute_tools_node(state: AgentState):
    """Executes database queries using 8+ specialized tools."""
    results = []
    async with async_session() as db:
        for q in state['sub_queries']:
            ql = q.lower()
            result = await _route_to_tool(ql, db)
            results.append({"query": q, "data": result})

    return {"context": results}


async def _route_to_tool(query: str, db) -> str:
    """Routes a sub-query to the best matching database tool."""

    # Tool 1: Total transaction count
    if any(kw in query for kw in ["total transaction", "how many transaction", "count transaction", "number of transaction"]):
        count = (await db.execute(select(func.count(Transaction.id)))).scalar()
        fraud_count = (await db.execute(select(func.count(Transaction.id)).where(Transaction.is_fraud == True))).scalar()
        return f"Total transactions: {count}, Fraudulent: {fraud_count}, Legitimate: {count - fraud_count}"

    # Tool 2: Fraud statistics
    if any(kw in query for kw in ["fraud rate", "fraud percentage", "fraud stat", "how much fraud"]):
        total = (await db.execute(select(func.count(Transaction.id)))).scalar() or 1
        fraud = (await db.execute(select(func.count(Transaction.id)).where(Transaction.is_fraud == True))).scalar()
        rate = (fraud / total * 100) if total > 0 else 0
        return f"Fraud rate: {rate:.1f}% ({fraud} out of {total} transactions)"

    # Tool 3: Recent alerts
    if any(kw in query for kw in ["alert", "warning", "notification", "recent alert"]):
        alerts = (await db.execute(
            select(Alert).order_by(desc(Alert.created_at)).limit(5)
        )).scalars().all()
        if alerts:
            alert_list = [f"[{a.severity.upper()}] {a.message} ({a.created_at.strftime('%d %b %H:%M')})" for a in alerts]
            return f"Recent alerts ({len(alerts)}):\n" + "\n".join(alert_list)
        return "No alerts found in the system."

    # Tool 4: High-risk users
    if any(kw in query for kw in ["high risk user", "risky user", "suspicious user", "top fraud"]):
        result = await db.execute(
            select(User.username, func.count(Transaction.id).label("fraud_count"))
            .join(Transaction, Transaction.user_id == User.id)
            .where(Transaction.is_fraud == True)
            .group_by(User.username)
            .order_by(desc("fraud_count"))
            .limit(5)
        )
        rows = result.all()
        if rows:
            user_list = [f"{r.username}: {r.fraud_count} fraudulent transactions" for r in rows]
            return "High-risk users:\n" + "\n".join(user_list)
        return "No high-risk users found."

    # Tool 5: Location-based queries
    if any(kw in query for kw in ["location", "city", "region", "mumbai", "delhi", "pune", "lagos", "moscow", "new york"]):
        # Extract location name
        locations = ["mumbai", "delhi", "pune", "lagos", "moscow", "new york", "london", "tokyo", "bangalore", "chennai"]
        target_loc = next((loc for loc in locations if loc in query), None)
        if target_loc:
            count = (await db.execute(
                select(func.count(Transaction.id)).where(Transaction.location.ilike(f'%{target_loc}%'))
            )).scalar()
            fraud_count = (await db.execute(
                select(func.count(Transaction.id)).where(
                    and_(Transaction.location.ilike(f'%{target_loc}%'), Transaction.is_fraud == True)
                )
            )).scalar()
            return f"Transactions from {target_loc.title()}: {count} total, {fraud_count} fraudulent"
        else:
            # Top locations by fraud
            result = await db.execute(
                select(Transaction.location, func.count(Transaction.id).label("count"))
                .where(and_(Transaction.is_fraud == True, Transaction.location.isnot(None)))
                .group_by(Transaction.location)
                .order_by(desc("count"))
                .limit(5)
            )
            rows = result.all()
            if rows:
                loc_list = [f"{r.location}: {r.count} frauds" for r in rows]
                return "Top fraud locations:\n" + "\n".join(loc_list)
            return "No location data available."

    # Tool 6: Time-range queries
    if any(kw in query for kw in ["today", "last hour", "recent", "latest", "last 24", "this week"]):
        if "hour" in query:
            since = datetime.utcnow() - timedelta(hours=1)
        elif "today" in query:
            since = datetime.utcnow().replace(hour=0, minute=0, second=0)
        elif "week" in query:
            since = datetime.utcnow() - timedelta(days=7)
        else:
            since = datetime.utcnow() - timedelta(hours=24)

        count = (await db.execute(
            select(func.count(Transaction.id)).where(Transaction.timestamp >= since)
        )).scalar()
        fraud_count = (await db.execute(
            select(func.count(Transaction.id)).where(
                and_(Transaction.timestamp >= since, Transaction.is_fraud == True)
            )
        )).scalar()
        return f"Since {since.strftime('%d %b %H:%M')}: {count} transactions, {fraud_count} fraudulent"

    # Tool 7: Average risk score
    if any(kw in query for kw in ["average risk", "avg risk", "mean risk", "risk score"]):
        avg = (await db.execute(select(func.avg(Transaction.risk_score)))).scalar()
        max_risk = (await db.execute(select(func.max(Transaction.risk_score)))).scalar()
        return f"Average risk score: {float(avg or 0):.1f}/100, Maximum: {float(max_risk or 0):.1f}/100"

    # Tool 8: Specific user lookup
    if any(kw in query for kw in ["user ", "username", "analyst", "admin"]):
        users = ["admin", "analyst", "ganesh", "sujal", "aditya", "priya", "rahul", "john"]
        target_user = next((u for u in users if u in query), None)
        if target_user:
            result = await db.execute(
                select(User).where(User.username.ilike(f'%{target_user}%'))
            )
            user = result.scalar_one_or_none()
            if user:
                txn_count = (await db.execute(
                    select(func.count(Transaction.id)).where(Transaction.user_id == user.id)
                )).scalar()
                fraud_count = (await db.execute(
                    select(func.count(Transaction.id)).where(
                        and_(Transaction.user_id == user.id, Transaction.is_fraud == True)
                    )
                )).scalar()
                return f"User '{user.username}' (Role: {user.role}): {txn_count} transactions, {fraud_count} flagged as fraud"
            return f"User '{target_user}' not found."
        # List all users
        result = await db.execute(select(User.username, User.role).limit(10))
        rows = result.all()
        user_list = [f"{r.username} ({r.role})" for r in rows]
        return "Users in system:\n" + "\n".join(user_list)

    # Tool 9: System overview
    if any(kw in query for kw in ["overview", "summary", "status", "system", "dashboard"]):
        total = (await db.execute(select(func.count(Transaction.id)))).scalar()
        fraud = (await db.execute(select(func.count(Transaction.id)).where(Transaction.is_fraud == True))).scalar()
        users = (await db.execute(select(func.count(User.id)))).scalar()
        alerts = (await db.execute(select(func.count(Alert.id)))).scalar()
        avg_risk = (await db.execute(select(func.avg(Transaction.risk_score)))).scalar()
        return (f"System Overview:\n"
                f"- Total Transactions: {total}\n"
                f"- Fraudulent: {fraud}\n"
                f"- Registered Users: {users}\n"
                f"- Total Alerts: {alerts}\n"
                f"- Average Risk Score: {float(avg_risk or 0):.1f}/100")

    # Fallback: General search
    return f"I searched the database but couldn't find specific data for: '{query}'. Try asking about transactions, alerts, users, or fraud statistics."


# ─── Node 4: Generate Answer ───────────────────────────────────
async def generate_answer_node(state: AgentState):
    """Aggregates context and generates the final answer."""
    # Build conversation history for memory
    history_str = ""
    if state.get("chat_history"):
        recent = state["chat_history"][-5:]
        history_str = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in recent])

    if state.get("is_greeting", False):
        # Direct greeting response — no DB query needed
        prompt = f"""You are FraudShield AI, a friendly fraud detection assistant.
        
Previous conversation:
{history_str}

User says: {state['query']}

Respond naturally and warmly. If it's a greeting, introduce yourself briefly and ask how you can help with fraud investigation. Keep it to 2-3 sentences. Do not use markdown or asterisks."""
    else:
        context_str = json.dumps(state.get('context', []), default=str)
        prompt = f"""You are FraudShield AI, an expert fraud detection assistant.

Previous conversation:
{history_str}

User Question: {state['query']}
Retrieved Data: {context_str}

INSTRUCTIONS:
1. Use the 'Retrieved Data' to provide an accurate, data-driven answer.
2. Reference the conversation history if the user refers to previous messages.
3. If no relevant data was found, suggest what the user could ask instead.
4. Keep the response concise and professional (3-5 sentences max).
5. Do NOT use markdown formatting or asterisks.
"""
    answer = await nvidia_ai_service.generate_explanation(prompt, {})
    return {"answer": answer}

# ─── Routing Logic ─────────────────────────────────────────────
def should_skip_tools(state: AgentState) -> str:
    """Decide whether to skip decompose+execute for greetings."""
    if state.get("is_greeting", False):
        return "skip"
    return "continue"

# ─── Graph Construction ────────────────────────────────────────
workflow = StateGraph(AgentState)

workflow.add_node("router", router_node)
workflow.add_node("decomposer", decompose_query_node)
workflow.add_node("executor", execute_tools_node)
workflow.add_node("aggregator", generate_answer_node)

workflow.set_entry_point("router")
workflow.add_conditional_edges(
    "router",
    should_skip_tools,
    {
        "skip": "aggregator",      # Greetings go straight to answer
        "continue": "decomposer",  # Data queries go through full pipeline
    }
)
workflow.add_edge("decomposer", "executor")
workflow.add_edge("executor", "aggregator")
workflow.add_edge("aggregator", END)

# Compile the graph
fraud_agent = workflow.compile()

"""Supervisor / Dynamic Routing module for VectraBank multi-agent system."""
from typing import Dict, Any, List

INTENT_AGENT_ROUTING = {
    "fraud_investigation": {
        "title": "Fraud & Security Investigation",
        "description": "Customer query involves suspicious activity, unauthorized transactions, or security.",
        "agents": [
            "Enhanced_Data_Gatherer",
            "Enhanced_Fraud_Analyst",
            "Enhanced_Risk_Analyst",
            "Enhanced_Synthesis_Coordinator"
        ],
        "primary_collections": ["fraud_detection", "transaction_monitoring", "compliance"]
    },
    "loan_application": {
        "title": "Lending & Credit Evaluation",
        "description": "Customer query involves mortgage, personal loan, interest rates, or eligibility.",
        "agents": [
            "Enhanced_Data_Gatherer",
            "Enhanced_Loan_Analyst",
            "Enhanced_Risk_Analyst",
            "Enhanced_Synthesis_Coordinator"
        ],
        "primary_collections": ["loan_policies", "risk_assessment", "compliance"]
    },
    "wealth_planning": {
        "title": "Wealth & Financial Planning",
        "description": "Customer query involves retirement, investments, portfolio allocation, and savings.",
        "agents": [
            "Enhanced_Data_Gatherer",
            "Enhanced_Support_Specialist",
            "Enhanced_Loan_Analyst",
            "Enhanced_Synthesis_Coordinator"
        ],
        "primary_collections": ["customer_support", "loan_policies", "risk_assessment"]
    },
    "customer_service": {
        "title": "Customer Service & Inquiries",
        "description": "General banking inquiries, account servicing, or support protocol questions.",
        "agents": [
            "Enhanced_Data_Gatherer",
            "Enhanced_Support_Specialist",
            "Enhanced_Synthesis_Coordinator"
        ],
        "primary_collections": ["customer_support", "compliance"]
    },
    "comprehensive_audit": {
        "title": "Full 360-Degree Banking Audit",
        "description": "Comprehensive evaluation across fraud, lending, support, risk, and strategy.",
        "agents": [
            "Enhanced_Data_Gatherer",
            "Enhanced_Fraud_Analyst",
            "Enhanced_Loan_Analyst",
            "Enhanced_Support_Specialist",
            "Enhanced_Risk_Analyst",
            "Enhanced_Synthesis_Coordinator"
        ],
        "primary_collections": [
            "fraud_detection", "loan_policies", "customer_support",
            "risk_assessment", "transaction_monitoring", "compliance"
        ]
    }
}

def analyze_and_route(query: str, customer_profile_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Determine query intent, select appropriate agents, and define routing strategy."""
    q_lower = query.lower()
    
    # Keyword detection for intents
    fraud_keywords = ["fraud", "suspicious", "unauthorized", "stolen", "dispute", "compromised", "scam", "hack", "chargeback"]
    loan_keywords = ["loan", "mortgage", "borrow", "apr", "interest rate", "lending", "refinance", "credit line", "heloc", "eligibility"]
    wealth_keywords = ["invest", "retirement", "portfolio", "savings", "wealth", "401k", "pension", "compound", "financial planning"]
    support_keywords = ["support", "help", "contact", "agent", "service", "hours", "branch", "fees", "fee waiver", "document"]
    
    matched_intents = []
    if any(k in q_lower for k in fraud_keywords):
        matched_intents.append("fraud_investigation")
    if any(k in q_lower for k in loan_keywords):
        matched_intents.append("loan_application")
    if any(k in q_lower for k in wealth_keywords):
        matched_intents.append("wealth_planning")
    if any(k in q_lower for k in support_keywords):
        matched_intents.append("customer_service")
        
    # Decision logic
    if len(matched_intents) >= 2 or ("comprehensive" in q_lower or "all" in q_lower or "full" in q_lower):
        selected_intent = "comprehensive_audit"
        reasoning = f"Query spans multiple domains ({', '.join(matched_intents) if matched_intents else 'comprehensive scope'}). Deploying all 6 specialized agents for a complete 360° banking audit."
    elif len(matched_intents) == 1:
        selected_intent = matched_intents[0]
        cfg = INTENT_AGENT_ROUTING[selected_intent]
        reasoning = f"Intent identified as '{cfg['title']}'. Dynamically routing to {len(cfg['agents'])} targeted agents to maximize precision and avoid unnecessary overhead."
    else:
        # Default fallback
        selected_intent = "comprehensive_audit"
        reasoning = "General banking analysis request. Executing full multi-agent sequential pipeline."

    routing_config = INTENT_AGENT_ROUTING[selected_intent]
    
    return {
        "intent_key": selected_intent,
        "intent_title": routing_config["title"],
        "reasoning": reasoning,
        "selected_agents": routing_config["agents"],
        "agent_count": len(routing_config["agents"]),
        "primary_collections": routing_config["primary_collections"],
        "is_full_audit": selected_intent == "comprehensive_audit"
    }

"""Banking financial calculation tools for multi-agent reasoning and verification."""
import math
from typing import Dict, Any, List, Optional

def calculate_dti(monthly_debt: float, monthly_income: float) -> Dict[str, Any]:
    """Calculate exact Debt-To-Income (DTI) ratio and assess credit tier eligibility."""
    if monthly_income <= 0:
        return {"error": "Monthly income must be greater than zero", "dti_percent": 0.0}
    
    dti_percent = round((monthly_debt / monthly_income) * 100, 2)
    
    if dti_percent < 30.0:
        tier = "Tier A+ (Prime Premium)"
        eligibility = "Eligible for all prime lending facilities with preferred lowest rates."
    elif dti_percent < 35.0:
        tier = "Tier A (Prime)"
        eligibility = "Eligible for prime mortgage and personal credit facilities."
    elif dti_percent < 40.0:
        tier = "Tier B (Standard)"
        eligibility = "Eligible for standard lending with standard verification."
    elif dti_percent < 45.0:
        tier = "Tier C (Conditional)"
        eligibility = "Requires additional collateral or guarantor endorsement."
    else:
        tier = "Subprime / Excessive DTI"
        eligibility = "Exceeds standard risk appetite threshold; debt consolidation recommended."
        
    return {
        "monthly_income": monthly_income,
        "monthly_debt": monthly_debt,
        "dti_ratio": round(monthly_debt / monthly_income, 4),
        "dti_percent": dti_percent,
        "tier": tier,
        "eligibility_assessment": eligibility
    }

def calculate_loan_affordability(
    annual_income: float,
    credit_score: int,
    existing_monthly_debt: float,
    requested_amount: float = 50000.0,
    term_months: int = 60
) -> Dict[str, Any]:
    """Calculate borrower capacity, monthly payment, and maximum recommended credit line."""
    monthly_income = max(1.0, float(annual_income) / 12.0)
    
    # Determine base interest rate based on credit score
    if credit_score >= 760:
        apr = 3.50
    elif credit_score >= 700:
        apr = 5.25
    elif credit_score >= 640:
        apr = 8.50
    else:
        apr = 13.99
        
    # Amortization monthly payment formula: P * (r*(1+r)^n) / ((1+r)^n - 1)
    monthly_r = (apr / 100.0) / 12.0
    if monthly_r > 0:
        factor = math.pow(1 + monthly_r, term_months)
        monthly_payment = round(requested_amount * (monthly_r * factor) / (factor - 1), 2)
    else:
        monthly_payment = round(requested_amount / term_months, 2)
        
    projected_total_monthly_debt = existing_monthly_debt + monthly_payment
    projected_dti_percent = round((projected_total_monthly_debt / monthly_income) * 100, 2)
    
    # Max borrowing capacity capping DTI at 36%
    max_allowable_total_debt = monthly_income * 0.36
    max_available_monthly_for_loan = max(0.0, max_allowable_total_debt - existing_monthly_debt)
    if monthly_r > 0:
        max_borrowing_limit = round(max_available_monthly_for_loan * (factor - 1) / (monthly_r * factor), 2)
    else:
        max_borrowing_limit = round(max_available_monthly_for_loan * term_months, 2)

    return {
        "requested_amount": requested_amount,
        "term_months": term_months,
        "assigned_apr": apr,
        "monthly_payment": monthly_payment,
        "total_repayment": round(monthly_payment * term_months, 2),
        "total_interest": round((monthly_payment * term_months) - requested_amount, 2),
        "projected_dti_percent": projected_dti_percent,
        "max_recommended_borrowing_limit": max(0.0, max_borrowing_limit),
        "affordable": projected_dti_percent <= 36.0
    }

def calculate_investment_growth(
    current_savings: float,
    monthly_contribution: float,
    annual_return_pct: float = 7.0,
    years: int = 10
) -> Dict[str, Any]:
    """Calculate compound retirement and investment growth projections."""
    monthly_r = (annual_return_pct / 100.0) / 12.0
    total_months = years * 12
    
    future_principal = current_savings * math.pow(1 + monthly_r, total_months)
    if monthly_r > 0:
        future_annuity = monthly_contribution * ((math.pow(1 + monthly_r, total_months) - 1) / monthly_r)
    else:
        future_annuity = monthly_contribution * total_months
        
    projected_value = round(future_principal + future_annuity, 2)
    total_deposited = round(current_savings + (monthly_contribution * total_months), 2)
    interest_earned = round(projected_value - total_deposited, 2)
    
    return {
        "current_savings": current_savings,
        "monthly_contribution": monthly_contribution,
        "annual_return_pct": annual_return_pct,
        "horizon_years": years,
        "total_deposited": total_deposited,
        "projected_portfolio_value": projected_value,
        "estimated_growth_earnings": interest_earned,
        "multiplier": round(projected_value / max(1.0, total_deposited), 2)
    }

def scan_transaction_anomalies(transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Evaluate deterministic fraud and AML trigger rules against transaction activity."""
    flagged_alerts = []
    total_volume = 0.0
    large_tx_count = 0
    
    for tx in transactions:
        amt = float(tx.get("amount", 0.0))
        total_volume += amt
        desc = tx.get("description", "").lower()
        
        if amt >= 10000.0:
            flagged_alerts.append({
                "severity": "CRITICAL",
                "trigger": "AML Currency Transaction Report (CTR) Trigger",
                "detail": f"Transaction ${amt:,.2f} ('{tx.get('description')}') meets mandatory $10,000 threshold."
            })
        elif amt >= 2000.0:
            large_tx_count += 1
            flagged_alerts.append({
                "severity": "MEDIUM",
                "trigger": "High-Value Transaction Monitored",
                "detail": f"Transaction ${amt:,.2f} ('{tx.get('description')}') requires velocity cross-check."
            })
            
        if any(term in desc for term in ["crypto", "wire transfer", "unknown payee", "atm withdraw"]):
            flagged_alerts.append({
                "severity": "HIGH",
                "trigger": "Elevated Risk Merchant / Pattern",
                "detail": f"Suspicious activity identifier found in transaction: '{tx.get('description')}'."
            })
            
    risk_level = "LOW"
    if any(a["severity"] == "CRITICAL" for a in flagged_alerts):
        risk_level = "CRITICAL"
    elif any(a["severity"] == "HIGH" for a in flagged_alerts) or large_tx_count >= 2:
        risk_level = "HIGH"
    elif flagged_alerts:
        risk_level = "MEDIUM"
        
    return {
        "total_transactions_analyzed": len(transactions),
        "total_volume": round(total_volume, 2),
        "alerts_count": len(flagged_alerts),
        "risk_level": risk_level,
        "alerts": flagged_alerts
    }

def run_banking_tool_suite(customer_profile_dict: Dict[str, Any], query: str) -> Dict[str, Any]:
    """Execute all relevant banking tools for a customer and format verified computational outputs."""
    income = float(customer_profile_dict.get("income", 75000.0))
    monthly_income = income / 12.0
    credit_score = int(customer_profile_dict.get("credit_score", 720))
    transactions = customer_profile_dict.get("recent_transactions", [])
    
    # Calculate estimated monthly debt from known expenses (e.g. mortgage/loans in transactions)
    mortgage_or_debt = 0.0
    for tx in transactions:
        desc = tx.get("description", "").lower()
        if "mortgage" in desc or "loan" in desc or "payment" in desc:
            mortgage_or_debt += float(tx.get("amount", 0.0))
    if mortgage_or_debt == 0.0:
        mortgage_or_debt = monthly_income * 0.20 # Fallback conservative 20%
        
    dti_result = calculate_dti(mortgage_or_debt, monthly_income)
    affordability = calculate_loan_affordability(income, credit_score, mortgage_or_debt)
    investment = calculate_investment_growth(current_savings=15000.0, monthly_contribution=300.0, annual_return_pct=7.0, years=15)
    fraud_scan = scan_transaction_anomalies(transactions)
    
    return {
        "dti_metrics": dti_result,
        "loan_affordability": affordability,
        "wealth_projection": investment,
        "fraud_rule_scan": fraud_scan
    }

"""Offline (rule-based) implementations of the six banking agents.

Used when no LLM credentials (Azure AI Foundry / OpenAI) are configured so the
full pipeline -- RAG retrieval, sequential agent hand-off, report synthesis --
still runs end to end. Each agent reads the customer profile, the retrieved
policy chunks and the previous agents' outputs, and applies the thresholds
documented in ``banking_documents/``.
"""

from datetime import datetime
from typing import Any, Dict, List

AGENT_NAMES = [
    "Enhanced_Data_Gatherer",
    "Enhanced_Fraud_Analyst",
    "Enhanced_Loan_Analyst",
    "Enhanced_Support_Specialist",
    "Enhanced_Risk_Analyst",
    "Enhanced_Synthesis_Coordinator",
]

# Keywords used to classify a query's intent
_INTENTS = {
    "fraud": ["fraud", "suspicious", "unauthorized", "stolen", "scam", "hack", "dispute", "unknown charge"],
    "loan": ["loan", "mortgage", "borrow", "credit line", "eligib", "financing", "refinanc"],
    "planning": ["plan", "invest", "retire", "saving", "wealth", "portfolio"],
    "support": ["help", "access", "locked", "complaint", "card", "fee", "statement", "issue"],
}

# Descriptions that represent recurring obligations (used for DTI estimation)
_DEBT_KEYWORDS = ["mortgage", "rent", "car payment", "loan", "credit card payment"]


def classify_intent(query: str) -> List[str]:
    q = query.lower()
    intents = [name for name, words in _INTENTS.items() if any(w in q for w in words)]
    return intents or ["general"]


def _tenure_years(since: str) -> float:
    try:
        return (datetime.now() - datetime.strptime(since, "%Y-%m-%d")).days / 365.25
    except (ValueError, TypeError):
        return 0.0


def _metrics(profile: Dict[str, Any]) -> Dict[str, Any]:
    income = float(profile.get("income") or 0)
    txs = profile.get("recent_transactions") or []
    monthly_income = income / 12 if income else 0
    deposits = [float(t.get("amount", 0)) for t in txs if "deposit" in str(t.get("description", "")).lower()]
    debts = [float(t.get("amount", 0)) for t in txs
             if any(k in str(t.get("description", "")).lower() for k in _DEBT_KEYWORDS)]
    outflows = [float(t.get("amount", 0)) for t in txs if "deposit" not in str(t.get("description", "")).lower()]
    monthly_debt = sum(debts)
    dti = monthly_debt / monthly_income if monthly_income else 0.0
    total_out = sum(outflows)
    savings_rate = max(0.0, (monthly_income - total_out) / monthly_income) if monthly_income else 0.0
    amounts = [float(t.get("amount", 0)) for t in txs]
    return {
        "income": income,
        "monthly_income": monthly_income,
        "monthly_debt": monthly_debt,
        "dti": dti,
        "savings_rate": savings_rate,
        "deposits": deposits,
        "outflows": total_out,
        "tx_count": len(txs),
        "max_tx": max(amounts) if amounts else 0.0,
        "tenure": _tenure_years(profile.get("customer_since", "")),
        "products": profile.get("banking_products") or [],
        "credit": int(profile.get("credit_score") or 0),
        "fees": [t for t in txs if "fee" in str(t.get("description", "")).lower()],
    }


def _income_tier(income: float) -> tuple:
    if income >= 100000:
        return "A+", 0.30, "3+ years"
    if income >= 75000:
        return "A", 0.35, "2+ years"
    if income >= 50000:
        return "B", 0.40, "1+ years"
    if income >= 30000:
        return "C", 0.45, "6+ months"
    return "Below C", 0.0, "n/a"


def _credit_tier(score: int) -> tuple:
    if score >= 750:
        return "Excellent", 3.5, 90
    if score >= 700:
        return "Good", 4.5, 85
    if score >= 650:
        return "Fair", 6.0, 80
    return "Review", None, None


def _policy_lines(search_results: List[Dict], collections: List[str] = None, limit: int = 2) -> str:
    picked = [r for r in search_results if not collections or r.get("collection") in collections][:limit]
    if not picked:
        picked = search_results[:limit]
    lines = []
    for r in picked:
        lines.append(f"- `{r.get('filename', 'Unknown')}` ({r.get('collection', '?')}, "
                     f"relevance {float(r.get('final_score', r.get('relevance_score', 0))):.2f})")
    return "\n".join(lines) if lines else "- No matching policy chunks retrieved"


def _fmt(v: float) -> str:
    return f"${v:,.2f}"


# --------------------------------------------------------------------------- agents

def _data_gatherer(p, q, sr, policies, prev) -> str:
    m = _metrics(p)
    filled = sum(bool(p.get(k)) for k in ["income", "credit_score", "account_type", "customer_since",
                                          "recent_transactions", "banking_products", "last_review_date"])
    completeness = round(filled / 7 * 100)
    segment = {"premium_plus": "Premium+", "premium": "Premium", "standard": "Standard", "basic": "Basic"}.get(
        p.get("account_type", "standard"), "Standard")
    intents = ", ".join(classify_intent(q))
    return f"""## Customer Financial Summary — {p.get('customer_id')}

| Metric | Value |
|---|---|
| Annual income | {_fmt(m['income'])} (monthly {_fmt(m['monthly_income'])}) |
| Credit score | {m['credit'] or 'unknown'} |
| Segment | {segment} (`{p.get('account_type')}`) |
| Tenure | {m['tenure']:.1f} years (since {p.get('customer_since') or 'n/a'}) |
| Active products | {len(m['products'])} — {', '.join(m['products']) or 'none'} |
| Recurring obligations | {_fmt(m['monthly_debt'])}/month |
| Debt-to-income (est.) | {m['dti']:.1%} |
| Savings rate (est.) | {m['savings_rate']:.1%} |

### Data Quality Assessment
- Completeness score: **{completeness}%** ({filled}/7 profile fields populated)
- {m['tx_count']} recent transactions available{' — limited history, treat estimates with caution' if m['tx_count'] < 3 else ''}
- Last profile review: {p.get('last_review_date') or 'never'}

### Query Classification
Detected intent(s): **{intents}** — "{q}"

### Policy Relevance Mapping
{_policy_lines(sr, limit=4)}

### Key Observations
- {"Stable salary deposits observed" if m['deposits'] else "No salary deposits found in the recent window"}
- {"Fee events detected (" + str(len(m['fees'])) + ") — indicates possible cash-flow stress" if m['fees'] else "No penalty or overdraft fees detected"}
- Largest single transaction: {_fmt(m['max_tx'])}
"""


def _fraud_analyst(p, q, sr, policies, prev) -> str:
    m = _metrics(p)
    txs = p.get("recent_transactions") or []
    intents = classify_intent(q)
    indicators = []
    score = 10
    high = [t for t in txs if float(t.get("amount", 0)) > 2000 and "deposit" not in str(t.get("description", "")).lower()]
    medium = [t for t in txs if 500 <= float(t.get("amount", 0)) <= 2000 and "deposit" not in str(t.get("description", "")).lower()]
    if high:
        score += 25
        indicators.append(f"{len(high)} outgoing transaction(s) above the $2,000 high-risk threshold")
    if medium:
        score += 5 * min(len(medium), 3)
        indicators.append(f"{len(medium)} transaction(s) in the $500–$2,000 medium-risk band")
    if m["max_tx"] > 10000:
        score += 20
        indicators.append(f"Very large transaction ({_fmt(m['max_tx'])}) — CTR/AML review threshold")
    if m["fees"]:
        score += 10
        indicators.append("Overdraft/penalty fees — possible account stress or unauthorized debits")
    if "fraud" in intents:
        score += 25
        indicators.append("Customer self-reported suspicious activity — mandatory P0 investigation")
    if m["tenure"] < 1:
        score += 10
        indicators.append("Account younger than 1 year — elevated account-takeover exposure")
    score = min(score, 100)
    level = "Critical" if score >= 75 else "High" if score >= 50 else "Medium" if score >= 25 else "Low"
    escalation = {"Critical": "Level 3 — account freeze & security investigation",
                  "High": "Level 2 — manual review by fraud team",
                  "Medium": "Level 1 — automated flagging & customer notification",
                  "Low": "Standard monitoring"}[level]
    timeline = {"Critical": "Immediate", "High": "Immediate", "Medium": "2-hour window", "Low": "24-hour review cycle"}[level]
    tx_rows = "\n".join(
        f"| {t.get('ts', 'n/a')} | {t.get('description', 'n/a')} | {_fmt(float(t.get('amount', 0)))} | "
        f"{'High' if float(t.get('amount', 0)) > 2000 and 'deposit' not in str(t.get('description', '')).lower() else 'Medium' if float(t.get('amount', 0)) >= 500 and 'deposit' not in str(t.get('description', '')).lower() else 'Low'} |"
        for t in txs[:10]) or "| — | No transactions | — | — |"
    return f"""## Transaction Pattern Analysis

| Date | Description | Amount | Policy band |
|---|---|---|---|
{tx_rows}

### Fraud Risk Score: **{score}/100 ({level})**

### Suspicious Indicators
{chr(10).join('- ' + i for i in indicators) if indicators else '- None identified; activity is consistent with expected salary/bill patterns'}

### Typology Screening
- Account takeover: {"possible — verify recent logins/devices" if "fraud" in intents or m['tenure'] < 1 else "not indicated"}
- Card fraud: {"review card-present vs. card-not-present activity" if "fraud" in intents else "not indicated"}
- Money laundering: {"structuring/large-value pattern requires AML review" if m['max_tx'] > 10000 else "not indicated"}

### Recommended Actions
- Escalation: **{escalation}** (response: {timeline})
- {"Enable biometric verification for high-value transactions and reset credentials" if score >= 50 else "Maintain real-time monitoring and behavioral analytics"}
- {"Contact customer to confirm each disputed transaction; issue replacement card if needed" if "fraud" in intents else "Notify customer of any new-payee or geographic anomalies"}

**Policy basis:**
{_policy_lines(sr, ["fraud_detection", "transaction_monitoring"])}
"""


def _loan_analyst(p, q, sr, policies, prev) -> str:
    m = _metrics(p)
    tier, max_dti, emp = _income_tier(m["income"])
    ctier, apr, ltv = _credit_tier(m["credit"])
    conditions = []
    if tier == "Below C":
        decision = "Declined"
        conditions.append("Income below the $30,000 Tier C minimum")
    elif ctier == "Review":
        decision = "Review Required"
        conditions.append(f"Credit score {m['credit']} is below 650 — case-by-case underwriting")
    elif m["dti"] > max_dti:
        decision = "Conditional"
        conditions.append(f"Estimated DTI {m['dti']:.1%} exceeds Tier {tier} limit of {max_dti:.0%}")
    else:
        decision = "Approved" if ctier in ("Excellent", "Good") else "Conditional"
        if decision == "Conditional":
            conditions.append("Fair credit tier — standard rate and reduced LTV apply")
    headroom = max(0.0, max_dti * m["monthly_income"] - m["monthly_debt"]) if max_dti else 0.0
    rate = (apr or 8.0) / 100 / 12
    n = 360
    max_loan = headroom * ((1 - (1 + rate) ** -n) / rate) if headroom and rate else 0.0
    doc_level = {"A+": "Premium", "A": "Comprehensive", "B": "Standard", "C": "Basic"}.get(tier, "Comprehensive")
    products = []
    if decision in ("Approved", "Conditional"):
        if "mortgage" not in m["products"] and ("loan" in classify_intent(q) or m["income"] >= 75000):
            products.append(f"30-year fixed mortgage at ~{apr or 6.0}% APR, up to {ltv or 80}% LTV")
        products.append("Personal loan / line of credit sized to DTI headroom")
        if "credit_card" not in m["products"] and m["credit"] >= 650:
            products.append("Rewards credit card")
    else:
        products.append("Secured credit-builder loan")
        products.append("Financial coaching before re-application (90 days)")
    return f"""## Eligibility Determination: **{decision}**

| Criterion | Customer | Policy |
|---|---|---|
| Income tier | {_fmt(m['income'])} → **Tier {tier}** | A+ $100K / A $75K / B $50K / C $30K |
| Credit tier | {m['credit']} → **{ctier}** | Excellent 750+ / Good 700+ / Fair 650+ |
| Debt-to-income | {m['dti']:.1%} | ≤ {max_dti:.0%} for Tier {tier} |
| Employment history required | — | {emp} |

### Applicable Terms
- Rate: {f"{apr}% APR" if apr else "set by underwriting"}; LTV: {f"{ltv}%" if ltv else "case-by-case"}
- Monthly payment headroom: {_fmt(headroom)}
- Maximum recommended loan (30-yr amortization): **{_fmt(round(max_loan, -3))}**
- Required documentation level: **{doc_level}**

### Conditions / Flags
{chr(10).join('- ' + c for c in conditions) if conditions else '- None — meets all tier requirements'}

### Product Recommendations
{chr(10).join('- ' + x for x in products)}

**Policy basis:**
{_policy_lines(sr, ["loan_policies"])}
"""


def _support_specialist(p, q, sr, policies, prev) -> str:
    m = _metrics(p)
    intents = classify_intent(q)
    if "fraud" in intents:
        priority, sla = "P0 - Critical", "15 minutes (24/7)"
    elif "loan" in intents or "support" in intents:
        priority, sla = "P1 - High", "2 hours (business hours)"
    elif "planning" in intents:
        priority, sla = "P2 - Medium", "24 hours (business days)"
    else:
        priority, sla = "P3 - Low", "48 hours"
    retention = "High" if (len(m["products"]) <= 1 or m["fees"] or "fraud" in intents) else \
        "Medium" if len(m["products"]) <= 3 else "Low"
    clv = "High" if m["income"] >= 75000 and len(m["products"]) >= 4 else \
        "Medium" if m["income"] >= 40000 else "Developing"
    gaps = []
    if "savings" not in m["products"]:
        gaps.append("No savings product — emergency-fund gap")
    if m["fees"]:
        gaps.append("Overdraft fees incurred — offer overdraft protection / low-balance alerts")
    if not p.get("last_review_date") or _tenure_years(p.get("last_review_date")) > 1:
        gaps.append("Relationship review overdue (>12 months)")
    if "investment" not in m["products"] and "planning" in intents:
        gaps.append("No investment product despite planning interest")
    tier_route = "Tier 3 — Senior banking specialist" if priority.startswith("P0") else \
        "Tier 2 — Specialized banking agent" if priority.startswith("P1") else "Tier 1 — Digital / basic support"
    return f"""## Customer Experience Assessment

- Service priority: **{priority}** — response SLA **{sla}**
- Routing: {tier_route}
- Customer lifetime value: **{clv}**
- Retention risk: **{retention}**

### Service Gaps & Opportunities
{chr(10).join('- ' + g for g in gaps) if gaps else '- No material service gaps identified'}

### Recommended Engagement Actions
- {"Proactive outbound call from fraud desk; confirm identity and walk through disputed items" if "fraud" in intents else "Assign relationship manager follow-up within SLA"}
- Enable digital self-service: mobile alerts, card controls (freeze/unfreeze), e-statements
- {"Premium concierge & annual wealth review" if clv == "High" else "Bundle offer to deepen relationship (savings + card + auto-pay)"}
- Track against quality targets: 85% first-contact resolution, 90% CSAT

**Policy basis:**
{_policy_lines(sr, ["customer_support"])}
"""


def _risk_analyst(p, q, sr, policies, prev) -> str:
    m = _metrics(p)
    intents = classify_intent(q)
    credit_p = 5 if m["credit"] >= 750 else 12 if m["credit"] >= 700 else 22 if m["credit"] >= 650 else 40
    if m["dti"] > 0.4:
        credit_p += 10
    market_p = 8 if m["income"] >= 75000 else 15 if m["income"] >= 40000 else 25
    op_p = 30 if "fraud" in intents else 8
    comp_p = 20 if m["max_tx"] > 10000 or "fraud" in intents else 5
    rep_p = 25 if "fraud" in intents else 6

    def lvl(x):
        return "Critical" if x > 60 else "High" if x >= 30 else "Medium" if x >= 10 else "Low"

    rows = [("Credit", credit_p), ("Market", market_p), ("Operational", op_p),
            ("Compliance", comp_p), ("Reputational", rep_p)]
    overall = round(sum(x for _, x in rows) / len(rows), 1)
    review = "Quarterly" if lvl(overall) in ("High", "Critical") else \
        "Semi-annual" if lvl(overall) == "Medium" else "Annual"
    if m["tenure"] < 0.25:
        review = "90-day intensive monitoring (new customer)"
    matrix = "\n".join(f"| {n} | {x}% | {lvl(x)} |" for n, x in rows)
    mitigations = sorted(rows, key=lambda r: -r[1])
    mit_text = {
        "Credit": "Enhanced due diligence on new credit; credit-builder enrolment",
        "Market": "Diversify product mix; rate-lock options on lending",
        "Operational": "Credential reset, device re-verification, transaction holds pending review",
        "Compliance": "KYC refresh and AML screening; document SAR decision",
        "Reputational": "Fast, transparent resolution with customer communication log",
    }
    return f"""## Multi-dimensional Risk Assessment Matrix

| Category | Probability | Level |
|---|---|---|
{matrix}

### Overall Risk: **{overall}% ({lvl(overall)})**

### Compliance Status
- KYC: profile on file{"; refresh recommended" if m['tenure'] < 1 or "fraud" in intents else ", current"}
- AML: {"review required — large-value activity" if m['max_tx'] > 10000 else "no reportable activity in window"}
- Fraud policy v2.0: {"active investigation required" if "fraud" in intents else "compliant"}

### Prioritized Mitigations
{chr(10).join(f"{i}. **{n}** — {mit_text[n]}" for i, (n, _) in enumerate(mitigations[:3], 1))}

### Monitoring Schedule
- Review frequency: **{review}**

**Policy basis:**
{_policy_lines(sr, ["risk_assessment", "compliance"])}
"""


def _synthesis(p, q, sr, policies, prev) -> str:
    m = _metrics(p)
    intents = classify_intent(q)

    def grab(agent: str, marker: str) -> str:
        text = prev.get(agent, "")
        for line in text.splitlines():
            if marker in line:
                return line.split("**")[1] if "**" in line else line.strip()
        return "n/a"

    fraud = grab("Enhanced_Fraud_Analyst", "Fraud Risk Score")
    loan = grab("Enhanced_Loan_Analyst", "Eligibility Determination")
    prio = grab("Enhanced_Support_Specialist", "Service priority")
    risk = grab("Enhanced_Risk_Analyst", "Overall Risk")
    ctier = _credit_tier(m["credit"])[0]
    tier = _income_tier(m["income"])[0]

    focus = {
        "fraud": "securing the account and resolving the reported suspicious activity",
        "loan": "determining lending eligibility and structuring an appropriate offer",
        "planning": "building a long-term financial plan with investment and retirement products",
        "support": "resolving the service request quickly within SLA",
        "general": "a holistic review of the relationship",
    }[intents[0]]
    actions = []
    if "fraud" in intents:
        actions += ["Fraud desk: contact customer within 15 minutes, place temporary holds on disputed items",
                    "Security: reset credentials and re-verify devices today"]
    if "loan" in intents:
        actions += [f"Lending: issue pre-qualification letter based on '{loan}' determination within 2 hours",
                    "Collect required documentation package"]
    if "planning" in intents:
        actions += ["Wealth team: schedule a financial-planning session this week",
                    "Prepare retirement contribution and diversified portfolio proposal"]
    if not actions:
        actions = ["Relationship manager: follow up within SLA", "Refresh customer profile and preferences"]

    return f"""## Executive Summary

Customer **{p.get('customer_id')}** ({p.get('account_type')} account, {m['tenure']:.1f} years tenure) asked: *"{q}"*. The engagement centres on {focus}. The customer earns {_fmt(m['income'])} annually (Tier {tier}) with a {ctier.lower()} credit score of {m['credit']} and holds {len(m['products'])} product(s).

Across six specialist reviews, fraud exposure is rated **{fraud}**, lending is **{loan}**, service priority is **{prio}**, and enterprise risk is **{risk}**. Estimated debt-to-income is {m['dti']:.1%} with a savings rate of {m['savings_rate']:.1%}.

## Consolidated Key Findings
1. Fraud risk: {fraud}
2. Loan eligibility: {loan} (Tier {tier}, {ctier} credit)
3. Service priority: {prio}
4. Enterprise risk: {risk}
5. Product engagement: {len(m['products'])} product(s) — {"strong relationship" if len(m['products']) >= 4 else "cross-sell opportunity"}

## Strategic Recommendations
1. {"Prioritise account security and transparent dispute resolution" if "fraud" in intents else "Deliver a tailored offer aligned to the stated goal"}
2. {"Offer credit-building and savings products to strengthen financial resilience" if m['credit'] < 700 else "Leverage strong credit for preferential pricing and premium products"}
3. Align monitoring cadence with the risk analyst's schedule and refresh KYC as needed

## Immediate Action Items
{chr(10).join('- ' + a for a in actions)}

## Long-term Relationship Strategy
- {"Graduate customer from basic to standard tier as credit and savings improve" if p.get('account_type') == 'basic' else "Retain via premium service, annual reviews and loyalty pricing"}
- Expand product footprint (target {max(len(m['products']) + 1, 3)}+ products) with needs-based offers
- Re-assess in line with policy review frequency
"""


_AGENTS = {
    "Enhanced_Data_Gatherer": _data_gatherer,
    "Enhanced_Fraud_Analyst": _fraud_analyst,
    "Enhanced_Loan_Analyst": _loan_analyst,
    "Enhanced_Support_Specialist": _support_specialist,
    "Enhanced_Risk_Analyst": _risk_analyst,
    "Enhanced_Synthesis_Coordinator": _synthesis,
}


def run_offline_agent(name: str, profile: Dict[str, Any], query: str, search_results: List[Dict],
                      policies: Dict[str, Any], previous: Dict[str, str]) -> str:
    """Produce the named agent's analysis without calling an LLM."""
    return _AGENTS[name](profile, query, search_results, policies, previous).strip()

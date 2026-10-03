"""
Unit tests for supervisor routing logic in backend/supervisor.py
"""
from backend.supervisor import route_query_to_specialist

def test_route_loan():
    agent, reason = route_query_to_specialist("Can I get a 30-year fixed mortgage with 15% down?")
    assert agent == "Loan Advisor"

def test_route_compliance():
    agent, reason = route_query_to_specialist("What is the AML threshold for an international wire transfer?")
    assert agent == "Compliance Officer"

def test_route_investment():
    agent, reason = route_query_to_specialist("How much will my $10,000 grow at 7% compound interest in 20 years?")
    assert agent == "Investment Advisor"

def test_route_account_general():
    agent, reason = route_query_to_specialist("What is the fee for an overdraft on my checking account?")
    assert agent == "Account Specialist"

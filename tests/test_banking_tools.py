"""
Unit tests for deterministic banking tools in backend/banking_tools.py
"""
import pytest
from backend.banking_tools import calculate_dti, calculate_mortgage_payment, calculate_compound_interest, check_aml_transaction

def test_dti_standard():
    res = calculate_dti(monthly_debt=2000, gross_monthly_income=6000)
    assert res["status"] == "success"
    assert res["dti_percent"] == 33.33
    assert res["is_qualified_standard"] is True

def test_dti_over_limit():
    res = calculate_dti(monthly_debt=3000, gross_monthly_income=6000)
    assert res["dti_percent"] == 50.0
    assert res["is_qualified_standard"] is False

def test_mortgage_calculation():
    res = calculate_mortgage_payment(principal=300000, annual_rate_pct=6.0, term_years=30)
    assert res["monthly_principal_and_interest"] == 1798.65
    assert res["total_repayment"] == 647514.0

def test_aml_trigger():
    res = check_aml_transaction(amount=15000, transaction_type="cash_deposit")
    assert res["requires_ctr_filing"] is True
    assert res["risk_level"] == "ELEVATED"

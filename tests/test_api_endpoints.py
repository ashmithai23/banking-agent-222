"""
Integration tests for FastAPI application endpoints
"""
from fastapi.testclient import TestClient
from backend.api import app

client = TestClient(app)

def test_root_health():
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] == "online"

def test_dti_tool_endpoint():
    res = client.post("/api/tools/dti", json={"monthly_debt": 1500, "gross_monthly_income": 5000})
    assert res.status_code == 200
    data = res.json()
    assert data["dti_percent"] == 30.0
    assert data["is_qualified_standard"] is True

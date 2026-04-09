from fastapi.testclient import TestClient
import sys, os
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_schema():
    response = client.get("/schema")
    assert response.status_code == 200
    data = response.json()
    assert "technology_to_sector" in data

def test_transform_success():
    DATA_DIR = Path(__file__).parent / "data"
    
    # Use real test data from tests/data/
    with open(DATA_DIR / "TotalDiscountedCost.csv", "rb") as f1, \
         open(DATA_DIR / "TotalAnnualTechnologyActivity.csv", "rb") as f2, \
         open(DATA_DIR / "AnnualEmissions.csv", "rb") as f3:
        response = client.post("/transform", files={
            "total_discounted_cost": ("TotalDiscountedCost.csv", f1, "text/csv"),
            "total_annual_technology_activity": ("TotalAnnualTechnologyActivity.csv", f2, "text/csv"),
            "annual_emissions": ("AnnualEmissions.csv", f3, "text/csv"),
        }, data={"scenario": "test", "run_id": "api_test_001"})
    assert response.status_code == 200
    body = response.json()
    assert "og_parameters" in body
    assert "mapping_trace" in body["og_parameters"]

def test_transform_missing_file_returns_422():
    response = client.post("/transform", files={}, data={"scenario": "test", "run_id": "x"})
    assert response.status_code == 422

def test_history():
    response = client.get("/history")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

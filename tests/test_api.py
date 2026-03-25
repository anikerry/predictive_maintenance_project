from fastapi.testclient import TestClient
from src.api import app  # Imports your FastAPI app
import pytest
from httpx import ASGITransport, AsyncClient

# Initialize the test client
client = TestClient(app)

def test_health_check():
    """Test if the API boots up and the root endpoint works."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Predictive Maintenance API is running" in response.json()["message"]

def test_predict_healthy_machine():
    """Test if the model correctly predicts a healthy machine."""
    # This is the exact dummy data we used in Swagger UI
    payload = {
        "Air_temperature_K": 298.1,
        "Process_temperature_K": 308.6,
        "Rotational_speed_rpm": 1551.0,
        "Torque_Nm": 42.8,
        "Tool_wear_min": 0.0,
        "Type_L": 0,
        "Type_M": 1
    }
    
    response = client.post("/predict", json=payload)
    
    # 1. Check if the request was successful
    assert response.status_code == 200
    
    data = response.json()
    
    # 2. Check if the model predicted "Healthy"
    assert data["machine_status"] == "Healthy ✅"
    
    # 3. Check if the probability is formatted correctly
    assert "%" in data["failure_probability"]
    assert data["sensor_data_processed"] is True

@pytest.mark.anyio
async def test_root():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get("/")
    assert response.status_code == 200
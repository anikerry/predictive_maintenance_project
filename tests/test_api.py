import pytest
from httpx import ASGITransport, AsyncClient
import src.api as api_module


class _DummyModel:
    def predict(self, X):
        return [0]


@pytest.fixture(autouse=True)
def _mock_model(monkeypatch):
    dummy = _DummyModel()
    # Patch whichever model variable exists in src.api
    for name in ("model", "rf_model", "clf", "classifier", "loaded_model", "pipeline"):
        if hasattr(api_module, name):
            monkeypatch.setattr(api_module, name, dummy, raising=False)


@pytest.mark.anyio
async def test_root():
    async with AsyncClient(transport=ASGITransport(app=api_module.app), base_url="http://testserver") as client:
        response = await client.get("/")
    assert response.status_code == 200


@pytest.mark.anyio
async def test_predict_healthy_machine():
    # Keep payload aligned with existing API schema
    payload = {
        "Air_temperature_K": 298.1,
        "Process_temperature_K": 308.6,
        "Rotational_speed_rpm": 1551.0,
        "Torque_Nm": 42.8,
        "Tool_wear_min": 0.0,
        "Type_L": 0,
        "Type_M": 1
    }

    async with AsyncClient(transport=ASGITransport(app=api_module.app), base_url="http://testserver") as client:
        response = await client.post("/predict", json=payload)

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["prediction"] == 0
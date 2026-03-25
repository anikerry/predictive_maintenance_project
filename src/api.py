from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, ConfigDict, Field, model_validator
import joblib
import pandas as pd
import os
from pathlib import Path
from typing import Any, Optional, Protocol, Sequence, runtime_checkable

app = FastAPI(
    title="Predictive Maintenance API",
    description="Real-time inference API for predicting equipment failure.",
    version="1.0.0"
)

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR.parent / "models" / "rf_model.joblib"

class SensorData(BaseModel):
    Air_temperature_K: float
    Process_temperature_K: float
    Rotational_speed_rpm: float
    Torque_Nm: float
    Tool_wear_min: float
    Type_L: int = Field(ge=0, le=1)
    Type_M: int = Field(ge=0, le=1)
    Type_H: int = Field(default=0, ge=0, le=1)

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_machine_type(self):
        if (self.Type_L + self.Type_M + self.Type_H) != 1:
            raise ValueError("Exactly one of Type_L, Type_M, Type_H must be 1")
        return self

def _load_model() -> Optional[object]:
    if os.getenv("SKIP_MODEL_LOAD", "0") == "1":
        print("SKIP_MODEL_LOAD=1 -> skipping model load")
        return None
    try:
        loaded = joblib.load(MODEL_PATH)
        print(f"Model loaded successfully from {MODEL_PATH}")
        return loaded
    except Exception as e:
        print(f"ERROR: Could not load model from {MODEL_PATH}")
        print(f"Error details: {e}")
        return None

@runtime_checkable
class ModelProtocol(Protocol):
    def predict(self, X: Sequence[Sequence[float]]) -> Sequence[int]: ...
    def predict_proba(self, X: Sequence[Sequence[float]]) -> Sequence[Sequence[float]]: ...

model: Optional[ModelProtocol] = _load_model()

@app.post("/predict")
def predict(data: SensorData):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not available")

    features = [[
        data.Air_temperature_K,
        data.Process_temperature_K,
        data.Rotational_speed_rpm,
        data.Torque_Nm,
        data.Tool_wear_min,
        data.Type_L,
        data.Type_M,
        data.Type_H,
    ]]

    pred = int(model.predict(features)[0])

    proba = None
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(features)
        proba = float(probs[0][1])

    return {"prediction": pred, "failure_probability": proba}

@app.get("/")
async def root():
    return {"message": "Predictive Maintenance API is running. Go to /docs to test it."}

@app.get("/api-docs", response_class=HTMLResponse)
async def api_docs():
    """Serve interactive HTML API documentation."""
    # Path to the HTML documentation file
    docs_path = os.path.join(BASE_DIR, "../docs/api-documentation.html")
    
    try:
        with open(docs_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        # Fallback: return minimal HTML if file not found
        return """
        <html>
            <head><title>API Documentation</title></head>
            <body style="font-family: Arial; padding: 20px;">
                <h1>Predictive Maintenance API</h1>
                <p>Documentation file not found, but API is running!</p>
                <p>Visit <a href="/docs">/docs</a> for interactive Swagger UI.</p>
            </body>
        </html>
        """
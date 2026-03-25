from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional, Protocol, Sequence, runtime_checkable, cast

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, ConfigDict, Field, model_validator

app = FastAPI(
    title="Predictive Maintenance API",
    version="1.0.0",
    description="Predict machine failure risk from sensor inputs.",
)

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_MODEL_PATH = BASE_DIR.parent / "models" / "rf_model.joblib"
MODEL_PATH = Path(os.getenv("MODEL_PATH", str(DEFAULT_MODEL_PATH)))


@runtime_checkable
class ModelProtocol(Protocol):
    def predict(self, X: Any) -> Sequence[int]: ...
    def predict_proba(self, X: Any) -> Sequence[Sequence[float]]: ...


class SensorData(BaseModel):
    Air_temperature_K: float
    Process_temperature_K: float
    Rotational_speed_rpm: float
    Torque_Nm: float
    Tool_wear_min: float
    Type_L: int = Field(ge=0, le=1)
    Type_M: int = Field(ge=0, le=1)
    Type_H: int = Field(default=0, ge=0, le=1)

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "Air_temperature_K": 298.1,
                "Process_temperature_K": 308.6,
                "Rotational_speed_rpm": 1551.0,
                "Torque_Nm": 42.8,
                "Tool_wear_min": 0.0,
                "Type_L": 0,
                "Type_M": 1,
                "Type_H": 0
            }
        },
    )

    @model_validator(mode="after")
    def validate_machine_type(self) -> "SensorData":
        if (self.Type_L + self.Type_M + self.Type_H) != 1:
            raise ValueError("Exactly one of Type_L, Type_M, Type_H must be 1")
        return self


model_features: Optional[list[str]] = None

def _load_model() -> Optional[ModelProtocol]:
    global model_features
    if os.getenv("SKIP_MODEL_LOAD", "0") == "1":
        print("SKIP_MODEL_LOAD=1 -> skipping model load")
        return None
    try:
        loaded = joblib.load(MODEL_PATH)

        # Support both:
        # 1) raw sklearn model
        # 2) artifact dict: {"model": model, "features": [...]}
        if isinstance(loaded, dict) and "model" in loaded:
            model_features = list(loaded.get("features", [])) or None
            loaded = loaded["model"]

        print(f"Model loaded successfully from {MODEL_PATH}")
        return loaded  # type: ignore[return-value]
    except Exception as e:
        print(f"ERROR: Could not load model from {MODEL_PATH}")
        print(f"Error details: {e}")
        return None


model: Optional[ModelProtocol] = _load_model()


@app.get("/")
def root() -> dict:
    return {"message": "API is running"}


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "model_loaded": model is not None}


@app.post("/predict")
def predict(data: SensorData) -> dict:
    if model is None:
        raise HTTPException(status_code=503, detail="Model not available")

    values = {
        "Air_temperature_K": data.Air_temperature_K,
        "Process_temperature_K": data.Process_temperature_K,
        "Rotational_speed_rpm": data.Rotational_speed_rpm,
        "Torque_Nm": data.Torque_Nm,
        "Tool_wear_min": data.Tool_wear_min,
        "Type_L": data.Type_L,
        "Type_M": data.Type_M,
        "Type_H": data.Type_H,
    }
    values["Temp_diff_K"] = values["Process_temperature_K"] - values["Air_temperature_K"]
    values["Power_W"] = values["Rotational_speed_rpm"] * values["Torque_Nm"]

    try:
        if model_features:
            cols = model_features
        else:
            feature_names = getattr(model, "feature_names_in_", None)
            if feature_names is not None:
                cols = list(cast(Sequence[str], feature_names))
            else:
                cols = [
                    "Air_temperature_K", "Process_temperature_K", "Rotational_speed_rpm",
                    "Torque_Nm", "Tool_wear_min", "Type_L", "Type_M", "Type_H",
                ]

        X = pd.DataFrame([[values[c] for c in cols]], columns=cols)

        pred = int(model.predict(X)[0])
        failure_probability = None
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(X)
            failure_probability = float(probs[0][1])

        return {
            "prediction": pred,
            "status": "failure" if pred == 1 else "healthy",
            "failure_probability": failure_probability,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failed: {e}")


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
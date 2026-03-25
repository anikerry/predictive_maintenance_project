from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import joblib
import pandas as pd
import os
from typing import Any

app = FastAPI(
    title="Predictive Maintenance API",
    description="Real-time inference API for predicting equipment failure.",
    version="1.0.0"
)

model: Any | None = None
features: list[str] | None = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "../models/rf_model.joblib")

model = None
SKIP_MODEL_LOAD = os.getenv("SKIP_MODEL_LOAD", "0") == "1"

if not SKIP_MODEL_LOAD:
    try:
        artifact = joblib.load(MODEL_PATH)
        model = artifact['model']
        features = artifact['features']
        print(f"Model loaded successfully from {MODEL_PATH}")
    except Exception as e:
        print(f"ERROR: Could not load model from {MODEL_PATH}")
        print(f"Error details: {e}")
        model = None

class SensorData(BaseModel):
    Air_temperature_K: float
    Process_temperature_K: float
    Rotational_speed_rpm: float
    Torque_Nm: float
    Tool_wear_min: float
    Type_L: int
    Type_M: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "Air_temperature_K": 298.1,
                "Process_temperature_K": 308.6,
                "Rotational_speed_rpm": 1551,
                "Torque_Nm": 42.8,
                "Tool_wear_min": 0,
                "Type_L": 0,
                "Type_M": 1
            }
        }

@app.post("/predict")
async def predict_failure(data: SensorData):
    try:
        loaded_model = model
        loaded_features = features

        if loaded_model is None or loaded_features is None:
            raise HTTPException(
                status_code=503,
                detail="Model is not available. Check server logs for load errors."
            )

        input_dict = data.model_dump() if hasattr(data, "model_dump") else data.dict()
        
        input_dict['Temp_diff_K'] = input_dict['Process_temperature_K'] - input_dict['Air_temperature_K']
        input_dict['Power_W'] = input_dict['Rotational_speed_rpm'] * input_dict['Torque_Nm']
        
        input_df = pd.DataFrame([input_dict], columns=loaded_features)
        
        if model is None:
            raise HTTPException(status_code=503, detail="Model not available")
        
        prediction = loaded_model.predict(input_df)[0]
        probability = loaded_model.predict_proba(input_df)[0][1]
        
        return {
            "machine_status": "Failure Predicted" if prediction == 1 else "Healthy",
            "failure_probability": f"{probability * 100:.2f}%",
            "sensor_data_processed": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

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
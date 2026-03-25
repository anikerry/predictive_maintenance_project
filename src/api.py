from fastapi import FastAPI, HTTPException
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

# 1. Initialize variables globally so they always exist
model: Any | None = None
features: list[str] | None = None

# 2. Use an absolute-like path trick to find the model reliably
# This finds the directory api.py is in, then goes up one level to /models
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "../models/rf_model.joblib")

try:
    artifact = joblib.load(MODEL_PATH)
    model = artifact['model']
    features = artifact['features']
    print(f"✅ Model loaded successfully from {MODEL_PATH}")
except Exception as e:
    print(f"❌ CRITICAL ERROR: Could not load model from {MODEL_PATH}")
    print(f"❌ Error details: {e}")

# 3. Define the Input Data Schema using Pydantic
# This ensures the API only accepts the exact data format we expect
class SensorData(BaseModel):
    Air_temperature_K: float
    Process_temperature_K: float
    Rotational_speed_rpm: float
    Torque_Nm: float
    Tool_wear_min: float
    Type_L: int  # 1 if Low quality, 0 otherwise
    Type_M: int  # 1 if Medium quality, 0 otherwise
    
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

# 4. Create the Prediction Endpoint
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

        # Convert incoming JSON payload to a dictionary
        input_dict = data.model_dump() if hasattr(data, "model_dump") else data.dict()
        
        # Calculate our engineered features on the fly!
        input_dict['Temp_diff_K'] = input_dict['Process_temperature_K'] - input_dict['Air_temperature_K']
        input_dict['Power_W'] = input_dict['Rotational_speed_rpm'] * input_dict['Torque_Nm']
        
        # Convert to a DataFrame in the exact column order the model expects
        input_df = pd.DataFrame([input_dict], columns=loaded_features)
        
        # Make the prediction
        prediction = loaded_model.predict(input_df)[0]
        probability = loaded_model.predict_proba(input_df)[0][1] # Probability of failure (Class 1)
        
        # Return the result
        return {
            "machine_status": "Failure Predicted ⚠️" if prediction == 1 else "Healthy ✅",
            "failure_probability": f"{probability * 100:.2f}%",
            "sensor_data_processed": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "Predictive Maintenance API is running. Go to /docs to test it."}
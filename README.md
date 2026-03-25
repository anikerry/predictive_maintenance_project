# Predictive Maintenance ML Pipeline

End-to-end pipeline to predict machine failure from industrial sensor data and serve predictions through a FastAPI microservice.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.103-green)
![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.3-orange)
![Docker](https://img.shields.io/badge/Docker-ready-blue)

## Overview
This project uses the AI4I 2020 dataset from the UCI repository to:
1. Fetch and clean sensor data.
2. Engineer useful features such as `Temp_diff_K` and `Power_W`.
3. Train a `RandomForestClassifier` to detect machine failure.
4. Serve predictions via a FastAPI endpoint.

## Repository Structure
```text
.
├── data/
├── models/
│   └── rf_model.joblib
├── src/
│   ├── api.py
│   ├── etl.py
│   └── train.ipynb
├── Dockerfile
├── requirements.txt
└── README.md
```

## Prerequisites
- Python 3.12
- Conda or virtualenv (optional but recommended)
- Docker (optional, for containerized run)

## Quick Start (Local Python)
1. Clone and enter the project:
```bash
git clone <your-repo-url>
cd predictive_maintenance_project
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure trained model exists:
- This repo already includes `models/rf_model.joblib`.
- If you retrain, export the same artifact format (`model` + `features`) to `models/rf_model.joblib`.

4. Run API:
```bash
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

5. Test API docs:
- Open: `http://localhost:8000/docs`

## Run with Docker
1. Build image:
```bash
docker build -t predictive-maintenance-api .
```

2. Run container:
```bash
docker run -d -p 8000:8000 predictive-maintenance-api
```

3. Verify service:
- Health check: `GET http://localhost:8000/`
- Swagger UI: `http://localhost:8000/docs`

## API Contract
### `POST /predict`
Request body:
```json
{
   "Air_temperature_K": 298.1,
   "Process_temperature_K": 308.6,
   "Rotational_speed_rpm": 1551,
   "Torque_Nm": 42.8,
   "Tool_wear_min": 0,
   "Type_L": 0,
   "Type_M": 1
}
```

Response:
```json
{
   "machine_status": "Healthy",
   "failure_probability": "0.00%",
   "sensor_data_processed": true
}
```

## Reproducibility Notes
- **Raw dataset** is included locally at `data/ai4i2020_raw.csv` for offline use and reproducibility.
- ETL script can be re-run to regenerate both raw and processed datasets:
  ```bash
  python src/etl.py
  ```
- Processed dataset is saved to `data/processed_machine_data.csv` and used by the training notebook.
- The API expects a serialized artifact at `models/rf_model.joblib` containing:
   - `model`: trained estimator
   - `features`: ordered feature list used during training

## Next Improvements
- Add automated tests for `/predict` and model artifact validation.
- Export notebook training workflow into a standalone Python training script for CI use.
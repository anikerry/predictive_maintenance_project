# Predictive Maintenance ML Pipeline

Production-ready machine learning system for predictive maintenance.  
End-to-end workflow for detecting equipment failure from industrial sensor data, exposed via a containerized FastAPI service.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.103-green)
![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.3-orange)
![Docker](https://img.shields.io/badge/Docker-ready-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Overview

This repository demonstrates a practical ML engineering pipeline:

- **Data Processing**: ETL for industrial sensor telemetry
- **Feature Engineering**: Domain-informed transformations
- **Model Training**: Random Forest classifier for imbalanced failure detection
- **API Deployment**: FastAPI service with interactive docs
- **CI/CD**: GitHub Actions test/build workflow
- **Containerization**: Dockerized runtime

---

## Repository Structure

```text
.
├── .github/
│   └── workflows/
│       └── ci.yml
├── data/
│   ├── ai4i2020_raw.csv
│   └── processed_machine_data.csv
├── docs/
│   └── api-documentation.html
├── figures/
│   ├── class_distribution_imbalance.png
│   ├── confusion_matrix.png
│   ├── engineered_features_distribution.png
│   ├── feature_correlation_matrix.png
│   ├── feature_importances.png
│   ├── raw_sensor_features_distribution.png
│   ├── roc_and_precision_recall_curves.png
│   └── train_vs_test_performance.png
├── models/
│   └── rf_model.joblib
├── src/
│   ├── __init__.py
│   ├── api.py
│   ├── etl.py
│   └── train.ipynb
├── tests/
│   ├── conftest.py
│   └── test_api.py
├── .gitignore
├── Dockerfile
├── environment.yml
├── pytest.ini
├── requirements.txt
└── README.md
```

> Keep exactly one model artifact at `models/rf_model.joblib` (avoid duplicates under `src/models/`).

---

## Model Performance

| Metric | Value |
|--------|-------|
| Accuracy | 97.5% |
| Precision | 91% |
| Recall | 67% |
| F1-Score | 0.778 |
| ROC-AUC | 0.93 |
| Inference Latency | ~0.15 ms/prediction |

---

## Figures

Notebook visualizations are exported automatically to `figures/` when plot cells are run.

- `feature_correlation_matrix.png`
- `engineered_features_distribution.png`
- `raw_sensor_features_distribution.png`
- `class_distribution_imbalance.png`
- `confusion_matrix.png`
- `train_vs_test_performance.png`
- `roc_and_precision_recall_curves.png`
- `feature_importances.png`

---

## Prerequisites

- Python 3.12+
- pip

Optional:
- Conda (recommended for environment isolation)
- Docker

---

## Quick Start

### 1) Local (PowerShell)

```powershell
git clone https://github.com/anikerry/predictive_maintenance_project.git
cd predictive_maintenance_project

python -m pip install --upgrade pip
pip install -r requirements.txt

pytest tests/ -q
python -m uvicorn src.api:app --reload --app-dir .
```

- Swagger UI: `http://127.0.0.1:8000/docs`
- Health endpoint: `http://127.0.0.1:8000/health`

### 2) Conda

```powershell
conda env create -f environment.yml
conda activate pred_ml
pip install -r requirements.txt
pytest tests/ -q
python -m uvicorn src.api:app --host 0.0.0.0 --port 8000 --app-dir .
```

### 3) Docker

```powershell
docker build -t predictive-maintenance-api:latest .
docker run -d --name maintenance-api -p 8000:8000 predictive-maintenance-api:latest
```

### Run API (PowerShell)
```powershell
cd "D:\GenAI Projects\predictive_maintenance_project"
python -m uvicorn src.api:app --reload --app-dir .
```

---

## API Endpoints

### `GET /`
Basic service check.

### `GET /health`
Returns service status and whether the model is loaded.

### `POST /predict`
Predict machine state from sensor values.

#### Example request

```json
{
  "Air_temperature_K": 298.1,
  "Process_temperature_K": 308.6,
  "Rotational_speed_rpm": 1551.0,
  "Torque_Nm": 42.8,
  "Tool_wear_min": 0.0,
  "Type_L": 0,
  "Type_M": 1,
  "Type_H": 0
}
```

#### Example response (200)

```json
{
  "prediction": 0,
  "status": "healthy",
  "failure_probability": 0.0
}
```

#### Error responses

- `422` validation error (invalid request body)
- `503` model unavailable
- `500` inference failure

---

## Testing Strategy

- Tests use `httpx.AsyncClient` + `ASGITransport`
- AnyIO backend pinned to `asyncio` in tests
- Model is mocked in unit tests
- CI sets `SKIP_MODEL_LOAD=1` to avoid artifact/version coupling during test runs

Run tests:

```powershell
pytest tests/ -q
```

---

## CI Pipeline (GitHub Actions)

Workflow (`.github/workflows/ci.yml`) performs:

1. Dependency installation
2. API unit tests
3. Docker build validation

Key stability pins:

- `pytest>=8,<10`
- `httpx<0.28`

---

## Data & Reproducibility

- Source dataset: AI4I 2020 (UCI)
- Raw and processed data are versioned in `data/`
- Deterministic split/training strategy (fixed random state)
- Serialized model at `models/rf_model.joblib`

To regenerate processed data:

```powershell
python src/etl.py
```

Retraining is documented in `src/train.ipynb`.

---

## Technical Decisions

### Why Random Forest
- Strong baseline for tabular sensor data
- Handles nonlinear interactions
- Works with class-weight balancing
- Fast inference for API workloads

### Why FastAPI
- High performance
- Automatic OpenAPI docs
- Strong validation via Pydantic

### Why Docker
- Reproducible environments
- Deployment portability
- CI/CD-friendly runtime packaging

---

## Roadmap

- Expand unit/integration test coverage
- Add model artifact/version validation tests
- Add monitoring/metrics for inference and drift
- Add model versioning strategy and staged rollout

---

## Contributing

1. Fork repository
2. Create feature branch
3. Commit with clear messages
4. Open Pull Request

---

## License

MIT License.
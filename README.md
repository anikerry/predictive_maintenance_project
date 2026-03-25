# Predictive Maintenance ML Pipeline

**Production-ready machine learning system for predictive maintenance** — End-to-end pipeline to detect equipment failure from industrial sensor data with sub-millisecond inference latency through a containerized FastAPI microservice.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.103-green)
![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.3-orange)
![Docker](https://img.shields.io/badge/Docker-ready-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## Overview

This project demonstrates a complete ML engineering pipeline with:
- **Data Processing**: ETL pipeline for 10,000+ sensor readings from industrial machinery
- **Feature Engineering**: Domain-driven feature creation (temperature differential, power calculations)
- **Model Training**: Balanced Random Forest classifier handling severe class imbalance (97:3 healthy-to-failure ratio)
- **API Deployment**: Production-grade REST API with Swagger documentation
- **Containerization**: Docker support for seamless deployment

The system achieves **91% precision** on held-out test data while maintaining sub-millisecond prediction latency.

## Repository Structure
```text
.
├── data/
│   ├── ai4i2020_raw.csv              # Raw dataset (10,000 samples)
│   └── processed_machine_data.csv    # Cleaned & engineered features
├── src/
│   ├── api.py                        # FastAPI server with /predict endpoint
│   ├── etl.py                        # Data extraction, transformation, loading
│   └── train.ipynb                   # Model training & exploratory analysis
├── models/
│   └── rf_model.joblib               # Serialized Random Forest classifier
├── environment.yml                    # Conda environment specification
├── requirements.txt                   # pip dependencies
├── Dockerfile                         # Container configuration
└── README.md
```

## Technical Highlights

### Machine Learning
- **Algorithm**: Random Forest (100 estimators) with balanced class weights
- **Data Handling**: Scikit-learn preprocessing with proper train/test splitting (80/20)
- **Feature Engineering**: Domain-informed features (temperature differential, power calculations)
- **Class Imbalance Solution**: Weighted loss function to handle 32:1 imbalance ratio

### Data Pipeline
- **ETL Architecture**: Modular pipeline (extract → transform → load)
- **Data Validation**: Column normalization, data type handling, missing value checks
- **Reproducibility**: Both raw and processed datasets versioned for audit trail
- **Local First**: Offline capability with cached datasets

### API & Deployment
- **Framework**: FastAPI with async request handling
- **Documentation**: Auto-generated Swagger UI at `/docs`
- **Containerization**: Multi-layer Docker image optimized for size
- **Error Handling**: Comprehensive exception handling with HTTP status codes
- **Model Loading**: Safe artifact deserialization with fallback handlers

## Model Performance

| Metric | Value |
|--------|-------|
| **Accuracy** | 97.5% |
| **Precision** | 91% |
| **Recall** | 67% |
| **F1-Score** | 0.778 |
| **ROC-AUC** | 0.93 |
| **Inference Latency** | 0.15 ms/prediction |
| **Test Dataset Size** | 2,000 samples |

**Precision-Recall Trade-off**: The model prioritizes precision (91%) to minimize false alarms in production while maintaining reasonable recall (67%) for failure detection.


## Prerequisites

### Required
- **Python 3.12** or higher
- **pip** (Python package manager)

### Optional
- **Conda/Mamba** — For isolated environment management using `environment.yml`
- **Docker & Docker Compose** — For containerized deployment
- **git** — For version control and cloning the repository

## Installation & Quick Start

### Option 1: Local Python (Recommended for Development)

1. **Clone the repository:**
```bash
git clone https://github.com/anikerry/predictive_maintenance_project.git
cd predictive_maintenance_project
```

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

3. **Verify trained model exists:**
The repository includes a pre-trained Random Forest model at `models/rf_model.joblib`. If you wish to retrain:
```bash
python src/etl.py  # Generate processed dataset
# Then run training cells in src/train.ipynb
```

4. **Start the API server:**
```bash
uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload
```

5. **Test the API:**
- Interactive API Docs: `http://localhost:8000/docs`
- Health Check: `curl http://localhost:8000/`

### Option 2: Using Conda Environment

For full reproducibility with locked dependency versions:

```bash
conda env create -f environment.yml
conda activate pred_ml
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

### Option 3: Docker (Production)

1. **Build the container image:**
```bash
docker build -t predictive-maintenance-api:latest .
```

2. **Run the containerized API:**
```bash
docker run -d \
  --name maintenance-api \
  -p 8000:8000 \
  predictive-maintenance-api:latest
```

3. **Verify the service:**
```bash
curl http://localhost:8000/
# Response: {"message": "Predictive Maintenance API is running. Go to /docs to test it."}
```

4. **Stop the container:**
```bash
docker stop maintenance-api
docker rm maintenance-api
```

## API Endpoints

### `POST /predict` — Machine Failure Prediction

**Request:**
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

**Response (Success - 200):**
```json
{
  "machine_status": "Healthy",
  "failure_probability": "0.00%",
  "sensor_data_processed": true
}
```

**Response (Failure Detected - 200):**
```json
{
  "machine_status": "Failure Predicted",
  "failure_probability": "87.34%",
  "sensor_data_processed": true
}
```

**Error Response (Bad Request - 400):**
```json
{
  "detail": "Missing required field: 'Air_temperature_K'"
}
```

### `GET /` — Health Check

Returns service status as JSON.

### `GET /docs` — API Documentation

Interactive Swagger UI with request/response examples.

## Request Parameters

The `/predict` endpoint expects these sensor reading fields:

| Parameter | Type | Unit | Range | Description |
|-----------|------|------|-------|-------------|
| `Air_temperature_K` | float | Kelvin | 295-305 | Ambient environment temperature |
| `Process_temperature_K` | float | Kelvin | 305-315 | Machine operating temperature |
| `Rotational_speed_rpm` | float | RPM | 1168-2886 | Spindle rotation speed |
| `Torque_Nm` | float | N·m | 3.8-76.6 | Applied torque |
| `Tool_wear_min` | float | Minutes | 0-258 | Cumulative tool wear |
| `Type_L` | int | Binary | 0 or 1 | Product type L (one-hot) |
| `Type_M` | int | Binary | 0 or 1 | Product type M (one-hot) |

Note: `Type_H` is implicitly 0 when both `Type_L` and `Type_M` are 0.

## Data & Reproducibility

### Dataset
- **Source**: UC Irvine Machine Learning Repository (AI4I 2020 dataset)
- **Samples**: 10,000 industrial machine records
- **Features**: 5 sensor readings + 2 computed features + 3 machine type indicators
- **Target**: Binary classification (Machine_failure: 0=Healthy, 1=Failed)
- **Class Distribution**: 97% Healthy, 3% Failure (severe imbalance)

### Reproducibility
The project is designed for full reproducibility:

1. **Versioned Dependencies**: Both `requirements.txt` and `environment.yml` lock dependency versions
2. **Cached Data**: Raw dataset included at `data/ai4i2020_raw.csv` for offline use
3. **Deterministic Splits**: Fixed `random_state=42` in train/test split
4. **Model Serialization**: Complete artifact saved with model + feature list

**To regenerate the dataset and retrain:**
```bash
# Fetch and process data
python src/etl.py

# Run training in Jupyter (train.ipynb) or export to standalone script
# The new model will be saved to models/rf_model.joblib
```

## Project Structure Details

### `src/etl.py`
Modular ETL pipeline with functions for:
- `fetch_and_load_data()` — Download from UCI, save locally
- `clean_and_transform()` — Data cleaning, one-hot encoding, feature engineering
- `save_data()` — Persist processed dataset to CSV
- `load_data_local()` — Load from cached file for offline use

### `src/api.py`
FastAPI application featuring:
- Pydantic models for request/response validation
- Async request handling for high concurrency
- Graceful error handling with informative messages
- CORS-ready architecture for client integration
- OpenAPI/Swagger documentation auto-generation

### `src/train.ipynb`
Jupyter notebook documenting:
- Exploratory data analysis (EDA) with visualizations
- Feature correlation analysis
- Class imbalance quantification
- Model training and hyperparameter tuning
- Comprehensive performance metrics (Accuracy, Precision, Recall, ROC-AUC)
- Feature importance visualization

## Future Enhancements

- [ ] **Unit Tests**: Pytest suite for ETL pipeline and API endpoints
- [ ] **Model Tests**: Validation of model artifact integrity and feature compatibility
- [ ] **Continuous Training**: Scheduled retraining pipeline on new data
- [ ] **Advanced Models**: Experiment with Gradient Boosting (XGBoost, LightGBM) and ensemble methods
- [ ] **API Versioning**: Support multiple model versions with fallback strategy
- [ ] **Monitoring**: Prometheus/Grafana metrics for inference latency, prediction distribution
- [ ] **Database Logger**: Store predictions with feedback for model drift detection
- [ ] **Kubernetes Deployment**: Helm charts for cloud-native scaling
- [ ] **Web Dashboard**: Real-time visualization of predictions and system health
- [ ] **Feature Store**: Centralized feature management for production ML systems

## Technical Decisions

### Why Random Forest?
- Effective on tabular sensor data without extensive normalization
- Built-in feature importance for interpretability
- Handles class imbalance well with `class_weight='balanced'`
- Fast inference for real-time predictions (<1ms)
- Minimal hyperparameter tuning required for solid baseline

### Why FastAPI?
- High performance with async/await support
- Automatic OpenAPI documentation generation
- Built-in data validation with Pydantic
- Modern Python 3.6+ type hints
- Minimal boilerplate code

### Why Docker?
- Environment reproducibility across dev/test/prod
- Simplified dependency management
- Easy horizontal scaling in orchestration platforms
- Industry standard for containerized ML services

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit changes with clear messages
4. Push to branch and create a Pull Request

## License

This project is licensed under the MIT License — see LICENSE file for details.

---

**Questions?** Open an issue on GitHub or refer to the API documentation at `/docs` when the service is running.
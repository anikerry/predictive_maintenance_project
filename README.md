# 🏭 End-to-End Predictive Maintenance ML Pipeline

Predicting industrial equipment failure from streaming sensor data to eliminate unplanned downtime.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.103-green)
![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.3-orange)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)

## 📌 Project Overview
Unplanned downtime costs the manufacturing industry billions annually. This project provides an automated, end-to-end Machine Learning pipeline that ingests IoT sensor data (rotational speed, torque, tool wear, temperature), processes it, and predicts impending machine failures in real-time.

By containerizing the prediction engine as a microservice using Docker, this architecture can be seamlessly deployed to edge devices on the factory floor or integrated into cloud dashboards used by reliability engineering teams.

## 🎯 Business Impact & Metrics
* **Improved prediction accuracy by 12%** by engineering domain-specific features (e.g., calculating structural `Power_W` from rotational speed and torque) prior to model training.
* **Pipeline automated:** Built a fully automated ETL pipeline that extracts the official AI4I 2020 dataset from the UCI Repository, cleans it, and prevents data leakage.
* **Sub-millisecond Latency:** Achieved an average inference time of **0.0686 ms** per prediction by optimizing model serialization (`joblib`) and utilizing an asynchronous FastAPI serving layer.
* **Precision Targeting:** Handled severe class imbalance (97% healthy / 3% failure) using balanced class weights, achieving **91% Precision** to minimize costly false alarms on the factory floor.

## 💻 Tech Stack
* **Core:** Python 3.12
* **Data Engineering:** `pandas`, `numpy`
* **Machine Learning:** `scikit-learn` (Random Forest Classifier)
* **Model Serving:** FastAPI, `uvicorn`, Pydantic
* **DevOps & Deployment:** Docker

## 🏗️ Architecture
1. **ETL (`jupyter notebook`):** Raw sensor data is ingested, cleaned, and engineered. Identifier columns are dropped to prevent target leakage.
2. **Model Training:** A Random Forest classifier is trained to detect complex, non-linear failure patterns.
3. **Inference API (`src/api.py`):** A FastAPI service loads the serialized model on startup and exposes a `/predict` endpoint that computes engineered features on the fly.
4. **Containerization (`Dockerfile`):** The entire application is packaged into an isolated environment for reliable deployment.

## 🚀 How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/predictive-maintenance-pipeline.git](https://github.com/yourusername/predictive-maintenance-pipeline.git)
   cd predictive-maintenance-pipeline
Build the Docker container:

Bash
docker build -t predictive-maintenance-api .
Run the container:

Bash
docker run -d -p 8000:8000 predictive-maintenance-api
Test the API:
Navigate to http://localhost:8000/docs to view the interactive Swagger UI. You can send a test POST request with dummy sensor data to see real-time predictions.


---
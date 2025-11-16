# SQL Injection Detection System - Backend

FastAPI-based backend for SQL injection detection using machine learning and explainable AI.

## Features

- 5 ML models (Random Forest, XGBoost, Logistic Regression, SVM, Naive Bayes)
- Model ensembling with voting
- Explainable AI (LIME, SHAP, Feature Importance)
- Gemini LLM for natural language explanations
- Active learning pipeline
- Attack payload generator
- Comprehensive logging
- REST API with authentication

## Setup

### 1. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```
### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your actual values
```
Required environment variables:

- `DATABASE_URL`: MySQL connection string
- `DB_PASSWORD`: MySQL password
- `GEMINI_API_KEY`: Your Gemini API key
- `ADMIN_API_KEY`: Admin API key (set your own)
- `DEMO_API_KEY`: Demo API key (set your own)

### 3. Setup MySQL Database

```bash
# Login to MySQL
mysql -u root -p

# Create database
CREATE DATABASE sqli_detection;
```
### 4. Initialize Database

```bash
python init_database.py
```
This creates all tables and seeds initial data (API keys, attack patterns, config).

### 5. Download Dataset
Download from: https://www.kaggle.com/datasets/sajid576/sql-injection-dataset
Extract and place CSV file at: `../data/raw/sql_injection_dataset.csv`

### 6. Train Models

```bash
python train_models.py
```
This trains all 5 models and saves them to the database. Takes 5-10 minutes.

### 7. Start Server

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Or:

```bash
python app/main.py
```
## API Documentation
Once the server is running, visit:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints
### Detection
- `POST /api/v1/detect/detect` - Detect SQL injection
- `POST /api/v1/detect/batch-detect` - Batch detection

### Demo
- `POST /api/v1/demo/protected` - Protected demo
- `POST /api/v1/demo/vulnerable` - Vulnerable demo
- `POST /api/v1/demo/compare` - Side-by-side comparison

### Analytics
- `GET /api/v1/analytics/stats` - Overall statistics
- `GET /api/v1/analytics/timeline` - Attack timeline
- `GET /api/v1/analytics/dashboard` - Complete dashboard data

### Logs
- `GET /api/v1/logs` - Get logs with filters
- `GET /api/v1/logs/{id}` - Get log details
- `POST /api/v1/logs/feedback` - Submit feedback
- `GET /api/v1/logs/export/csv` - Export to CSV
- `GET /api/v1/logs/export/json` - Export to JSON

### Models
- `GET /api/v1/models` - List all models
- `POST /api/v1/models/switch` - Switch active model
- `POST /api/v1/models/activate/{id}` - Activate model version
- `POST /api/v1/models/train/{name}` - Train specific model
- `POST /api/v1/models/compare` - Compare two models

### Admin
- `GET /api/v1/admin/system-info` - System information
- `GET /api/v1/admin/api-keys` - List API keys
- `POST /api/v1/admin/api-keys` - Create API key
- `POST /api/v1/admin/retrain` - Trigger active learning

### Stress Test
- `POST /api/v1/stress-test/generate-payloads` - Generate test payloads
- `POST /api/v1/stress-test/run` - Run stress test
- `GET /api/v1/stress-test/status/{id}` - Get test status

## Authentication
All endpoints require `X-API-Key` header:

```bash
curl -H "X-API-Key: demo-key-change-this" http://localhost:8000/api/v1/analytics/stats
```
## Project Structure
```text
backend/
├── app/
│   ├── api/           # API endpoints
│   ├── models/        # Database models
│   ├── schemas/       # Pydantic schemas
│   ├── ml/           # ML components
│   ├── xai/          # XAI explainers
│   ├── services/     # Business logic
│   └── utils/        # Utilities
├── init_database.py  # DB initialization
├── train_models.py   # Model training
└── requirements.txt
```
## Testing
```bash
# Test detection endpoint
curl -X POST http://localhost:8000/api/v1/detect/detect \
  -H "Content-Type: application/json" \
  -H "X-API-Key: demo-key-change-this" \
  -d '{"query": "SELECT * FROM users WHERE id = 1"}'
```
## Troubleshooting
### Database Connection Error
- Ensure MySQL is running
- Check `DATABASE_URL` in `.env`
- Verify database exists: `SHOW DATABASES;`

### Models Not Found
- Run `python train_models.py`
- Check `models` directory exists

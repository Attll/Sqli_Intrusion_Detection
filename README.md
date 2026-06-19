# SQL Injection Intrusion Detection System (SQLi-IDS)

An end-to-end SQL Injection Detection System that leverages Machine Learning (ML) and Explainable AI (XAI). This project provides a full-stack solution featuring a high-performance FastAPI backend, a modern React frontend dashboard, and active learning capabilities.

## 🌟 Key Features

### Backend
* **Multi-Model Machine Learning Ensemble**: Utilizes 5 distinct models (Random Forest, XGBoost, Logistic Regression, SVM, Naive Bayes) with ensemble voting for high accuracy.
* **Explainable AI (XAI)**: Integrates LIME and SHAP to provide visibility into model decisions and highlight malicious query segments.
* **LLM Integration**: Uses Google Generative AI (Gemini) to generate natural language explanations for detected threats.
* **Active Learning Pipeline**: Allows continuous model improvement by retraining on newly verified data.
* **Robust API**: RESTful API built with FastAPI with authentication, comprehensive logging, and endpoints for detection, analytics, models management, and demos.

### Frontend
* **Modern SPA**: Built with React 18 and Vite for fast loading and seamless navigation.
* **Interactive Dashboard**: Real-time analytics, statistics, and attack timelines visualized using Recharts.
* **Explainable Results**: Visually displays XAI outputs and LLM explanations for detected injections.
* **State Management**: Uses Zustand and React Query for efficient data fetching and global state management.
* **Responsive UI**: Styled with Tailwind CSS and Lucide React icons.

---

## 🏗️ Architecture & Components

The application follows a standard client-server architecture.

1. **Client (Frontend)**: A React-based web dashboard where administrators can view analytics, test payloads, monitor logs, and manage ML models.
2. **Server (Backend)**: A FastAPI application that serves the frontend's API requests, handles database operations, and runs the machine learning pipelines.
3. **Database (MySQL)**: Stores application data including API keys, detection logs, system configurations, and serialized machine learning models.
4. **Machine Learning Pipeline**: Processes incoming SQL queries, extracts features, runs them through the ensemble of trained models, and produces a classification (Safe vs. SQLi).
5. **XAI & LLM Services**: Post-processes predictions to generate LIME/SHAP explanations and fetches natural language summaries from the Gemini API.

---

## 📁 Repository Structure

```text
Sqli_Intrusion_Detection/
└── sql-injection-detection/
    ├── backend/                 # Python FastAPI Backend
    │   ├── app/
    │   │   ├── api/             # API endpoints (detect, demo, analytics, logs, models, admin)
    │   │   ├── ml/              # Machine learning models, pipelines, and feature extractors
    │   │   ├── models/          # SQLAlchemy database models
    │   │   ├── schemas/         # Pydantic validation schemas
    │   │   ├── services/        # Core business logic (detection logic, model training)
    │   │   ├── utils/           # Helper utilities (logging, authentication)
    │   │   └── xai/             # Explainable AI (LIME, SHAP) integration
    │   ├── init_database.py     # Script to initialize DB and seed initial data
    │   ├── train_models.py      # Script to train all ML models and save them to the DB
    │   └── requirements.txt     # Python dependencies
    ├── frontend/                # React Vite Frontend
    │   ├── src/
    │   │   ├── components/      # Reusable UI components
    │   │   ├── hooks/           # Custom React hooks
    │   │   ├── pages/           # Page components (Dashboard, Logs, Models, Settings)
    │   │   ├── services/        # API integration (Axios calls)
    │   │   ├── store/           # Zustand state management
    │   │   └── utils/           # Utility functions
    │   ├── package.json         # Node.js dependencies and scripts
    │   ├── tailwind.config.js   # Tailwind CSS configuration
    │   └── vite.config.js       # Vite configuration
    └── data/                    # Datasets
        └── raw/
            └── sql_injection_dataset.csv  # The Kaggle dataset used for training
```

---

## ⚙️ Functioning

### 1. The Detection Flow
- The user (or an external system) submits an SQL query payload to the `POST /api/v1/detect/detect` endpoint.
- The backend parses the query and extracts key features (e.g., presence of SQL keywords, punctuation, specific patterns).
- The query is passed to the **Active ML Model** (or the Ensemble). The ensemble runs the query through its sub-models and aggregates the predictions (e.g., majority voting) to determine if it is an injection.
- If flagged or requested, the query is passed to the **XAI Modules** (LIME/SHAP) which determine the most significant features contributing to the prediction.
- The payload and prediction context are sent to the **Gemini LLM**, which generates a plain-English explanation of why the query is safe or dangerous.
- The full result, including prediction, probabilities, XAI data, and LLM explanation, is returned to the client and logged in the database.

### 2. Active Learning
- Verified logs and feedback can be used to retrain models. The `/api/v1/admin/retrain` endpoint triggers an active learning pipeline that updates the models based on recent attack patterns.

### 3. Monitoring & Analytics
- Every API request for detection is logged.
- The frontend dashboard fetches aggregation stats (e.g., total detections, attack types, timeline) from the `/api/v1/analytics/stats` and `timeline` endpoints, displaying them visually.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+ & npm
- MySQL Server

### 1. Database Setup
Ensure MySQL is running, then create the database:
```sql
CREATE DATABASE sqli_detection;
```

### 2. Backend Setup
Navigate to the backend directory and install dependencies:
```bash
cd sql-injection-detection/backend
pip install -r requirements.txt
```

Configure your environment variables:
```bash
cp .env.example .env
# Edit .env with your actual values:
# DATABASE_URL=******localhost:3306/sqli_detection
# GEMINI_API_KEY=your_gemini_api_key
```

Initialize the database and train the initial models:
*(Requires placing the dataset at `data/raw/sql_injection_dataset.csv`)*
```bash
python init_database.py
python train_models.py
```

Start the FastAPI server:
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
API Documentation available at: `http://localhost:8000/docs`

### 3. Frontend Setup
Navigate to the frontend directory and install dependencies:
```bash
cd sql-injection-detection/frontend
npm install
```

Start the React development server:
```bash
npm run dev
```
Access the application at `http://localhost:5173`.

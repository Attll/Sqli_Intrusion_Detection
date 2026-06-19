# SQL Injection Intrusion Detection System (SQLi-IDS)

An end-to-end SQL Injection Detection System that leverages Machine Learning (ML) and Explainable AI (XAI). This project provides a full-stack solution featuring a high-performance FastAPI backend, a modern React frontend dashboard, and active learning capabilities.

---

## 🌟 Key Features

### Machine Learning & Backend (Deep Dive)
* **Multi-Model Machine Learning Ensemble**: Utilizes 5 distinct models simultaneously to classify queries. The models include:
  * **Random Forest**: Tree-based bagging method robust against overfitting.
  * **XGBoost**: Gradient boosted decision trees optimized for performance and capturing complex patterns.
  * **Logistic Regression**: Linear model to capture fundamental token relationships.
  * **Support Vector Machine (SVM)**: Effective in high-dimensional spaces to find the optimal decision boundary.
  * **Multinomial Naive Bayes**: Probabilistic classifier ideal for text features.
* **Ensemble Voting Mechanism**: Uses dynamic ensemble aggregation supporting both "Hard Voting" (majority rule) and "Soft Voting" (averaging prediction probabilities) to achieve high accuracy and robustness.
* **Advanced Feature Extraction**: Custom `SQLInjectionPreprocessor` combining:
  * **TF-IDF Vectorization**: Character-level n-grams (1-3) to capture underlying string patterns.
  * **Structural Features**: Query length, word count, SQL keyword frequencies (SELECT, UNION, DROP, etc.), special character counts, and ratio metrics.
  * **Evasion & Suspicious Patterns Detection**: Flags common evasion techniques like hex usage (`0x`), tautologies (`1=1`), waitfor/sleep commands, and suspicious SQL encoding.
* **Class Imbalance Handling**: Integrated **SMOTE** (Synthetic Minority Over-sampling Technique) to ensure the models aren't biased toward benign traffic when malicious samples are rare.
* **Explainable AI (XAI)**:
  * **SHAP**: Utilizes `TreeExplainer` for tree-based models and `KernelExplainer` for others to calculate Shapley values, highlighting the marginal contribution of each feature to the overall prediction.
  * **LIME**: Uses `LimeTabularExplainer` to fit local surrogate models, highlighting exactly which parts of the query increased or decreased the malicious score.
* **LLM Integration**: Uses Google Generative AI (Gemini) to generate natural language explanations in three dynamic styles (simple, technical, detailed) for non-technical users and analysts alike.
* **Active Learning**: Exposes endpoints (`/api/v1/admin/retrain`) to trigger automated hyperparameter tuning and model retraining workflows based on newly collected and verified logs.

### Frontend
* **Modern SPA**: Built with React 18 and Vite for fast loading and seamless navigation.
* **Interactive Dashboard**: Real-time analytics, statistics, and attack timelines visualized using Recharts.
* **Explainable Results**: Visually displays XAI feature importance charts (red for increasing risk, green for decreasing risk) alongside the generated Gemini LLM explanations.
* **State Management**: Uses Zustand and React Query for efficient data fetching and global state management.
* **Responsive UI**: Styled with Tailwind CSS and Lucide React icons.

---

## 🏗️ Architecture & Components

1. **Client (Frontend)**: A React-based web dashboard where administrators can view analytics, test payloads, monitor logs, and manage ML models.
2. **Server (Backend)**: A FastAPI application managing the REST API, connecting to the database, executing the `ModelTrainer`, running the `SQLInjectionPredictor`, and interfacing with the `GeminiExplainer`.
3. **Database (MySQL)**: Stores API keys, detection logs, system configurations, and serialized machine learning models via joblib.
4. **Machine Learning Pipeline**: Processes incoming SQL queries, extracts non-negative structural and TF-IDF features, scales them using StandardScaler/MinMaxScaler, passes them to the Ensemble Predictor, and returns the classification confidence.
5. **XAI & LLM Services**: Post-processes prediction outputs to generate LIME/SHAP explanations and fetches natural language summaries from the Gemini API using context-aware prompt templates.

---

## 📁 Repository Structure

```text
Sqli_Intrusion_Detection/
└── sql-injection-detection/
    ├── backend/                 # Python FastAPI Backend
    │   ├── app/
    │   │   ├── api/             # API endpoints (detect, demo, analytics, logs, models, admin)
    │   │   ├── ml/              # Machine learning models
    │   │   │   ├── ensemble.py  # EnsemblePredictor logic (Hard/Soft voting)
    │   │   │   ├── predictor.py # SQLInjectionPredictor for individual models
    │   │   │   ├── preprocessor.py # SQLInjectionPreprocessor (TF-IDF & Structural Features)
    │   │   │   └── trainer.py   # ModelTrainer (GridSearchCV, SMOTE, Hyperparameter tuning)
    │   │   ├── models/          # SQLAlchemy database models
    │   │   ├── schemas/         # Pydantic validation schemas
    │   │   ├── services/        # Core business logic (detection workflow)
    │   │   ├── utils/           # Helper utilities
    │   │   └── xai/             # Explainable AI
    │   │       ├── gemini_service.py # LLM Prompts and Integration
    │   │       ├── lime_explainer.py
    │   │       └── shap_explainer.py
    │   ├── init_database.py     # Script to initialize DB and seed initial data
    │   ├── train_models.py      # Script to train all ML models and save them to the DB
    │   └── requirements.txt     # Python dependencies
    ├── frontend/                # React Vite Frontend
    │   ├── src/                 # React components, hooks, services, and Zustand store
    │   ├── package.json         
    │   └── tailwind.config.js   
    └── data/                    # Datasets (place sql_injection_dataset.csv in data/raw/)
```

---

## ⚙️ Functioning: The Detection & ML Flow

1. **Payload Ingestion**: The user submits a SQL query payload to the `POST /api/v1/detect/detect` endpoint.
2. **Preprocessing**: The `SQLInjectionPreprocessor` extracts a large matrix of structural features (tautologies, keywords, lengths) and TF-IDF character-level n-grams, applying min-max scaling and standard scaling.
3. **Prediction**: The `EnsemblePredictor` ingests the features and passes them to the 5 baseline models. It calculates an average probability (Soft Voting) or majority vote (Hard Voting) to determine if the query is an injection.
4. **Explainability Extraction**: If flagged, the `SHAPExplainer` and `LIMEExplainer` generate feature importance vectors to quantify why the ensemble triggered an alert (e.g., highlighting that the `union_count` and `has_tautology` features spiked).
5. **Generative LLM Summary**: The extracted LIME/SHAP features and prediction confidence are fed into the `GeminiExplainer` to produce a plain-English explanation.
6. **Persistence**: The full result and context are logged into MySQL, enabling future active learning and dashboard analytics.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+ & npm
- MySQL Server

### 1. Database Setup
```sql
CREATE DATABASE sqli_detection;
```

### 2. Backend Setup
Navigate to the backend directory and install dependencies:
```bash
cd sql-injection-detection/backend
pip install -r requirements.txt
```

Configure your environment variables (`.env`):
```env
DATABASE_URL=******localhost:3306/sqli_detection
GEMINI_API_KEY=your_gemini_api_key
```

Initialize the database and train the initial models *(Requires placing the dataset at `data/raw/sql_injection_dataset.csv`)*:
```bash
python init_database.py
python train_models.py
```

Start the FastAPI server:
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup
Navigate to the frontend directory, install dependencies, and run:
```bash
cd sql-injection-detection/frontend
npm install
npm run dev
```
Access the dashboard at `http://localhost:5173`.

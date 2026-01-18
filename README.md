# Cashi Credit Scoring API

A machine learning-powered credit scoring system that predicts loan default probability and generates credit scores. Built with FastAPI, Logistic Regression with Weight of Evidence (WoE) transformation, and business rules validation.

## Table of Contents

- [Overview](#overview)
- [Quick Start with Docker](#quick-start-with-docker)
- [Model Development](#model-development)
- [Features Used for Prediction](#features-used-for-prediction)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Running the API](#running-the-api)
- [Using the Frontend](#using-the-frontend)
- [Docker Deployment](#docker-deployment)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Business Rules](#business-rules)
- [License](#license)

---

## Overview

Cashi Credit Scoring API provides:

- **Credit Score Calculation**: Scores range from 356-671 based on applicant financial profile
- **Default Probability**: Probability of loan default (0-100%)
- **Risk Classification**: Low / Medium / High risk levels
- **Human-Readable Explanations**: Clear reasons for the score
- **Business Rules Validation**: Hard rejections and risk overrides for edge cases

---

## Quick Start with Docker

The fastest way to get up and running:

```bash
# Clone the repository
docker pull python:3.11-slim
git clone https://github.com/aziemma/cashi_project
cd cashi_project

# Build and start everything
./setup.sh
```

This will:
1. Build Docker images for backend and frontend
2. Start the API server on http://localhost:8000
3. Start the Streamlit frontend on http://localhost:8501

**That's it!** Open http://localhost:8501 in your browser to start scoring.

---

## Model Development

The complete model development process is documented in the Jupyter notebook:

```
notebooks/credit_scoring_model.ipynb
```

This notebook contains:

1. **Exploratory Data Analysis (EDA)** - Understanding the Lending Club dataset, distributions, correlations, and target variable analysis
2. **Feature Engineering** - Creating derived features like `loan_to_income`, `installment_to_income`, and `credit_history_months`
3. **Weight of Evidence (WoE) Transformation** - Converting features to WoE values using optimal binning with monotonic constraints
4. **Information Value (IV) Analysis** - Feature selection based on predictive power
5. **Train/Test Split & SMOTE** - Handling class imbalance in default prediction
6. **Model Training** - Logistic Regression with class weights
7. **Model Evaluation** - ROC-AUC, confusion matrix, classification report
8. **Scorecard Creation** - Converting model coefficients to a points-based credit scorecard

**Model Performance:**
- Algorithm: Logistic Regression with `class_weight='balanced'`
- AUC Score: 0.6679
- Score Range: 356 - 671

---

## Features Used for Prediction

The model uses **12 features** to predict default probability. Users provide 11 independent features, and 2 are calculated automatically.

### Independent Features (User Provides)

| Feature | Description | Valid Range |
|---------|-------------|-------------|
| `applicant_id` | Unique identifier for the application | Any string |
| `grade_numeric` | Lending Club credit grade. A=1 (best) to G=7 (highest risk). Assigned by Lending Club based on credit profile. | 1-7 |
| `int_rate` | Annual interest rate (%). Higher rates indicate higher perceived risk by the lender. | 5-31% |
| `inq_last_6mths` | Number of hard credit inquiries in the last 6 months. Many inquiries may indicate financial stress or credit-seeking behavior. | 0+ |
| `revol_util` | Revolving credit utilization (%). The percentage of available revolving credit (e.g., credit cards) currently being used. Below 30% is considered ideal. | 0-150% |
| `installment` | Monthly loan payment amount ($). The fixed amount the borrower pays each month. | $0+ |
| `dti` | Debt-to-Income ratio (%). Total monthly debt payments divided by gross monthly income. Lower is better. | 0-100% |
| `open_acc` | Number of open credit accounts. Includes credit cards, mortgages, auto loans, etc. | 0+ |
| `loan_amnt` | Loan amount requested ($). The total amount the applicant wants to borrow. | $0-$40,000 |
| `annual_inc` | Annual income ($). Total yearly income before taxes. Used to assess repayment capacity. | $20,000+ |
| `credit_history_months` | Length of credit history in months. Calculated from earliest credit line. Longer history generally indicates stability. | 0+ |

### Calculated Features (Auto-Computed)

| Feature | Formula | Description |
|---------|---------|-------------|
| `installment_to_income` | `installment / (annual_inc / 12)` | Monthly payment as a fraction of monthly income. Above 0.40 (40%) triggers a risk override. |
| `loan_to_income` | `loan_amnt / annual_inc` | Loan amount as a fraction of annual income. Above 0.50 (50%) triggers a risk override. |

---

## Project Structure

```
cashi_project/
├── data/                          # Data storage
│   └── predictions.db             # SQLite database for prediction history
│
├── docs/                          # Documentation
│
├── frontend/                      # Streamlit web interface
│   └── app.py                     # Main Streamlit application
│
├── logs/                          # Application logs (auto-created)
│   ├── app.log                    # All application logs (DEBUG+)
│   ├── error.log                  # Error logs only
│   └── predictions.log            # Structured JSON audit log for predictions
│
├── notebooks/                     # Jupyter notebooks
│   └── credit_scoring_model.ipynb # EDA, feature engineering, model training
│
├── src/                           # Source code
│   ├── api/                       # FastAPI application
│   │   ├── main.py                # FastAPI app initialization
│   │   ├── schemas.py             # Pydantic request/response models
│   │   ├── database.py            # SQLite database operations
│   │   └── routes/
│   │       ├── credit.py          # /credit/score endpoint (main scoring logic)
│   │       └── health.py          # /health and /stats endpoints
│   │
│   ├── loader/                    # Data loading utilities
│   │   ├── loader.py              # Data loading functions
│   │   └── preprocessor.py        # Data preprocessing functions
│   │
│   ├── models/                    # Trained model artifacts
│   │   ├── __init__.py            # WoETransformerV2 class definition
│   │   ├── credit_model.pkl       # Trained Logistic Regression model
│   │   ├── woe_transformer.pkl    # Fitted WoE transformer
│   │   ├── model_config.pkl       # Factor, offset, and selected features
│   │   └── scorecard.pkl          # Points-based scorecard table
│   │
│   └── monitoring/                # Logging and monitoring
│       ├── __init__.py
│       └── logger.py              # Loguru configuration
│
├── tests/                         # Test suite
│   ├── conftest.py                # Shared pytest fixtures
│   ├── unit/                      # Unit tests
│   │   ├── test_validate_applicant.py  # Business rules validation tests
│   │   ├── test_risk_override.py       # Risk override logic tests
│   │   └── test_explanation.py         # Explanation generation tests
│   └── integration/               # Integration tests
│       └── test_api_endpoints.py  # API endpoint tests
│
├── main.py                        # Alternative entry point
├── pyproject.toml                 # Project dependencies and configuration
├── uv.lock                        # Dependency lock file
├── Dockerfile                     # Docker image definition
├── docker-compose.yml             # Multi-container orchestration
├── setup.sh                       # All-in-one setup script
└── .dockerignore                  # Files excluded from Docker build
```

---

## Installation

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/aziemma/cashi_project
   cd cashi_project
   ```

2. **Install dependencies with uv**
   ```bash
   uv sync
   ```

   Or with pip:
   ```bash
   pip install -e .
   ```

---

## Running the API

### Start the Backend Server

```bash
uv run uvicorn src.api.main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Using the Frontend

The Streamlit frontend provides a user-friendly interface for credit scoring.

### Start the Frontend

```bash
# In a separate terminal (keep backend running)
uv run streamlit run frontend/app.py
```

The frontend will open at `http://localhost:8501`

### Frontend Pages

1. **Credit Score** - Main scoring form
   - Enter applicant information
   - View auto-calculated ratios with warnings
   - Get credit score, default probability, and risk level
   - Read human-readable explanation

2. **System Health** - Check API status
   - Verify backend is running
   - Check if model is loaded

3. **Statistics** - View prediction history
   - Total predictions count
   - Breakdown by risk level
   - Average credit score

---

## Docker Deployment

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed and running
- [Docker Compose](https://docs.docker.com/compose/install/) (included with Docker Desktop)

### Using the Setup Script

The `setup.sh` script provides a convenient way to manage the application:

```bash
# Build and start everything (default)
./setup.sh

# Other commands
./setup.sh build     # Build Docker images only
./setup.sh start     # Start services (assumes already built)
./setup.sh stop      # Stop all services
./setup.sh restart   # Restart all services
./setup.sh logs      # View logs from all services
./setup.sh clean     # Stop and remove containers, images
./setup.sh local     # Run locally without Docker (development)
./setup.sh help      # Show help
```

### Manual Docker Commands

If you prefer to use Docker commands directly:

```bash
# Build images
docker compose build

# Start services
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down

# Remove everything (including images)
docker compose down --rmi all --volumes
```

### Services

| Service | Port | URL |
|---------|------|-----|
| Backend API | 8000 | http://localhost:8000 |
| API Documentation | 8000 | http://localhost:8000/docs |
| Streamlit Frontend | 8501 | http://localhost:8501 |

### Volumes

The Docker setup mounts these directories for persistence:
- `./data` → `/app/data` (SQLite database)
- `./logs` → `/app/logs` (Application logs)

---

## API Endpoints

### Health Check

```bash
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

### Statistics

```bash
GET /stats
```

**Response:**
```json
{
  "total_predictions": 150,
  "by_risk_level": {"Low": 45, "Medium": 60, "High": 45},
  "avg_credit_score": 512.5,
  "last_24h": 25,
  "model_loaded": true
}
```

### Credit Score

```bash
POST /credit/score
Content-Type: application/json
```

**Request Body:**
```json
{
  "applicant_id": "APP001",
  "grade_numeric": 3,
  "int_rate": 13.5,
  "inq_last_6mths": 0,
  "revol_util": 25.0,
  "installment": 350.0,
  "installment_to_income": 0.07,
  "loan_to_income": 0.30,
  "dti": 15.0,
  "open_acc": 8,
  "loan_amnt": 15000,
  "annual_inc": 50000,
  "credit_history_months": 120
}
```

**Success Response (200):**
```json
{
  "applicant_id": "APP001",
  "credit_score": 590,
  "default_probability": 0.03,
  "risk_level": "Low",
  "explanation": "Low default risk; due to long credit history, favorable interest rate, low debt-to-income ratio."
}
```

**Rejection Response (400):**
```json
{
  "detail": {
    "message": "Application rejected due to validation errors",
    "errors": [
      "Income $15,000 below minimum threshold ($20,000)"
    ]
  }
}
```

### cURL Example

```bash
curl -X POST http://localhost:8000/credit/score \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_id": "TEST001",
    "grade_numeric": 3,
    "int_rate": 13.5,
    "inq_last_6mths": 0,
    "revol_util": 25.0,
    "installment": 350.0,
    "installment_to_income": 0.07,
    "loan_to_income": 0.30,
    "dti": 15.0,
    "open_acc": 8,
    "loan_amnt": 15000,
    "annual_inc": 50000,
    "credit_history_months": 120
  }'
```

---

## Testing

### Run All Tests

```bash
uv run pytest tests/ -v
```

### Run Unit Tests Only

```bash
uv run pytest tests/unit/ -v
```

### Run Integration Tests Only

```bash
uv run pytest tests/integration/ -v
```

### Run with Coverage

```bash
uv run pytest tests/ -v --cov=src --cov-report=html
```

### Test Categories

| Test File | Tests | Coverage |
|-----------|-------|----------|
| `test_validate_applicant.py` | 14 | All 10 business rules (hard rejections + warnings) |
| `test_risk_override.py` | 13 | Risk level classification, score capping at 450 |
| `test_explanation.py` | 21 | Positive/negative factors, warnings in explanations |
| `test_api_endpoints.py` | 18 | All endpoints, error handling, response schemas |

**Total: 68 tests**

---

## Business Rules

The API enforces business rules that go beyond the ML model to handle edge cases.

### Hard Rejections (Block Scoring)

Applications are **rejected** if any of these conditions are true:

| Rule | Threshold | Reason |
|------|-----------|--------|
| Minimum Income | < $20,000 | Insufficient income for loan repayment |
| Maximum Loan | > $40,000 | Exceeds lending limit |
| Interest Rate | < 5% or > 31% | Outside valid product range |
| Credit Grade | < 1 or > 7 | Invalid grade value |
| Negative Values | Any field < 0 | Invalid input data |

### Risk Overrides (Score Capping)

If any of these warnings are triggered, the score is **capped at 450** and probability set to **minimum 70%**:

| Rule | Threshold | Reason |
|------|-----------|--------|
| Loan-to-Income | > 50% | Loan too large relative to income |
| Installment-to-Income | > 40% | Monthly payment burden too high |
| Debt-to-Income | > 60% | Overall debt burden too high |
| Credit History | < 12 months | Insufficient credit history |

### Risk Level Classification

| Score Range | Risk Level |
|-------------|------------|
| 580+ | Low |
| 480-579 | Medium |
| < 480 | High |

---

## License 
Emmanuel Azi-Love

MIT

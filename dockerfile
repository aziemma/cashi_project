# ============================================
# Single-stage, production-safe Dockerfile
# ============================================
FROM python:3.11-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    git \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies INTO SYSTEM PYTHON
RUN uv pip install --system \
    fastapi \
    "uvicorn[standard]" \
    pydantic \
    joblib \
    "numpy>=1.24,<2.4" \
    pandas \
    "scikit-learn>=1.8.0" \
    loguru \
    streamlit \
    requests \
    optbinning

# Copy app
COPY src/ /app/src/
COPY frontend/ /app/frontend/

ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=1

EXPOSE 8000 8501

CMD ["python", "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

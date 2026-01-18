"""Credit scoring endpoint."""

import json
import time
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from fastapi import APIRouter, HTTPException, Request

from ...monitoring import get_logger
from ..schemas import CreditScoreRequest, CreditScoreResponse
from ..database import save_prediction

logger = get_logger()

router = APIRouter(prefix="/credit", tags=["credit"])

# Load model artifacts - use absolute path for reliability
MODEL_DIR = Path(__file__).resolve().parent.parent.parent / "models"

try:
    credit_model = joblib.load(MODEL_DIR / "credit_model.pkl")
    woe_transformer = joblib.load(MODEL_DIR / "woe_transformer.pkl")
    model_config = joblib.load(MODEL_DIR / "model_config.pkl")

    FACTOR = model_config["factor"]
    OFFSET = model_config["offset"]
    SELECTED_FEATURES = model_config["selected_features"]
    MODEL_LOADED = True
    logger.info("Credit scoring model loaded successfully")
except Exception as e:
    logger.error(f"Error loading model: {e}")
    MODEL_LOADED = False
    credit_model = None
    woe_transformer = None
    FACTOR = None
    OFFSET = None
    SELECTED_FEATURES = None


def validate_applicant(data: dict) -> tuple[list, list]:
    """
    Business rules validation.
    Returns (errors, warnings) - errors block scoring, warnings are advisory.
    """
    errors = []
    warnings = []

    # Hard rejection rules (errors)
    if data["annual_inc"] < 20000:
        errors.append(f"Income ${data['annual_inc']:,.0f} below minimum threshold ($20,000)")

    if data["loan_amnt"] > 40000:
        errors.append(f"Loan amount ${data['loan_amnt']:,.0f} exceeds maximum ($40,000)")

    if data["int_rate"] < 5 or data["int_rate"] > 31:
        errors.append(f"Interest rate {data['int_rate']}% outside valid range (5-31%)")

    if data["grade_numeric"] < 1 or data["grade_numeric"] > 7:
        errors.append(f"Grade {data['grade_numeric']} invalid (must be 1-7)")

    # Check for negative values
    for key, value in data.items():
        if key != "applicant_id" and value < 0:
            errors.append(f"{key} cannot be negative")

    # Warning rules (don't block but flag risk)
    if data["loan_amnt"] / (data["annual_inc"] + 1) > 0.5:
        warnings.append("Loan-to-income ratio exceeds 50%")

    if data["installment_to_income"] > 0.40:
        warnings.append("Monthly payment exceeds 40% of monthly income")

    if data["dti"] > 60:
        warnings.append("Debt-to-income ratio exceeds 60%")

    if data["credit_history_months"] < 12:
        warnings.append("Credit history less than 1 year")

    if data["revol_util"] > 100:
        warnings.append("Revolving utilization exceeds 100%")

    return errors, warnings


def apply_risk_override(score: int, prob: float, warnings: list) -> tuple[int, float, str]:
    """
    Apply risk override if business rules are violated.
    Returns (adjusted_score, adjusted_prob, risk_level).
    """
    risk_override = False

    # Check for high-risk override conditions
    high_risk_warnings = [
        "Loan-to-income ratio exceeds 50%",
        "Monthly payment exceeds 40% of monthly income",
        "Debt-to-income ratio exceeds 60%",
        "Credit history less than 1 year"
    ]

    for warning in warnings:
        if warning in high_risk_warnings:
            risk_override = True
            break

    if risk_override:
        score = min(score, 450)
        prob = max(prob, 0.70)

    # Determine risk level
    if score >= 580:
        risk_level = "Low"
    elif score >= 480:
        risk_level = "Medium"
    else:
        risk_level = "High"

    return score, prob, risk_level


def score_applicant(data: dict) -> tuple[int, float]:
    """
    Score a single applicant using the trained model.
    Returns (credit_score, default_probability).
    """
    # Cap revol_util at 100 if exceeded
    if data["revol_util"] > 100:
        data["revol_util"] = 100.0

    # Prepare features DataFrame
    features = {feat: data[feat] for feat in SELECTED_FEATURES}
    df = pd.DataFrame([features])

    # Transform to WoE
    df_woe = woe_transformer.transform(df, SELECTED_FEATURES)

    # Get default probability
    default_prob = credit_model.predict_proba(df_woe)[0][1]

    # Calculate credit score
    if 0 < default_prob < 1:
        score = OFFSET - FACTOR * np.log(default_prob / (1 - default_prob))
    else:
        score = OFFSET

    return int(round(score)), round(float(default_prob), 2)


def generate_explanation(data: dict, risk_level: str, warnings: list) -> str:
    """
    Generate human-readable explanation for the credit score.
    """
    explanations = []

    # Risk level intro
    if risk_level == "Low":
        explanations.append("Low default risk")
    elif risk_level == "Medium":
        explanations.append("Moderate default risk")
    else:
        explanations.append("High default risk")

    # Positive factors
    positives = []
    if data["credit_history_months"] >= 120:
        positives.append("long credit history")
    elif data["credit_history_months"] >= 60:
        positives.append("established credit history")

    if data["int_rate"] < 14:
        positives.append("favorable interest rate")

    if data["dti"] < 20:
        positives.append("low debt-to-income ratio")

    if data["revol_util"] < 30:
        positives.append("low credit utilization")

    if data["inq_last_6mths"] == 0:
        positives.append("no recent credit inquiries")

    if data["annual_inc"] >= 100000:
        positives.append("strong income")
    elif data["annual_inc"] >= 60000:
        positives.append("stable income")

    # Negative factors
    negatives = []
    if data["int_rate"] >= 20:
        negatives.append("high interest rate indicates elevated risk profile")

    if data["revol_util"] >= 70:
        negatives.append("high credit utilization")

    if data["dti"] >= 35:
        negatives.append("elevated debt burden")

    if data["inq_last_6mths"] >= 3:
        negatives.append("multiple recent credit inquiries")

    if data["credit_history_months"] < 36:
        negatives.append("limited credit history")

    if data["grade_numeric"] >= 5:
        negatives.append("subprime credit grade")

    # Add warnings as negatives
    for warning in warnings:
        if "Loan-to-income" in warning:
            negatives.append("loan amount high relative to income")
        elif "Monthly payment exceeds" in warning:
            negatives.append("monthly payment burden is significant")

    # Build explanation
    if positives:
        explanations.append(f"due to {', '.join(positives[:3])}")

    if negatives:
        if positives:
            explanations.append(f"however, {', '.join(negatives[:2])}")
        else:
            explanations.append(f"due to {', '.join(negatives[:3])}")

    return "; ".join(explanations) + "."


@router.post("/score", response_model=CreditScoreResponse)
async def get_credit_score(request: CreditScoreRequest, req: Request):
    """
    Calculate credit score for an applicant.

    Returns credit score (356-671 range), default probability, risk level, and explanation.
    Includes business rule validation and risk overrides.
    """
    start_time = time.time()

    if not MODEL_LOADED:
        logger.error("Model not loaded - rejecting request")
        raise HTTPException(status_code=503, detail="Model not loaded")

    # Convert request to dict
    data = request.model_dump()

    logger.info(f"Scoring request for applicant: {data['applicant_id']}")

    # Validate business rules
    errors, warnings = validate_applicant(data)

    # If hard errors, reject
    if errors:
        logger.warning(f"Applicant {data['applicant_id']} rejected: {errors}")
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Application rejected due to validation errors",
                "errors": errors
            }
        )

    # Score the applicant
    credit_score, default_prob = score_applicant(data)

    # Apply risk overrides if warnings exist
    credit_score, default_prob, risk_level = apply_risk_override(
        credit_score, default_prob, warnings
    )

    # Generate explanation
    explanation = generate_explanation(data, risk_level, warnings)

    # Calculate response time
    response_time_ms = (time.time() - start_time) * 1000

    # Log the prediction (human-readable)
    logger.info(
        f"Applicant {data['applicant_id']}: "
        f"score={credit_score}, prob={default_prob}, risk={risk_level}, "
        f"response_time={response_time_ms:.2f}ms"
    )

    # Log structured prediction for audit (JSON format)
    prediction_log = json.dumps({
        "type": "PREDICTION",
        "applicant_id": data["applicant_id"],
        "credit_score": credit_score,
        "default_probability": default_prob,
        "risk_level": risk_level,
        "response_time_ms": round(response_time_ms, 2),
        "input": {k: v for k, v in data.items() if k != "applicant_id"}
    })
    logger.info(f"PREDICTION: {prediction_log}")

    # Get client IP
    client_ip = req.client.host if req.client else None

    # Save to database
    try:
        save_prediction(
            applicant_id=data["applicant_id"],
            credit_score=credit_score,
            default_probability=default_prob,
            risk_level=risk_level,
            explanation=explanation,
            input_data=data,
            request_ip=client_ip,
            response_time_ms=response_time_ms
        )
    except Exception as e:
        logger.error(f"Failed to save prediction to database: {e}")

    return CreditScoreResponse(
        applicant_id=data["applicant_id"],
        credit_score=credit_score,
        default_probability=default_prob,
        risk_level=risk_level,
        explanation=explanation
    )

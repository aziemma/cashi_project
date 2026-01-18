"""Pydantic schemas for API request/response validation."""

from pydantic import BaseModel, Field
from typing import Optional


class CreditScoreRequest(BaseModel):
    """Request schema for credit scoring endpoint."""

    applicant_id: str = Field(..., description="Unique identifier for the applicant")
    grade_numeric: float = Field(..., ge=1, le=7, description="Grade as numeric (A=1 to G=7)")
    int_rate: float = Field(..., ge=0, le=35, description="Interest rate percentage")
    inq_last_6mths: float = Field(..., ge=0, description="Inquiries in last 6 months")
    revol_util: float = Field(..., ge=0, description="Revolving utilization percentage")
    installment: float = Field(..., ge=0, description="Monthly installment amount")
    installment_to_income: float = Field(..., ge=0, description="Installment to monthly income ratio")
    loan_to_income: float = Field(..., ge=0, description="Loan amount to annual income ratio")
    dti: float = Field(..., ge=0, description="Debt-to-income ratio")
    open_acc: float = Field(..., ge=0, description="Number of open accounts")
    loan_amnt: float = Field(..., ge=0, description="Loan amount requested")
    annual_inc: float = Field(..., ge=0, description="Annual income")
    credit_history_months: float = Field(..., ge=0, description="Length of credit history in months")

    class Config:
        json_schema_extra = {
            "example": {
                "applicant_id": "app_001",
                "grade_numeric": 3,
                "int_rate": 13.5,
                "inq_last_6mths": 0,
                "revol_util": 61.0,
                "installment": 1188,
                "installment_to_income": 0.11,
                "loan_to_income": 0.28,
                "dti": 17.0,
                "open_acc": 12,
                "loan_amnt": 35000,
                "annual_inc": 125000,
                "credit_history_months": 230
            }
        }


class CreditScoreResponse(BaseModel):
    """Response schema for credit scoring endpoint."""

    applicant_id: str
    credit_score: int
    default_probability: float
    risk_level: str
    explanation: str


class HealthResponse(BaseModel):
    """Response schema for health check endpoint."""

    status: str
    model_loaded: bool

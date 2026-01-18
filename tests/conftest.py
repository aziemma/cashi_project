"""Shared pytest fixtures for all tests."""

import pytest


@pytest.fixture
def valid_applicant_data():
    """A valid applicant that passes all business rules."""
    return {
        "applicant_id": "test_valid_001",
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


@pytest.fixture
def low_income_applicant():
    """Applicant with income below $20K threshold."""
    return {
        "applicant_id": "test_low_income",
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
        "annual_inc": 15000,  # Below $20K
        "credit_history_months": 120
    }


@pytest.fixture
def high_loan_applicant():
    """Applicant requesting loan above $40K limit."""
    return {
        "applicant_id": "test_high_loan",
        "grade_numeric": 3,
        "int_rate": 13.5,
        "inq_last_6mths": 0,
        "revol_util": 25.0,
        "installment": 350.0,
        "installment_to_income": 0.07,
        "loan_to_income": 0.30,
        "dti": 15.0,
        "open_acc": 8,
        "loan_amnt": 50000,  # Above $40K
        "annual_inc": 100000,
        "credit_history_months": 120
    }


@pytest.fixture
def high_risk_applicant():
    """Applicant that triggers risk override warnings."""
    return {
        "applicant_id": "test_high_risk",
        "grade_numeric": 5,
        "int_rate": 22.0,
        "inq_last_6mths": 4,
        "revol_util": 85.0,
        "installment": 800.0,
        "installment_to_income": 0.45,  # Triggers warning
        "loan_to_income": 0.60,  # Triggers warning
        "dti": 65.0,  # Triggers warning
        "open_acc": 12,
        "loan_amnt": 30000,
        "annual_inc": 50000,
        "credit_history_months": 8  # Triggers warning
    }


@pytest.fixture
def short_credit_history_applicant():
    """Applicant with credit history less than 1 year."""
    return {
        "applicant_id": "test_short_history",
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
        "credit_history_months": 6  # Less than 12 months
    }

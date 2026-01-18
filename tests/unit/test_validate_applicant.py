"""Unit tests for validate_applicant() business rules."""

import pytest
from src.api.routes.credit import validate_applicant


class TestHardRejectionRules:
    """Tests for hard rejection rules (errors that block scoring)."""

    def test_valid_applicant_no_errors(self, valid_applicant_data):
        """Valid applicant should have no errors."""
        errors, warnings = validate_applicant(valid_applicant_data)
        assert len(errors) == 0

    def test_income_below_minimum_rejected(self, low_income_applicant):
        """Income below $20K should be rejected."""
        errors, warnings = validate_applicant(low_income_applicant)
        assert len(errors) == 1
        assert "below minimum threshold" in errors[0]
        assert "$20,000" in errors[0]

    def test_loan_above_maximum_rejected(self, high_loan_applicant):
        """Loan amount above $40K should be rejected."""
        errors, warnings = validate_applicant(high_loan_applicant)
        assert len(errors) == 1
        assert "exceeds maximum" in errors[0]
        assert "$40,000" in errors[0]

    def test_interest_rate_below_range_rejected(self, valid_applicant_data):
        """Interest rate below 5% should be rejected."""
        data = valid_applicant_data.copy()
        data["int_rate"] = 3.0
        errors, warnings = validate_applicant(data)
        assert len(errors) == 1
        assert "outside valid range" in errors[0]

    def test_interest_rate_above_range_rejected(self, valid_applicant_data):
        """Interest rate above 31% should be rejected."""
        data = valid_applicant_data.copy()
        data["int_rate"] = 35.0
        errors, warnings = validate_applicant(data)
        assert len(errors) == 1
        assert "outside valid range" in errors[0]

    def test_invalid_grade_below_range_rejected(self, valid_applicant_data):
        """Grade below 1 should be rejected."""
        data = valid_applicant_data.copy()
        data["grade_numeric"] = 0
        errors, warnings = validate_applicant(data)
        assert len(errors) == 1
        assert "invalid" in errors[0].lower()

    def test_invalid_grade_above_range_rejected(self, valid_applicant_data):
        """Grade above 7 should be rejected."""
        data = valid_applicant_data.copy()
        data["grade_numeric"] = 8
        errors, warnings = validate_applicant(data)
        assert len(errors) == 1
        assert "invalid" in errors[0].lower()

    def test_negative_value_rejected(self, valid_applicant_data):
        """Negative values should be rejected."""
        data = valid_applicant_data.copy()
        data["annual_inc"] = -5000
        errors, warnings = validate_applicant(data)
        assert any("cannot be negative" in e for e in errors)

    def test_multiple_errors_all_returned(self):
        """Multiple validation failures should all be returned."""
        data = {
            "applicant_id": "test_multiple",
            "grade_numeric": 10,  # Invalid
            "int_rate": 2.0,  # Too low
            "inq_last_6mths": 0,
            "revol_util": 25.0,
            "installment": 350.0,
            "installment_to_income": 0.07,
            "loan_to_income": 0.30,
            "dti": 15.0,
            "open_acc": 8,
            "loan_amnt": 50000,  # Too high
            "annual_inc": 10000,  # Too low
            "credit_history_months": 120
        }
        errors, warnings = validate_applicant(data)
        assert len(errors) >= 4


class TestWarningRules:
    """Tests for warning rules (flags but doesn't block)."""

    def test_high_loan_to_income_ratio_warning(self, valid_applicant_data):
        """Loan-to-income > 50% should trigger warning."""
        data = valid_applicant_data.copy()
        data["loan_amnt"] = 30000
        data["annual_inc"] = 50000  # 60% ratio
        errors, warnings = validate_applicant(data)
        assert len(errors) == 0
        assert any("Loan-to-income ratio exceeds 50%" in w for w in warnings)

    def test_high_installment_to_income_warning(self, valid_applicant_data):
        """Installment-to-income > 40% should trigger warning."""
        data = valid_applicant_data.copy()
        data["installment_to_income"] = 0.45
        errors, warnings = validate_applicant(data)
        assert len(errors) == 0
        assert any("Monthly payment exceeds 40%" in w for w in warnings)

    def test_high_dti_warning(self, valid_applicant_data):
        """DTI > 60 should trigger warning."""
        data = valid_applicant_data.copy()
        data["dti"] = 65.0
        errors, warnings = validate_applicant(data)
        assert len(errors) == 0
        assert any("Debt-to-income ratio exceeds 60%" in w for w in warnings)

    def test_short_credit_history_warning(self, short_credit_history_applicant):
        """Credit history < 12 months should trigger warning."""
        errors, warnings = validate_applicant(short_credit_history_applicant)
        assert len(errors) == 0
        assert any("Credit history less than 1 year" in w for w in warnings)

    def test_high_revol_util_warning(self, valid_applicant_data):
        """Revolving utilization > 100% should trigger warning."""
        data = valid_applicant_data.copy()
        data["revol_util"] = 110.0
        errors, warnings = validate_applicant(data)
        assert len(errors) == 0
        assert any("Revolving utilization exceeds 100%" in w for w in warnings)

    def test_multiple_warnings(self, high_risk_applicant):
        """Applicant with multiple risk factors should have multiple warnings."""
        errors, warnings = validate_applicant(high_risk_applicant)
        assert len(errors) == 0
        assert len(warnings) >= 3  # DTI, installment-to-income, credit history

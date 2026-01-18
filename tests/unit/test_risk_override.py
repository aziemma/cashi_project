"""Unit tests for apply_risk_override() function."""

import pytest
from src.api.routes.credit import apply_risk_override


class TestRiskLevelClassification:
    """Tests for risk level classification based on score."""

    def test_low_risk_score_above_580(self):
        """Score >= 580 should be Low risk."""
        score, prob, risk_level = apply_risk_override(600, 0.05, [])
        assert risk_level == "Low"
        assert score == 600
        assert prob == 0.05

    def test_medium_risk_score_480_to_579(self):
        """Score 480-579 should be Medium risk."""
        score, prob, risk_level = apply_risk_override(520, 0.20, [])
        assert risk_level == "Medium"

    def test_high_risk_score_below_480(self):
        """Score < 480 should be High risk."""
        score, prob, risk_level = apply_risk_override(400, 0.60, [])
        assert risk_level == "High"

    def test_boundary_score_580_is_low(self):
        """Score exactly 580 should be Low risk."""
        score, prob, risk_level = apply_risk_override(580, 0.10, [])
        assert risk_level == "Low"

    def test_boundary_score_479_is_high(self):
        """Score exactly 479 should be High risk."""
        score, prob, risk_level = apply_risk_override(479, 0.40, [])
        assert risk_level == "High"


class TestRiskOverrideApplication:
    """Tests for risk override when warnings are present."""

    def test_loan_to_income_warning_caps_score(self):
        """Loan-to-income warning should cap score at 450."""
        warnings = ["Loan-to-income ratio exceeds 50%"]
        score, prob, risk_level = apply_risk_override(600, 0.05, warnings)
        assert score == 450
        assert prob == 0.70
        assert risk_level == "High"

    def test_installment_to_income_warning_caps_score(self):
        """Installment-to-income warning should cap score at 450."""
        warnings = ["Monthly payment exceeds 40% of monthly income"]
        score, prob, risk_level = apply_risk_override(550, 0.10, warnings)
        assert score == 450
        assert prob == 0.70

    def test_dti_warning_caps_score(self):
        """DTI warning should cap score at 450."""
        warnings = ["Debt-to-income ratio exceeds 60%"]
        score, prob, risk_level = apply_risk_override(580, 0.08, warnings)
        assert score == 450
        assert prob == 0.70

    def test_short_credit_history_warning_caps_score(self):
        """Short credit history warning should cap score at 450."""
        warnings = ["Credit history less than 1 year"]
        score, prob, risk_level = apply_risk_override(590, 0.06, warnings)
        assert score == 450
        assert prob == 0.70

    def test_revol_util_warning_no_override(self):
        """Revolving utilization warning should NOT trigger override."""
        warnings = ["Revolving utilization exceeds 100%"]
        score, prob, risk_level = apply_risk_override(600, 0.05, warnings)
        assert score == 600  # Not capped
        assert prob == 0.05  # Not increased
        assert risk_level == "Low"

    def test_multiple_warnings_still_caps_once(self):
        """Multiple warnings should cap score once at 450."""
        warnings = [
            "Loan-to-income ratio exceeds 50%",
            "Monthly payment exceeds 40% of monthly income",
            "Debt-to-income ratio exceeds 60%"
        ]
        score, prob, risk_level = apply_risk_override(600, 0.03, warnings)
        assert score == 450
        assert prob == 0.70

    def test_low_score_not_increased_by_override(self):
        """Score already below 450 should not be changed."""
        warnings = ["Loan-to-income ratio exceeds 50%"]
        score, prob, risk_level = apply_risk_override(400, 0.80, warnings)
        assert score == 400  # min(400, 450) = 400
        assert prob == 0.80  # max(0.80, 0.70) = 0.80

    def test_empty_warnings_no_override(self):
        """No warnings should not trigger override."""
        score, prob, risk_level = apply_risk_override(600, 0.05, [])
        assert score == 600
        assert prob == 0.05

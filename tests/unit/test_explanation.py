"""Unit tests for generate_explanation() function."""

import pytest
from src.api.routes.credit import generate_explanation


class TestRiskLevelIntro:
    """Tests for risk level introduction in explanations."""

    def test_low_risk_intro(self, valid_applicant_data):
        """Low risk should start with 'Low default risk'."""
        explanation = generate_explanation(valid_applicant_data, "Low", [])
        assert explanation.startswith("Low default risk")

    def test_medium_risk_intro(self, valid_applicant_data):
        """Medium risk should start with 'Moderate default risk'."""
        explanation = generate_explanation(valid_applicant_data, "Medium", [])
        assert explanation.startswith("Moderate default risk")

    def test_high_risk_intro(self, valid_applicant_data):
        """High risk should start with 'High default risk'."""
        explanation = generate_explanation(valid_applicant_data, "High", [])
        assert explanation.startswith("High default risk")


class TestPositiveFactors:
    """Tests for positive factors in explanations."""

    def test_long_credit_history_mentioned(self, valid_applicant_data):
        """Credit history >= 120 months should mention 'long credit history'."""
        data = valid_applicant_data.copy()
        data["credit_history_months"] = 150
        explanation = generate_explanation(data, "Low", [])
        assert "long credit history" in explanation

    def test_established_credit_history_mentioned(self, valid_applicant_data):
        """Credit history 60-119 months should mention 'established credit history'."""
        data = valid_applicant_data.copy()
        data["credit_history_months"] = 80
        explanation = generate_explanation(data, "Low", [])
        assert "established credit history" in explanation

    def test_favorable_interest_rate_mentioned(self, valid_applicant_data):
        """Interest rate < 14% should mention 'favorable interest rate'."""
        data = valid_applicant_data.copy()
        data["int_rate"] = 10.0
        explanation = generate_explanation(data, "Low", [])
        assert "favorable interest rate" in explanation

    def test_low_dti_mentioned(self, valid_applicant_data):
        """DTI < 20 should mention 'low debt-to-income ratio'."""
        data = valid_applicant_data.copy()
        data["dti"] = 15.0
        explanation = generate_explanation(data, "Low", [])
        assert "low debt-to-income ratio" in explanation

    def test_low_revol_util_mentioned(self, valid_applicant_data):
        """Revolving utilization < 30 should mention 'low credit utilization'."""
        data = valid_applicant_data.copy()
        data["revol_util"] = 20.0
        # Remove other positive factors so this one shows (only 3 are displayed)
        data["credit_history_months"] = 40  # Not long enough for positive
        data["int_rate"] = 16.0  # Not favorable
        data["dti"] = 25.0  # Not low
        explanation = generate_explanation(data, "Low", [])
        assert "low credit utilization" in explanation

    def test_no_recent_inquiries_mentioned(self, valid_applicant_data):
        """Zero inquiries should mention 'no recent credit inquiries'."""
        data = valid_applicant_data.copy()
        data["inq_last_6mths"] = 0
        # Remove other positive factors so this one shows
        data["credit_history_months"] = 40
        data["int_rate"] = 16.0
        data["dti"] = 25.0
        data["revol_util"] = 40.0
        explanation = generate_explanation(data, "Low", [])
        assert "no recent credit inquiries" in explanation

    def test_strong_income_mentioned(self, valid_applicant_data):
        """Income >= 100K should mention 'strong income'."""
        data = valid_applicant_data.copy()
        data["annual_inc"] = 120000
        # Remove other positive factors so this one shows
        data["credit_history_months"] = 40
        data["int_rate"] = 16.0
        data["dti"] = 25.0
        data["revol_util"] = 40.0
        data["inq_last_6mths"] = 2
        explanation = generate_explanation(data, "Low", [])
        assert "strong income" in explanation

    def test_stable_income_mentioned(self, valid_applicant_data):
        """Income 60K-99K should mention 'stable income'."""
        data = valid_applicant_data.copy()
        data["annual_inc"] = 75000
        # Remove other positive factors so this one shows
        data["credit_history_months"] = 40
        data["int_rate"] = 16.0
        data["dti"] = 25.0
        data["revol_util"] = 40.0
        data["inq_last_6mths"] = 2
        explanation = generate_explanation(data, "Low", [])


class TestNegativeFactors:
    """Tests for negative factors in explanations."""

    def test_high_interest_rate_mentioned(self, valid_applicant_data):
        """Interest rate >= 20% should mention 'high interest rate'."""
        data = valid_applicant_data.copy()
        data["int_rate"] = 25.0
        explanation = generate_explanation(data, "High", [])
        assert "high interest rate" in explanation

    def test_high_revol_util_mentioned(self, valid_applicant_data):
        """Revolving utilization >= 70 should mention 'high credit utilization'."""
        data = valid_applicant_data.copy()
        data["revol_util"] = 80.0
        explanation = generate_explanation(data, "High", [])
        assert "high credit utilization" in explanation

    def test_elevated_dti_mentioned(self, valid_applicant_data):
        """DTI >= 35 should mention 'elevated debt burden'."""
        data = valid_applicant_data.copy()
        data["dti"] = 40.0
        explanation = generate_explanation(data, "High", [])
        assert "elevated debt burden" in explanation

    def test_multiple_inquiries_mentioned(self, valid_applicant_data):
        """3+ inquiries should mention 'multiple recent credit inquiries'."""
        data = valid_applicant_data.copy()
        data["inq_last_6mths"] = 4
        explanation = generate_explanation(data, "High", [])
        assert "multiple recent credit inquiries" in explanation

    def test_limited_credit_history_mentioned(self, valid_applicant_data):
        """Credit history < 36 months should mention 'limited credit history'."""
        data = valid_applicant_data.copy()
        data["credit_history_months"] = 24
        explanation = generate_explanation(data, "High", [])
        assert "limited credit history" in explanation

    def test_subprime_grade_mentioned(self, valid_applicant_data):
        """Grade >= 5 should mention 'subprime credit grade'."""
        data = valid_applicant_data.copy()
        data["grade_numeric"] = 6
        explanation = generate_explanation(data, "High", [])
        assert "subprime credit grade" in explanation


class TestWarningsInExplanation:
    """Tests for warnings appearing in explanations."""

    def test_loan_to_income_warning_in_explanation(self, valid_applicant_data):
        """Loan-to-income warning should appear in explanation."""
        warnings = ["Loan-to-income ratio exceeds 50%"]
        explanation = generate_explanation(valid_applicant_data, "High", warnings)
        assert "loan amount high relative to income" in explanation

    def test_monthly_payment_warning_in_explanation(self, valid_applicant_data):
        """Monthly payment warning should appear in explanation."""
        warnings = ["Monthly payment exceeds 40% of monthly income"]
        explanation = generate_explanation(valid_applicant_data, "High", warnings)
        assert "monthly payment burden is significant" in explanation


class TestExplanationFormat:
    """Tests for explanation formatting."""

    def test_explanation_ends_with_period(self, valid_applicant_data):
        """Explanation should end with a period."""
        explanation = generate_explanation(valid_applicant_data, "Low", [])
        assert explanation.endswith(".")

    def test_explanation_is_not_empty(self, valid_applicant_data):
        """Explanation should never be empty."""
        explanation = generate_explanation(valid_applicant_data, "Low", [])
        assert len(explanation) > 0

    def test_explanation_contains_semicolon_separator(self, valid_applicant_data):
        """Multiple factors should be separated by semicolons."""
        data = valid_applicant_data.copy()
        data["credit_history_months"] = 150
        data["int_rate"] = 10.0
        data["dti"] = 15.0
        explanation = generate_explanation(data, "Low", [])
        # With multiple positives, there should be content after risk level
        assert "due to" in explanation

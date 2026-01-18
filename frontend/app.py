"""Cashi Credit Scoring - Streamlit Frontend."""

import os
import streamlit as st
import requests
import uuid

# API Configuration - use environment variable for Docker, fallback to localhost
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Cashi Credit Scoring",
    page_icon="💳",
    layout="wide"
)

# Sidebar navigation
st.sidebar.title("Cashi Credit Scoring")
page = st.sidebar.radio(
    "Navigate",
    ["Credit Score", "System Health", "Statistics"]
)


def check_api_health():
    """Check if API is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200, response.json()
    except requests.exceptions.ConnectionError:
        return False, {"error": "Cannot connect to API"}
    except Exception as e:
        return False, {"error": str(e)}


# ============================================
# CREDIT SCORE PAGE
# ============================================
if page == "Credit Score":
    st.title("Credit Score Calculator")
    st.markdown("Enter applicant information to calculate credit score and default risk.")

    # Check API status
    api_ok, health_data = check_api_health()
    if not api_ok:
        st.error("API is not running. Please start the backend server first: `uv run uvicorn src.api.main:app --reload`")
        st.stop()

    if not health_data.get("model_loaded", False):
        st.warning("Model is not loaded. Predictions may not be available.")

    st.divider()

    # Form layout
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Applicant Information")

        applicant_id = st.text_input(
            "Applicant ID",
            value=str(uuid.uuid4())[:8],
            help="Unique identifier for this application"
        )

        annual_inc = st.number_input(
            "Annual Income ($)",
            min_value=0.0,
            max_value=1000000.0,
            value=50000.0,
            step=1000.0,
            help="Total yearly income before taxes. Used to assess repayment capacity."
        )

        loan_amnt = st.number_input(
            "Loan Amount Requested ($)",
            min_value=0.0,
            max_value=100000.0,
            value=15000.0,
            step=500.0,
            help="The total amount the applicant wants to borrow."
        )

        installment = st.number_input(
            "Monthly Installment ($)",
            min_value=0.0,
            max_value=5000.0,
            value=350.0,
            step=10.0,
            help="The fixed monthly payment amount for this loan."
        )

        grade_numeric = st.selectbox(
            "Credit Grade",
            options=[1, 2, 3, 4, 5, 6, 7],
            index=2,
            format_func=lambda x: f"{chr(64+x)} (Grade {x})",
            help="Lending Club grade: A=1 (best) to G=7 (highest risk). Assigned based on credit profile."
        )

        int_rate = st.slider(
            "Interest Rate (%)",
            min_value=5.0,
            max_value=31.0,
            value=13.5,
            step=0.1,
            help="Annual interest rate for this loan. Higher rates indicate higher perceived risk."
        )

    with col2:
        st.subheader("Credit Profile")

        credit_history_months = st.number_input(
            "Credit History (months)",
            min_value=0,
            max_value=600,
            value=120,
            step=6,
            help="How long the applicant has had credit accounts. Longer history generally indicates stability."
        )

        dti = st.slider(
            "Debt-to-Income Ratio (%)",
            min_value=0.0,
            max_value=100.0,
            value=15.0,
            step=0.5,
            help="Total monthly debt payments divided by monthly income. Lower is better."
        )

        revol_util = st.slider(
            "Revolving Credit Utilization (%)",
            min_value=0.0,
            max_value=150.0,
            value=25.0,
            step=1.0,
            help="Percentage of available revolving credit being used (e.g., credit cards). Below 30% is ideal."
        )

        open_acc = st.number_input(
            "Open Accounts",
            min_value=0,
            max_value=50,
            value=8,
            step=1,
            help="Number of currently open credit accounts (credit cards, loans, etc.)."
        )

        inq_last_6mths = st.number_input(
            "Credit Inquiries (last 6 months)",
            min_value=0,
            max_value=20,
            value=0,
            step=1,
            help="Number of hard credit inquiries. Many inquiries may indicate financial stress."
        )

    st.divider()

    # Calculated fields section
    st.subheader("Calculated Ratios")
    st.markdown("*These are automatically computed from the values above.*")

    # Calculate dependent fields
    monthly_income = annual_inc / 12 if annual_inc > 0 else 1
    installment_to_income = installment / monthly_income
    loan_to_income = loan_amnt / annual_inc if annual_inc > 0 else 0

    calc_col1, calc_col2 = st.columns(2)

    with calc_col1:
        st.metric(
            "Installment-to-Income Ratio",
            f"{installment_to_income:.2%}",
            help="Monthly payment as percentage of monthly income. Above 40% triggers risk override."
        )
        if installment_to_income > 0.40:
            st.warning("Above 40% - High payment burden")
        elif installment_to_income > 0.30:
            st.info("30-40% - Moderate payment burden")
        else:
            st.success("Below 30% - Manageable payment")

    with calc_col2:
        st.metric(
            "Loan-to-Income Ratio",
            f"{loan_to_income:.2%}",
            help="Loan amount as percentage of annual income. Above 50% triggers risk override."
        )
        if loan_to_income > 0.50:
            st.warning("Above 50% - High loan relative to income")
        elif loan_to_income > 0.30:
            st.info("30-50% - Moderate loan size")
        else:
            st.success("Below 30% - Conservative loan size")

    st.divider()

    # Submit button
    if st.button("Calculate Credit Score", type="primary", use_container_width=True):
        # Prepare request payload
        payload = {
            "applicant_id": applicant_id,
            "grade_numeric": float(grade_numeric),
            "int_rate": float(int_rate),
            "inq_last_6mths": float(inq_last_6mths),
            "revol_util": float(revol_util),
            "installment": float(installment),
            "installment_to_income": float(installment_to_income),
            "loan_to_income": float(loan_to_income),
            "dti": float(dti),
            "open_acc": float(open_acc),
            "loan_amnt": float(loan_amnt),
            "annual_inc": float(annual_inc),
            "credit_history_months": float(credit_history_months)
        }

        with st.spinner("Calculating credit score..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/credit/score",
                    json=payload,
                    timeout=10
                )

                if response.status_code == 200:
                    result = response.json()

                    st.success("Credit score calculated successfully!")

                    # Display results
                    result_col1, result_col2, result_col3 = st.columns(3)

                    with result_col1:
                        score = result["credit_score"]
                        score_color = "green" if score >= 580 else "orange" if score >= 480 else "red"
                        st.markdown(f"### Credit Score")
                        st.markdown(f"# :{score_color}[{score}]")
                        st.caption("Range: 356 - 671")

                    with result_col2:
                        prob = result["default_probability"]
                        prob_color = "green" if prob < 0.15 else "orange" if prob < 0.50 else "red"
                        st.markdown(f"### Default Probability")
                        st.markdown(f"# :{prob_color}[{prob:.0%}]")
                        st.caption("Lower is better")

                    with result_col3:
                        risk = result["risk_level"]
                        risk_color = "green" if risk == "Low" else "orange" if risk == "Medium" else "red"
                        st.markdown(f"### Risk Level")
                        st.markdown(f"# :{risk_color}[{risk}]")
                        st.caption("Low / Medium / High")

                    st.divider()

                    st.subheader("Explanation")
                    st.info(result["explanation"])

                elif response.status_code == 400:
                    error_data = response.json()
                    st.error("Application Rejected")
                    if "detail" in error_data and "errors" in error_data["detail"]:
                        for error in error_data["detail"]["errors"]:
                            st.error(f"- {error}")
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")

            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to API. Is the backend running?")
            except Exception as e:
                st.error(f"Error: {str(e)}")


# ============================================
# SYSTEM HEALTH PAGE
# ============================================
elif page == "System Health":
    st.title("System Health")
    st.markdown("Check the status of the credit scoring API.")

    if st.button("Check Health", type="primary"):
        with st.spinner("Checking API health..."):
            api_ok, health_data = check_api_health()

            if api_ok:
                st.success("API is running!")

                col1, col2 = st.columns(2)

                with col1:
                    status = health_data.get("status", "unknown")
                    status_color = "green" if status == "healthy" else "orange"
                    st.metric("Status", status)

                with col2:
                    model_loaded = health_data.get("model_loaded", False)
                    st.metric("Model Loaded", "Yes" if model_loaded else "No")

                st.json(health_data)
            else:
                st.error("API is not responding")
                st.json(health_data)


# ============================================
# STATISTICS PAGE
# ============================================
elif page == "Statistics":
    st.title("Prediction Statistics")
    st.markdown("View statistics about credit score predictions.")

    if st.button("Load Statistics", type="primary"):
        with st.spinner("Loading statistics..."):
            try:
                response = requests.get(f"{API_BASE_URL}/stats", timeout=5)

                if response.status_code == 200:
                    stats = response.json()

                    # Summary metrics
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric("Total Predictions", stats.get("total_predictions", 0))

                    with col2:
                        st.metric("Last 24 Hours", stats.get("last_24h", 0))

                    with col3:
                        avg_score = stats.get("avg_credit_score", 0)
                        st.metric("Average Score", f"{avg_score:.0f}" if avg_score else "N/A")

                    with col4:
                        model_status = "Loaded" if stats.get("model_loaded") else "Not Loaded"
                        st.metric("Model Status", model_status)

                    st.divider()

                    # Risk level breakdown
                    st.subheader("Predictions by Risk Level")
                    risk_data = stats.get("by_risk_level", {})

                    if risk_data:
                        risk_col1, risk_col2, risk_col3 = st.columns(3)

                        with risk_col1:
                            st.metric("Low Risk", risk_data.get("Low", 0), delta=None)

                        with risk_col2:
                            st.metric("Medium Risk", risk_data.get("Medium", 0), delta=None)

                        with risk_col3:
                            st.metric("High Risk", risk_data.get("High", 0), delta=None)
                    else:
                        st.info("No predictions recorded yet.")

                    st.divider()
                    st.subheader("Raw Data")
                    st.json(stats)
                else:
                    st.error(f"Error: {response.status_code}")

            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to API. Is the backend running?")
            except Exception as e:
                st.error(f"Error: {str(e)}")


# Footer
st.sidebar.divider()
st.sidebar.caption("Cashi Credit Scoring API v1.0")
st.sidebar.caption("Powered by ML + Business Rules")

"""Data preprocessing for Lending Club loan data.

This module handles cleaning, transformation, and feature selection
for credit risk modeling.
"""

import pandas as pd
import numpy as np
from typing import List, Optional, Tuple
from loguru import logger


# COLUMNS WE WANT TO DROP

# 100% missing or empty - completely useless
COLS_EMPTY = [
    "id",
    "member_id",
    "url",
    "desc",
    "hardship_type",
    "hardship_reason",
    "hardship_status",
    "deferral_term",
    "hardship_amount",
    "hardship_start_date",
    "hardship_end_date",
    "payment_plan_start_date",
    "hardship_length",
    "hardship_dpd",
    "hardship_loan_status",
    "orig_projected_additional_accrued_interest",
    "hardship_payoff_balance_amount",
    "hardship_last_payment_amount",
    "debt_settlement_flag_date",
    "settlement_status",
    "settlement_date",
    "settlement_amount",
    "settlement_percentage",
    "settlement_term",
]

# High missing (>50%) - too sparse to be useful
COLS_HIGH_MISSING = [
    "mths_since_last_delinq",
    "mths_since_last_record",
    "mths_since_last_major_derog",
    "annual_inc_joint",
    "dti_joint",
    "verification_status_joint",
    "revol_bal_joint",
    "sec_app_earliest_cr_line",
    "sec_app_inq_last_6mths",
    "sec_app_mort_acc",
    "sec_app_open_acc",
    "sec_app_revol_util",
    "sec_app_open_act_il",
    "sec_app_num_rev_accts",
    "sec_app_chargeoff_within_12_mths",
    "sec_app_collections_12_mths_ex_med",
    "sec_app_mths_since_last_major_derog",
    "mths_since_recent_bc_dlq",
    "mths_since_recent_revol_delinq",
]

# Leakage - post-loan features (data from AFTER loan decision)
COLS_LEAKAGE = [
    "out_prncp",
    "out_prncp_inv",
    "total_pymnt",
    "total_pymnt_inv",
    "total_rec_prncp",
    "total_rec_int",
    "total_rec_late_fee",
    "recoveries",
    "collection_recovery_fee",
    "last_pymnt_d",
    "last_pymnt_amnt",
    "next_pymnt_d",
    "last_credit_pull_d",
    "hardship_flag",
    "debt_settlement_flag",
]

# Zero variance / constant - no predictive value
COLS_ZERO_VARIANCE = [
    "pymnt_plan",
    "policy_code",
    "tax_liens",
    "num_tl_30dpd",
    "num_tl_120dpd_2m",
]

# Redundant / duplicate information
COLS_REDUNDANT = [
    "funded_amnt",      # same as loan_amnt
    "funded_amnt_inv",  # investor-side duplicate
    "sub_grade",        # redundant with grade
    "title",            # same as purpose
]

# Geographic granularity risk - potential discrimination
COLS_DISCRIMINATION_RISK = [
    "zip_code",  # too granular, redlining risk - use addr_state instead
]

# High cardinality free text - not useful as features
COLS_FREE_TEXT = [
    "emp_title",  # 5281+ unique values, needs NLP to use
]

# All columns to drop
COLS_TO_DROP = (
    COLS_EMPTY
    + COLS_HIGH_MISSING
    + COLS_LEAKAGE
    + COLS_ZERO_VARIANCE
    + COLS_REDUNDANT
    + COLS_DISCRIMINATION_RISK
    + COLS_FREE_TEXT
)

# TARGET VARIABLE MAPPING

# Loan statuses that indicate default
DEFAULT_STATUSES = [
    "Charged Off",
    "Default",
    "Late (31-120 days)",
    "Late (16-30 days)",
    "Does not meet the credit policy. Status:Charged Off",
]

# Loan statuses that indicate good standing (non-default)
GOOD_STATUSES = [
    "Fully Paid",
    "Current",
    "Does not meet the credit policy. Status:Fully Paid",
]

# Statuses to exclude (in-progress, ambiguous)
EXCLUDE_STATUSES = [
    "In Grace Period",
    "Issued",
]


# PREPROCESSOR CLASS


class LoanDataPreprocessor:
    """Preprocessor for Lending Club loan data.

    Handles:
    - Column dropping (empty, leakage, redundant, etc.)
    - Target variable creation (default vs non-default)
    - Missing value imputation
    - Data type conversion
    - Feature engineering basics
    """

    def __init__(
        self,
        drop_columns: Optional[List[str]] = None,
        target_column: str = "loan_status",
        create_binary_target: bool = True,
    ):
        """Initialize preprocessor.

        Args:
            drop_columns: Columns to drop. Defaults to COLS_TO_DROP.
            target_column: Name of the target column.
            create_binary_target: Whether to create binary default indicator.
        """
        self.drop_columns = drop_columns or COLS_TO_DROP
        self.target_column = target_column
        self.create_binary_target = create_binary_target
        self._fitted = False
        self._feature_columns: List[str] = []

    def fit(self, df: pd.DataFrame) -> "LoanDataPreprocessor":
        """Fit preprocessor to data (learn feature columns).

        Args:
            df: Input DataFrame.

        Returns:
            Self for method chaining.
        """
        # Identify columns that actually exist in the data
        existing_drop_cols = [c for c in self.drop_columns if c in df.columns]

        # Store feature columns (excluding target and drop columns)
        self._feature_columns = [
            c for c in df.columns
            if c not in existing_drop_cols and c != self.target_column
        ]

        self._fitted = True
        logger.info(f"Fitted preprocessor: {len(self._feature_columns)} features")
        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform data.

        Args:
            df: Input DataFrame.

        Returns:
            Transformed DataFrame.
        """
        if not self._fitted:
            raise ValueError("Preprocessor must be fitted before transform")

        df = df.copy()

        # Drop columns
        cols_to_drop = [c for c in self.drop_columns if c in df.columns]
        df = df.drop(columns=cols_to_drop)
        logger.info(f"Dropped {len(cols_to_drop)} columns")

        # Create binary target
        if self.create_binary_target and self.target_column in df.columns:
            df = self._create_binary_target(df)

        # Handle missing values
        df = self._handle_missing_values(df)

        # Convert data types
        df = self._convert_dtypes(df)

        return df

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fit and transform in one step.

        Args:
            df: Input DataFrame.

        Returns:
            Transformed DataFrame.
        """
        return self.fit(df).transform(df)

    def _create_binary_target(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create binary default indicator from loan_status.

        Args:
            df: Input DataFrame with loan_status column.

        Returns:
            DataFrame with 'default' column added.
        """
        # Filter to only definitive statuses
        valid_statuses = DEFAULT_STATUSES + GOOD_STATUSES
        initial_rows = len(df)
        df = df[df[self.target_column].isin(valid_statuses)].copy()

        # Create binary target: 1 = default, 0 = good standing
        df["default"] = df[self.target_column].isin(DEFAULT_STATUSES).astype(int)

        excluded_rows = initial_rows - len(df)
        if excluded_rows > 0:
            logger.info(f"Excluded {excluded_rows} rows with ambiguous loan status")

        logger.info(
            f"Target distribution - Default: {df['default'].sum()} "
            f"({df['default'].mean()*100:.1f}%), "
            f"Good: {(1-df['default']).sum()} ({(1-df['default'].mean())*100:.1f}%)"
        )

        return df

    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values with appropriate strategies.

        Args:
            df: Input DataFrame.

        Returns:
            DataFrame with missing values handled.
        """
        # Numeric columns: fill with median
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df[col].isna().any():
                median_val = df[col].median()
                df[col] = df[col].fillna(median_val)

        # Categorical columns: fill with mode or 'Unknown'
        categorical_cols = df.select_dtypes(include=["object"]).columns
        for col in categorical_cols:
            if df[col].isna().any():
                mode_val = df[col].mode()
                if len(mode_val) > 0:
                    df[col] = df[col].fillna(mode_val[0])
                else:
                    df[col] = df[col].fillna("Unknown")

        return df

    def _convert_dtypes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert columns to appropriate data types.

        Args:
            df: Input DataFrame.

        Returns:
            DataFrame with converted types.
        """
        # Convert term to numeric (e.g., " 36 months" -> 36)
        if "term" in df.columns:
            df["term"] = df["term"].str.extract(r"(\d+)").astype(float)

        # Convert emp_length to numeric
        if "emp_length" in df.columns:
            emp_length_map = {
                "< 1 year": 0.5,
                "1 year": 1,
                "2 years": 2,
                "3 years": 3,
                "4 years": 4,
                "5 years": 5,
                "6 years": 6,
                "7 years": 7,
                "8 years": 8,
                "9 years": 9,
                "10+ years": 10,
            }
            df["emp_length_numeric"] = df["emp_length"].map(emp_length_map)
            df["emp_length_numeric"] = df["emp_length_numeric"].fillna(0)

        # Convert earliest_cr_line to credit history length (months)
        if "earliest_cr_line" in df.columns and "issue_d" in df.columns:
            try:
                df["earliest_cr_line_dt"] = pd.to_datetime(
                    df["earliest_cr_line"], format="%b-%Y", errors="coerce"
                )
                df["issue_d_dt"] = pd.to_datetime(
                    df["issue_d"], format="%b-%Y", errors="coerce"
                )
                df["credit_history_months"] = (
                    (df["issue_d_dt"] - df["earliest_cr_line_dt"]).dt.days / 30
                ).astype(float)
                df = df.drop(columns=["earliest_cr_line_dt", "issue_d_dt"])
            except Exception as e:
                logger.warning(f"Could not convert credit line dates: {e}")

        return df

    @property
    def feature_columns(self) -> List[str]:
        """Get list of feature columns after preprocessing."""
        return self._feature_columns.copy()



# CONVENIENCE FUNCTIONS

def preprocess_loan_data(
    df: pd.DataFrame,
    drop_columns: Optional[List[str]] = None,
    create_binary_target: bool = True,
) -> Tuple[pd.DataFrame, LoanDataPreprocessor]:
    """Convenience function to preprocess loan data.

    Args:
        df: Raw loan DataFrame.
        drop_columns: Optional custom list of columns to drop.
        create_binary_target: Whether to create binary default indicator.

    Returns:
        Tuple of (preprocessed DataFrame, fitted preprocessor).
    """
    preprocessor = LoanDataPreprocessor(
        drop_columns=drop_columns,
        create_binary_target=create_binary_target,
    )
    df_processed = preprocessor.fit_transform(df)
    return df_processed, preprocessor


def get_columns_to_drop() -> List[str]:
    """Get the default list of columns to drop.

    Returns:
        List of column names to drop.
    """
    return COLS_TO_DROP.copy()


def get_drop_columns_by_category() -> dict:
    """Get columns to drop organized by category.

    Returns:
        Dictionary with category names as keys and column lists as values.
    """
    return {
        "empty_100pct_missing": COLS_EMPTY,
        "high_missing_50pct_plus": COLS_HIGH_MISSING,
        "leakage_post_loan": COLS_LEAKAGE,
        "zero_variance": COLS_ZERO_VARIANCE,
        "redundant": COLS_REDUNDANT,
        "discrimination_risk": COLS_DISCRIMINATION_RISK,
        "free_text_high_cardinality": COLS_FREE_TEXT,
    }

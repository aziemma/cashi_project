"""SQLite database for storing predictions."""

import sqlite3
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "predictions.db"


def init_db():
    """Initialize the database with required tables."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                applicant_id TEXT NOT NULL,
                credit_score INTEGER NOT NULL,
                default_probability REAL NOT NULL,
                risk_level TEXT NOT NULL,
                explanation TEXT,

                -- Input features
                grade_numeric REAL,
                int_rate REAL,
                inq_last_6mths REAL,
                revol_util REAL,
                installment REAL,
                installment_to_income REAL,
                loan_to_income REAL,
                dti REAL,
                open_acc REAL,
                loan_amnt REAL,
                annual_inc REAL,
                credit_history_months REAL,

                -- Metadata
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                request_ip TEXT,
                response_time_ms REAL
            )
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_applicant_id ON predictions(applicant_id)
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at ON predictions(created_at)
        """)

        conn.commit()


@contextmanager
def get_connection():
    """Get database connection context manager."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def save_prediction(
    applicant_id: str,
    credit_score: int,
    default_probability: float,
    risk_level: str,
    explanation: str,
    input_data: dict,
    request_ip: str = None,
    response_time_ms: float = None
):
    """Save a prediction to the database."""
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO predictions (
                applicant_id, credit_score, default_probability, risk_level, explanation,
                grade_numeric, int_rate, inq_last_6mths, revol_util, installment,
                installment_to_income, loan_to_income, dti, open_acc, loan_amnt,
                annual_inc, credit_history_months, request_ip, response_time_ms
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            applicant_id, credit_score, default_probability, risk_level, explanation,
            input_data.get("grade_numeric"),
            input_data.get("int_rate"),
            input_data.get("inq_last_6mths"),
            input_data.get("revol_util"),
            input_data.get("installment"),
            input_data.get("installment_to_income"),
            input_data.get("loan_to_income"),
            input_data.get("dti"),
            input_data.get("open_acc"),
            input_data.get("loan_amnt"),
            input_data.get("annual_inc"),
            input_data.get("credit_history_months"),
            request_ip,
            response_time_ms
        ))
        conn.commit()


def get_predictions_stats():
    """Get statistics about predictions for monitoring."""
    with get_connection() as conn:
        stats = {}

        # Total predictions
        result = conn.execute("SELECT COUNT(*) as count FROM predictions").fetchone()
        stats["total_predictions"] = result["count"]

        # Predictions by risk level
        result = conn.execute("""
            SELECT risk_level, COUNT(*) as count
            FROM predictions
            GROUP BY risk_level
        """).fetchall()
        stats["by_risk_level"] = {row["risk_level"]: row["count"] for row in result}

        # Average score
        result = conn.execute("SELECT AVG(credit_score) as avg_score FROM predictions").fetchone()
        stats["avg_credit_score"] = round(result["avg_score"], 2) if result["avg_score"] else 0

        # Predictions in last 24 hours
        result = conn.execute("""
            SELECT COUNT(*) as count
            FROM predictions
            WHERE created_at > datetime('now', '-1 day')
        """).fetchone()
        stats["last_24h"] = result["count"]

        return stats


# Initialize database on module import
init_db()

# conn = sqlite3.connect('/Users/azi/Downloads/cashi_project/data/predictions.db')
# conn.row_factory = sqlite3.Row
# cursor = conn.execute('SELECT applicant_id, credit_score, risk_level, explanation, created_at FROM predictions')
# for row in cursor:
#     print(dict(row))
# conn.close()

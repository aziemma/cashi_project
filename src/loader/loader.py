"""Data loading utilities for loan data."""

import pandas as pd
from pathlib import Path
from typing import Optional, Union
from loguru import logger


def load_raw_data(
    filepath: Union[str, Path],
    nrows: Optional[int] = None,
    usecols: Optional[list] = None,
) -> pd.DataFrame:
    """Load raw loan data from CSV.

    Args:
        filepath: Path to the CSV file.
        nrows: Optional number of rows to load (for testing/dev).
        usecols: Optional list of columns to load.

    Returns:
        Raw DataFrame.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Data file not found: {filepath}")

    logger.info(f"Loading data from {filepath}")

    df = pd.read_csv(
        filepath,
        nrows=nrows,
        usecols=usecols,
        low_memory=False,
    )

    logger.info(f"Loaded {len(df):,} rows, {len(df.columns)} columns")
    return df


def load_processed_data(
    filepath: Union[str, Path],
) -> pd.DataFrame:
    """Load preprocessed data from parquet or CSV.

    Args:
        filepath: Path to the processed data file.

    Returns:
        Processed DataFrame.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Processed data file not found: {filepath}")

    if filepath.suffix == ".parquet":
        df = pd.read_parquet(filepath)
    else:
        df = pd.read_csv(filepath, low_memory=False)

    logger.info(f"Loaded processed data: {len(df):,} rows, {len(df.columns)} columns")
    return df


def save_processed_data(
    df: pd.DataFrame,
    filepath: Union[str, Path],
    format: str = "parquet",
) -> None:
    """Save processed data to file.

    Args:
        df: DataFrame to save.
        filepath: Output path.
        format: Output format ('parquet' or 'csv').
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    if format == "parquet":
        df.to_parquet(filepath, index=False)
    else:
        df.to_csv(filepath, index=False)

    logger.info(f"Saved processed data to {filepath}")

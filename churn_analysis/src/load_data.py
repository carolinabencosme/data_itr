"""Data loading utilities."""

from pathlib import Path
from typing import Tuple

import pandas as pd


def load_csv_file(file_path: Path) -> pd.DataFrame:
    """Load a CSV file with explicit error handling."""
    if not file_path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    dataframe = pd.read_csv(file_path)
    if dataframe.empty:
        raise ValueError(f"Input file is empty: {file_path}")
    return dataframe


def load_crm_data(crm1_path: Path, crm2_path: Path) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load CRM enrollment and status datasets."""
    crm_enrollment_df = load_csv_file(crm1_path)
    crm_status_df = load_csv_file(crm2_path)
    return crm_enrollment_df, crm_status_df

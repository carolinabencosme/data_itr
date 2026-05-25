"""Data cleaning and standardization utilities."""

from typing import Dict, Sequence, Tuple

import pandas as pd


def clean_string_value(value: object) -> object:
    """Trim strings and normalize empty values to NA."""
    if pd.isna(value):
        return pd.NA
    if isinstance(value, str):
        stripped = value.strip()
        return stripped if stripped else pd.NA
    return value


def clean_currency_to_numeric(series: pd.Series) -> pd.Series:
    """Convert currency-like strings to numeric values."""
    as_text = series.astype("string").str.strip()
    cleaned = (
        as_text.str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .replace({"": pd.NA, "nan": pd.NA, "None": pd.NA, "null": pd.NA})
    )
    return pd.to_numeric(cleaned, errors="coerce")


def parse_date_columns(
    dataframe: pd.DataFrame, date_columns: Sequence[str]
) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """Parse date columns and return invalid counts by column."""
    cleaned_df = dataframe.copy()
    invalid_counts: Dict[str, int] = {}

    for column in date_columns:
        if column not in cleaned_df.columns:
            continue
        raw_text = cleaned_df[column].astype("string").str.strip()
        non_empty_mask = raw_text.notna() & raw_text.ne("")
        cleaned_df[column] = pd.to_datetime(raw_text, errors="coerce")
        invalid_counts[column] = int((cleaned_df[column].isna() & non_empty_mask).sum())

    return cleaned_df, invalid_counts


def clean_numeric_columns(dataframe: pd.DataFrame, numeric_columns: Sequence[str]) -> pd.DataFrame:
    """Clean and convert selected numeric columns."""
    cleaned_df = dataframe.copy()
    for column in numeric_columns:
        if column in cleaned_df.columns:
            cleaned_df[column] = clean_currency_to_numeric(cleaned_df[column])
    return cleaned_df


def clean_string_columns(dataframe: pd.DataFrame, columns: Sequence[str]) -> pd.DataFrame:
    """Apply string cleanup to selected columns."""
    cleaned_df = dataframe.copy()
    for column in columns:
        if column in cleaned_df.columns:
            cleaned_df[column] = cleaned_df[column].apply(clean_string_value)
    return cleaned_df

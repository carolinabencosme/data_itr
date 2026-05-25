"""Validation logic for schema and data quality checks."""

from typing import Dict, List, Sequence, Tuple

import pandas as pd


def validate_required_columns(
    dataframe: pd.DataFrame, required_columns: Sequence[str], dataset_name: str
) -> List[str]:
    """Validate required columns and raise an error if any are missing."""
    missing_columns = [column for column in required_columns if column not in dataframe.columns]
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise ValueError(f"{dataset_name} missing required columns: {missing}")
    return missing_columns


def get_duplicate_rows(dataframe: pd.DataFrame, key_column: str) -> pd.DataFrame:
    """Return duplicate rows based on the key column."""
    return dataframe[dataframe.duplicated(subset=[key_column], keep=False)].copy()


def get_unmatched_ids(
    left_df: pd.DataFrame, right_df: pd.DataFrame, key_column: str
) -> Tuple[pd.Series, pd.Series]:
    """Find IDs present in one dataframe and missing in the other."""
    left_ids = set(left_df[key_column].dropna().astype(str))
    right_ids = set(right_df[key_column].dropna().astype(str))
    only_left = pd.Series(sorted(left_ids - right_ids), name=f"{key_column}_only_in_left")
    only_right = pd.Series(sorted(right_ids - left_ids), name=f"{key_column}_only_in_right")
    return only_left, only_right


def count_nulls(dataframe: pd.DataFrame, columns: Sequence[str]) -> Dict[str, int]:
    """Count nulls for selected columns."""
    return {column: int(dataframe[column].isna().sum()) for column in columns if column in dataframe.columns}


def count_invalid_dates(dataframe: pd.DataFrame, date_columns: Sequence[str]) -> Dict[str, int]:
    """
    Count invalid date values by comparing non-empty raw values with parsed datetime values.
    Requires date columns to be parsed as datetime before use.
    """
    invalid_counts: Dict[str, int] = {}
    for column in date_columns:
        if column not in dataframe.columns:
            continue
        parsed = dataframe[column]
        raw_as_text = dataframe[column].astype("string")
        raw_non_empty = raw_as_text.notna() & raw_as_text.str.strip().ne("")
        invalid_counts[column] = int((parsed.isna() & raw_non_empty).sum())
    return invalid_counts


def build_data_quality_snapshot(
    crm_enrollment_df: pd.DataFrame,
    crm_status_df: pd.DataFrame,
    merged_clients_df: pd.DataFrame,
    join_key: str,
    critical_columns_crm1: Sequence[str],
    critical_columns_crm2: Sequence[str],
) -> Dict[str, object]:
    """Build a consolidated quality snapshot used in reporting."""
    crm1_duplicates = get_duplicate_rows(crm_enrollment_df, join_key)
    crm2_duplicates = get_duplicate_rows(crm_status_df, join_key)
    only_crm1_ids, only_crm2_ids = get_unmatched_ids(crm_enrollment_df, crm_status_df, join_key)

    snapshot = {
        "rows_crm1": int(len(crm_enrollment_df)),
        "rows_crm2": int(len(crm_status_df)),
        "rows_after_join": int(len(merged_clients_df)),
        "crm1_duplicate_count": int(len(crm1_duplicates)),
        "crm2_duplicate_count": int(len(crm2_duplicates)),
        "crm1_duplicate_ids": sorted(crm1_duplicates[join_key].astype(str).unique().tolist()),
        "crm2_duplicate_ids": sorted(crm2_duplicates[join_key].astype(str).unique().tolist()),
        "crm1_ids_without_match_in_crm2_count": int(len(only_crm1_ids)),
        "crm2_ids_without_match_in_crm1_count": int(len(only_crm2_ids)),
        "crm1_ids_without_match_in_crm2_sample": only_crm1_ids.head(20).tolist(),
        "crm2_ids_without_match_in_crm1_sample": only_crm2_ids.head(20).tolist(),
        "crm1_nulls_critical": count_nulls(crm_enrollment_df, critical_columns_crm1),
        "crm2_nulls_critical": count_nulls(crm_status_df, critical_columns_crm2),
    }
    return snapshot

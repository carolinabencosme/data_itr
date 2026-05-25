"""Business transformations for churn analysis."""

from typing import Iterable, Sequence

import numpy as np
import pandas as pd

from config import (
    CHURN_STATUS,
    INVOICE_BUCKETS,
    INVOICE_MISSING_LABEL,
    SERVICE_COLS_2_3,
    SERVICE_COLS_3_6,
    SERVICE_COLS_4_6,
)


def merge_crm_data(
    crm_enrollment_df: pd.DataFrame, crm_status_df: pd.DataFrame, join_key: str
) -> pd.DataFrame:
    """Merge CRM data using an inner join on the business key."""
    merged_clients_df = pd.merge(
        crm_enrollment_df,
        crm_status_df,
        on=join_key,
        how="inner",
        suffixes=("_crm1", "_crm2"),
    )
    return merged_clients_df


def calculate_ratio(numerator: float, denominator: float) -> float:
    """Safely calculate ratio."""
    if denominator == 0:
        return 0.0
    return float(numerator / denominator)


def percentage_of_total(series: pd.Series) -> pd.Series:
    """Return percentages over total for a numeric series."""
    total_value = series.sum()
    if total_value == 0:
        return pd.Series([0.0] * len(series), index=series.index)
    return (series / total_value) * 100


def contains_token(row: pd.Series, columns: Iterable[str], token: str) -> bool:
    """Check if any selected columns contain a token (case-insensitive)."""
    token_lower = token.lower()
    for column in columns:
        value = row.get(column, pd.NA)
        if pd.isna(value):
            continue
        if token_lower in str(value).lower():
            return True
    return False


def classify_core_service(row: pd.Series) -> str:
    """
    Classify core service type with strict first-match priority.
    Priority: Hardship > Fresh Start > Tax Prep Only > Other/Unknown.
    """
    if contains_token(row, SERVICE_COLS_4_6, "hardship"):
        return "Hardship"
    if contains_token(row, SERVICE_COLS_3_6, "fresh start"):
        return "Fresh Start"

    file_in_2_3 = contains_token(row, SERVICE_COLS_2_3, "file")
    file_in_4_6 = contains_token(row, SERVICE_COLS_4_6, "file")
    if file_in_2_3 and not file_in_4_6:
        return "Tax Prep Only"
    return "Other/Unknown"


def assign_invoice_bucket(invoice_amount: object) -> str:
    """Assign invoice bucket using required thresholds."""
    if pd.isna(invoice_amount) or float(invoice_amount) <= 0:
        return INVOICE_MISSING_LABEL

    value = float(invoice_amount)
    for lower, upper, label in INVOICE_BUCKETS:
        if lower <= value <= upper:
            return label
    return INVOICE_MISSING_LABEL


def enrich_business_columns(merged_clients_df: pd.DataFrame) -> pd.DataFrame:
    """Add churn, revenue, activation, timing and service classification features."""
    enriched_df = merged_clients_df.copy()

    enriched_df["is_churned"] = enriched_df["Status"].eq(CHURN_STATUS)
    enriched_df["churn_revenue"] = np.where(
        enriched_df["is_churned"],
        enriched_df["Net Net Resolution Costs"].fillna(0.0),
        0.0,
    )
    enriched_df["effective_activation_date"] = enriched_df["Activation_Date__c"].combine_first(
        enriched_df["Pre_Activation_Date__c"]
    )
    enriched_df["core_service_type"] = enriched_df.apply(classify_core_service, axis=1)

    agreement_date = enriched_df["2nd Trade Received Agreement Date"]
    close_date = enriched_df["ITR_Close_Date"]
    first_payment = enriched_df["Clients first payment date"]

    enriched_df["days_from_agreement_to_close"] = (close_date - agreement_date).dt.days
    enriched_df["months_from_agreement_to_close"] = enriched_df["days_from_agreement_to_close"] / 30.4375
    enriched_df["days_from_first_payment_to_close"] = (close_date - first_payment).dt.days
    enriched_df["months_from_first_payment_to_close"] = (
        enriched_df["days_from_first_payment_to_close"] / 30.4375
    )

    enriched_df["invoice_bucket"] = enriched_df["Net Net Resolution Costs"].apply(assign_invoice_bucket)
    return enriched_df


def format_percent(value: float) -> str:
    """Format percentage with two decimals."""
    return f"{value:.2f}%"


def format_currency(value: float) -> str:
    """Format currency as USD."""
    return f"${value:,.2f}"

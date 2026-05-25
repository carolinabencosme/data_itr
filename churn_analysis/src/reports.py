"""Report builders for churn analysis outputs."""

from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

from config import INVOICE_MISSING_LABEL, S1_BUCKET_LABELS
from transformations import calculate_ratio, percentage_of_total


def _safe_sum(series: pd.Series) -> float:
    return float(series.fillna(0).sum())


def _time_bucket_from_days(days_value: object) -> str:
    if pd.isna(days_value):
        return "Insufficient Date Data"
    value = float(days_value)
    if value < 0:
        return "Insufficient Date Data"
    if value <= 30:
        return "0-30 days"
    if value <= 60:
        return "31-60 days"
    if value <= 90:
        return "61-90 days"
    if value <= 180:
        return "91-180 days"
    if value <= 365:
        return "181-365 days"
    return ">365 days"


def build_report_s1_churn_timing(churned_clients_df: pd.DataFrame) -> Tuple[pd.DataFrame, str, Dict[str, float]]:
    """Build S1 churn timing report."""
    report_df = churned_clients_df.copy()
    report_df["timing_bucket"] = report_df["days_from_agreement_to_close"].apply(_time_bucket_from_days)

    grouped = (
        report_df.groupby("timing_bucket", dropna=False)
        .agg(
            churned_clients=("is_churned", "size"),
            churn_revenue=("churn_revenue", "sum"),
        )
        .reset_index()
    )
    grouped["pct_total_churn_clients"] = percentage_of_total(grouped["churned_clients"]).round(4)
    grouped["pct_total_churn_revenue"] = percentage_of_total(grouped["churn_revenue"]).round(4)

    category_order = pd.Categorical(grouped["timing_bucket"], categories=S1_BUCKET_LABELS, ordered=True)
    grouped = grouped.assign(_order=category_order).sort_values("_order").drop(columns="_order")

    mean_days = float(report_df["days_from_agreement_to_close"].mean())
    median_days = float(report_df["days_from_agreement_to_close"].median())
    mean_months = float(report_df["months_from_agreement_to_close"].mean())
    median_months = float(report_df["months_from_agreement_to_close"].median())
    mean_days_from_fp = float(report_df["days_from_first_payment_to_close"].mean())
    median_days_from_fp = float(report_df["days_from_first_payment_to_close"].median())

    stats_rows = pd.DataFrame(
        [
            {"timing_bucket": "STAT_MEAN_DAYS_AGREEMENT_TO_CHURN", "churned_clients": mean_days},
            {"timing_bucket": "STAT_MEDIAN_DAYS_AGREEMENT_TO_CHURN", "churned_clients": median_days},
            {"timing_bucket": "STAT_MEAN_MONTHS_AGREEMENT_TO_CHURN", "churned_clients": mean_months},
            {"timing_bucket": "STAT_MEDIAN_MONTHS_AGREEMENT_TO_CHURN", "churned_clients": median_months},
            {"timing_bucket": "STAT_MEAN_DAYS_FIRST_PAYMENT_TO_CHURN", "churned_clients": mean_days_from_fp},
            {"timing_bucket": "STAT_MEDIAN_DAYS_FIRST_PAYMENT_TO_CHURN", "churned_clients": median_days_from_fp},
        ]
    )
    report_output = pd.concat([grouped, stats_rows], ignore_index=True, sort=False)

    top_bucket = grouped.sort_values("churned_clients", ascending=False).head(1)
    top_bucket_name = top_bucket["timing_bucket"].iloc[0] if not top_bucket.empty else "N/A"
    top_bucket_pct = top_bucket["pct_total_churn_clients"].iloc[0] if not top_bucket.empty else 0.0
    interpretation = (
        f"El churn se concentra más en el bucket {top_bucket_name} ({top_bucket_pct:.2f}% de churned clients). "
        f"El tiempo promedio desde acuerdo a churn es {mean_days:.1f} días y la mediana {median_days:.1f} días. "
        "Esto ayuda a identificar si la fricción ocurre temprano o tardío en el ciclo del cliente."
    )

    metrics = {
        "mean_days_agreement_to_churn": mean_days,
        "median_days_agreement_to_churn": median_days,
        "mean_months_agreement_to_churn": mean_months,
        "median_months_agreement_to_churn": median_months,
    }
    return report_output, interpretation, metrics


def build_report_s2_activation_timing(churned_clients_df: pd.DataFrame) -> Tuple[pd.DataFrame, str, Dict[str, float]]:
    """Build S2 churn before/after activation report."""
    report_df = churned_clients_df.copy()

    conditions = [
        report_df["ITR_Close_Date"].isna(),
        report_df["effective_activation_date"].isna(),
        report_df["ITR_Close_Date"] < report_df["effective_activation_date"],
    ]
    labels = [
        "Missing Close Date",
        "No Activation Date Available",
        "Before Activation",
    ]
    report_df["activation_timing_category"] = np.select(conditions, labels, default="After Activation")

    grouped = (
        report_df.groupby("activation_timing_category", dropna=False)
        .agg(
            churned_clients=("is_churned", "size"),
            churn_revenue=("churn_revenue", "sum"),
        )
        .reset_index()
    )
    grouped["pct_total_churn_clients"] = percentage_of_total(grouped["churned_clients"]).round(4)
    grouped["pct_total_churn_revenue"] = percentage_of_total(grouped["churn_revenue"]).round(4)

    ordered_labels = [
        "Before Activation",
        "After Activation",
        "No Activation Date Available",
        "Missing Close Date",
    ]
    grouped["activation_timing_category"] = pd.Categorical(
        grouped["activation_timing_category"],
        categories=ordered_labels,
        ordered=True,
    )
    grouped = grouped.sort_values("activation_timing_category").reset_index(drop=True)

    before_share = float(
        grouped.loc[grouped["activation_timing_category"] == "Before Activation", "pct_total_churn_clients"].sum()
    )
    after_share = float(
        grouped.loc[grouped["activation_timing_category"] == "After Activation", "pct_total_churn_clients"].sum()
    )
    interpretation = (
        f"El churn before activation representa {before_share:.2f}% de churned clients, "
        f"mientras after activation representa {after_share:.2f}%. "
        "Una proporción alta before activation sugiere fricción de onboarding/expectativas; "
        "una proporción alta after activation sugiere posible problema de ejecución del servicio."
    )

    metrics = {
        "before_activation_pct_clients": before_share,
        "after_activation_pct_clients": after_share,
    }
    return grouped, interpretation, metrics


def build_report_s3_financing_lender_churn(
    merged_clients_df: pd.DataFrame, churned_clients_df: pd.DataFrame
) -> Tuple[pd.DataFrame, str, Dict[str, float]]:
    """Build S3 possflip/financing lender churn report."""
    with_lender_all = merged_clients_df[merged_clients_df["Financing Lender Used"].notna()].copy()
    with_lender_churned = churned_clients_df[churned_clients_df["Financing Lender Used"].notna()].copy()

    total_churned_clients = int(len(churned_clients_df))
    total_churned_revenue = _safe_sum(churned_clients_df["churn_revenue"])

    total_by_lender = (
        with_lender_all.groupby("Financing Lender Used").size().rename("total_clients").reset_index()
    )
    churn_by_lender = (
        with_lender_churned.groupby("Financing Lender Used")
        .agg(churned_quantity=("is_churned", "size"), churn_revenue=("churn_revenue", "sum"))
        .reset_index()
    )

    lender_report = total_by_lender.merge(churn_by_lender, on="Financing Lender Used", how="left")
    lender_report["churned_quantity"] = lender_report["churned_quantity"].fillna(0).astype(int)
    lender_report["churn_revenue"] = lender_report["churn_revenue"].fillna(0.0)
    lender_report["churn_rate"] = (
        lender_report["churned_quantity"] / lender_report["total_clients"].replace(0, np.nan)
    ).fillna(0.0)
    lender_report["pct_total_churn_quantity"] = (
        lender_report["churned_quantity"] / max(total_churned_clients, 1)
    )
    lender_report["pct_total_churn_revenue"] = lender_report["churn_revenue"] / max(total_churned_revenue, 1e-9)

    lender_report = lender_report.sort_values("churned_quantity", ascending=False).reset_index(drop=True)

    possflip_churn_dollars = _safe_sum(with_lender_churned["churn_revenue"])
    summary_rows = pd.DataFrame(
        [
            {
                "Financing Lender Used": "TOTAL_POSSFLIP_CHURN_DOLLARS",
                "total_clients": np.nan,
                "churned_quantity": np.nan,
                "churn_rate": np.nan,
                "pct_total_churn_quantity": np.nan,
                "churn_revenue": possflip_churn_dollars,
                "pct_total_churn_revenue": calculate_ratio(possflip_churn_dollars, total_churned_revenue),
            },
            {
                "Financing Lender Used": "GRAND_TOTAL",
                "total_clients": int(len(with_lender_all)),
                "churned_quantity": int(len(with_lender_churned)),
                "churn_rate": calculate_ratio(len(with_lender_churned), len(with_lender_all)),
                "pct_total_churn_quantity": calculate_ratio(len(with_lender_churned), total_churned_clients),
                "churn_revenue": possflip_churn_dollars,
                "pct_total_churn_revenue": calculate_ratio(possflip_churn_dollars, total_churned_revenue),
            },
        ]
    )
    report_output = pd.concat([lender_report, summary_rows], ignore_index=True, sort=False)

    interpretation = (
        f"El churn de clientes con lender (possflip churn) suma ${possflip_churn_dollars:,.2f}. "
        "El breakdown por lender permite separar si el riesgo está concentrado en pocos originadores o distribuido. "
        "Este reporte debe leerse junto al volumen total por lender para evitar sobre-interpretar tasas en bases pequeñas."
    )
    metrics = {
        "possflip_churn_dollars": possflip_churn_dollars,
        "possflip_churn_pct_revenue": calculate_ratio(possflip_churn_dollars, total_churned_revenue),
    }
    return report_output, interpretation, metrics


def _remove_income_outliers_iqr(
    dataframe: pd.DataFrame, income_column: str
) -> Tuple[pd.DataFrame, Dict[str, float]]:
    valid_income = dataframe[dataframe[income_column].notna()].copy()
    if valid_income.empty:
        return valid_income, {"q1": np.nan, "q3": np.nan, "lower_bound": np.nan, "upper_bound": np.nan}

    q1 = valid_income[income_column].quantile(0.25)
    q3 = valid_income[income_column].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    filtered_df = valid_income[
        (valid_income[income_column] >= lower_bound) & (valid_income[income_column] <= upper_bound)
    ].copy()
    return filtered_df, {
        "q1": float(q1),
        "q3": float(q3),
        "lower_bound": float(lower_bound),
        "upper_bound": float(upper_bound),
    }


def build_report_a1_income_churn_vs_active(
    merged_clients_df: pd.DataFrame,
) -> Tuple[pd.DataFrame, str, Dict[str, float]]:
    """Build A1 income comparison report with IQR outlier removal."""
    income_column = "Approximate Gross Monthly household income"
    pre_valid = merged_clients_df[merged_clients_df[income_column].notna()].copy()
    filtered_df, iqr_info = _remove_income_outliers_iqr(merged_clients_df, income_column)

    summary = (
        filtered_df.assign(churn_group=np.where(filtered_df["is_churned"], "Churned", "Active / Non-Churned"))
        .groupby("churn_group")
        .agg(
            count=("ITR Id", "size"),
            average_income=(income_column, "mean"),
            median_income=(income_column, "median"),
            min_income=(income_column, "min"),
            max_income=(income_column, "max"),
        )
        .reset_index()
    )

    pre_counts = (
        pre_valid.assign(churn_group=np.where(pre_valid["is_churned"], "Churned", "Active / Non-Churned"))
        .groupby("churn_group")
        .size()
        .rename("count_before_outlier_removal")
        .reset_index()
    )
    summary = summary.merge(pre_counts, on="churn_group", how="left")
    summary["outliers_removed"] = summary["count_before_outlier_removal"] - summary["count"]
    summary["pct_removed"] = (
        summary["outliers_removed"] / summary["count_before_outlier_removal"].replace(0, np.nan)
    ).fillna(0.0)

    interpretation = (
        "La comparación de income se hizo excluyendo outliers con método IQR para evitar sesgo por extremos. "
        "Diferencias de mediana entre churned y active/non-churned sugieren posible desalineación de avatar financiero, "
        "pero deben interpretarse junto a mix de servicio y lead source."
    )

    metrics = {
        "iqr_lower_bound": iqr_info["lower_bound"],
        "iqr_upper_bound": iqr_info["upper_bound"],
        "total_rows_with_valid_income": float(len(pre_valid)),
        "total_rows_after_outlier_removal": float(len(filtered_df)),
    }
    return summary, interpretation, metrics


def _build_group_churn_table(
    merged_clients_df: pd.DataFrame, group_column: str, sort_by: List[str]
) -> pd.DataFrame:
    total_churned_clients = int(merged_clients_df["is_churned"].sum())
    total_churned_revenue = _safe_sum(merged_clients_df["churn_revenue"])

    grouped_total = merged_clients_df.groupby(group_column).size().rename("total_clients").reset_index()
    grouped_churn = (
        merged_clients_df[merged_clients_df["is_churned"]]
        .groupby(group_column)
        .agg(churned_quantity=("is_churned", "size"), churn_revenue=("churn_revenue", "sum"))
        .reset_index()
    )
    report_df = grouped_total.merge(grouped_churn, on=group_column, how="left")
    report_df["churned_quantity"] = report_df["churned_quantity"].fillna(0).astype(int)
    report_df["churn_revenue"] = report_df["churn_revenue"].fillna(0.0)
    report_df["churn_rate"] = (
        report_df["churned_quantity"] / report_df["total_clients"].replace(0, np.nan)
    ).fillna(0.0)
    report_df["pct_total_churn_quantity"] = report_df["churned_quantity"] / max(total_churned_clients, 1)
    report_df["pct_total_churn_revenue"] = report_df["churn_revenue"] / max(total_churned_revenue, 1e-9)

    report_df = report_df.sort_values(sort_by, ascending=[False for _ in sort_by]).reset_index(drop=True)
    return report_df


def build_report_a2_churn_by_core_service_type(
    merged_clients_df: pd.DataFrame,
) -> Tuple[pd.DataFrame, str, Dict[str, float]]:
    """Build A2 report by core service type."""
    report_df = _build_group_churn_table(merged_clients_df, "core_service_type", ["churned_quantity", "churn_revenue"])
    expected_categories = ["Hardship", "Fresh Start", "Tax Prep Only", "Other/Unknown"]
    for category in expected_categories:
        if category not in report_df["core_service_type"].values:
            report_df.loc[len(report_df)] = {
                "core_service_type": category,
                "total_clients": 0,
                "churned_quantity": 0,
                "churn_revenue": 0.0,
                "churn_rate": 0.0,
                "pct_total_churn_quantity": 0.0,
                "pct_total_churn_revenue": 0.0,
            }
    report_df["core_service_type"] = pd.Categorical(
        report_df["core_service_type"], categories=expected_categories, ordered=True
    )
    report_df = report_df.sort_values("core_service_type").reset_index(drop=True)

    interpretation = (
        "Este corte muestra si el churn está más concentrado por tipo de servicio entregado. "
        "Si una categoría combina alto volumen y alta churn rate, se vuelve candidata prioritaria para investigación operativa."
    )
    metrics = {
        "service_category_count": float(len(report_df)),
    }
    return report_df, interpretation, metrics


def build_report_a3_churn_by_lead_source(
    merged_clients_df: pd.DataFrame,
) -> Tuple[pd.DataFrame, str, Dict[str, float]]:
    """Build A3 report by lead source."""
    report_df = _build_group_churn_table(merged_clients_df, "Lead Source", ["churned_quantity", "churn_revenue"])
    interpretation = (
        "Lead sources con alto churn volume o churn revenue deben revisarse en targeting y expectativa comercial. "
        "Nota: fuentes con pocos clientes pueden mostrar churn rates inestables, por lo que la lectura debe ponderar volumen."
    )
    metrics = {
        "lead_sources_count": float(len(report_df)),
    }
    return report_df, interpretation, metrics


def build_report_a4_churn_by_invoice_size(
    merged_clients_df: pd.DataFrame,
) -> Tuple[pd.DataFrame, str, Dict[str, float]]:
    """Build A4 report by invoice bucket."""
    report_df = _build_group_churn_table(merged_clients_df, "invoice_bucket", ["churned_quantity", "churn_revenue"])
    ordered_buckets = [
        "> $29,950",
        "$19,950 - $29,949",
        "$14,950 - $19,949",
        "$9,950 - $14,949",
        "$4,000 - $9,949",
        "$1 - $3,999",
        INVOICE_MISSING_LABEL,
    ]
    report_df["invoice_bucket"] = pd.Categorical(report_df["invoice_bucket"], categories=ordered_buckets, ordered=True)
    report_df = report_df.sort_values("invoice_bucket").reset_index(drop=True)

    interpretation = (
        "Este reporte permite ver si el churn está concentrado en tickets bajos, medios o altos. "
        "Combinar churn rate con participación del churn revenue evita sesgo por solo volumen de clientes."
    )
    metrics = {
        "invoice_bucket_count": float(len(report_df)),
    }
    return report_df, interpretation, metrics


def build_all_reports(merged_clients_df: pd.DataFrame) -> Dict[str, Dict[str, object]]:
    """Build all requested reports and return payload with tables, interpretations and metrics."""
    churned_clients_df = merged_clients_df[merged_clients_df["is_churned"]].copy()

    s1_df, s1_text, s1_metrics = build_report_s1_churn_timing(churned_clients_df)
    s2_df, s2_text, s2_metrics = build_report_s2_activation_timing(churned_clients_df)
    s3_df, s3_text, s3_metrics = build_report_s3_financing_lender_churn(merged_clients_df, churned_clients_df)
    a1_df, a1_text, a1_metrics = build_report_a1_income_churn_vs_active(merged_clients_df)
    a2_df, a2_text, a2_metrics = build_report_a2_churn_by_core_service_type(merged_clients_df)
    a3_df, a3_text, a3_metrics = build_report_a3_churn_by_lead_source(merged_clients_df)
    a4_df, a4_text, a4_metrics = build_report_a4_churn_by_invoice_size(merged_clients_df)

    return {
        "S1": {"table": s1_df, "interpretation": s1_text, "metrics": s1_metrics},
        "S2": {"table": s2_df, "interpretation": s2_text, "metrics": s2_metrics},
        "S3": {"table": s3_df, "interpretation": s3_text, "metrics": s3_metrics},
        "A1": {"table": a1_df, "interpretation": a1_text, "metrics": a1_metrics},
        "A2": {"table": a2_df, "interpretation": a2_text, "metrics": a2_metrics},
        "A3": {"table": a3_df, "interpretation": a3_text, "metrics": a3_metrics},
        "A4": {"table": a4_df, "interpretation": a4_text, "metrics": a4_metrics},
    }

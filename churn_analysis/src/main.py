"""Entry point for churn analysis pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

from clean_data import clean_numeric_columns, clean_string_columns, parse_date_columns
from config import (
    CRM1_PATH,
    CRM1_REQUIRED_COLUMNS,
    CRM2_PATH,
    CRM2_REQUIRED_COLUMNS,
    DATE_COLUMNS_CRM1,
    DATE_COLUMNS_CRM2,
    JOIN_KEY,
    NUMERIC_COLUMNS_CRM1,
    OUTPUT_DIR,
)
from export import (
    ensure_output_directory,
    export_excel_workbook,
    export_report_tables,
    write_data_quality_report,
    write_executive_summary,
    write_report_interpretations,
)
from load_data import load_crm_data
from reports import build_all_reports
from transformations import merge_crm_data, enrich_business_columns
from validation import build_data_quality_snapshot, validate_required_columns


def _prepare_data():
    crm_enrollment_raw_df, crm_status_raw_df = load_crm_data(CRM1_PATH, CRM2_PATH)

    validate_required_columns(crm_enrollment_raw_df, CRM1_REQUIRED_COLUMNS, "CRM 1")
    validate_required_columns(crm_status_raw_df, CRM2_REQUIRED_COLUMNS, "CRM 2")

    crm_enrollment_df = clean_string_columns(crm_enrollment_raw_df, CRM1_REQUIRED_COLUMNS)
    crm_status_df = clean_string_columns(crm_status_raw_df, CRM2_REQUIRED_COLUMNS)

    crm_enrollment_df[JOIN_KEY] = crm_enrollment_df[JOIN_KEY].astype("string")
    crm_status_df[JOIN_KEY] = crm_status_df[JOIN_KEY].astype("string")

    crm_enrollment_df = clean_numeric_columns(crm_enrollment_df, NUMERIC_COLUMNS_CRM1)
    crm_enrollment_df, invalid_dates_crm1 = parse_date_columns(crm_enrollment_df, DATE_COLUMNS_CRM1)
    crm_status_df, invalid_dates_crm2 = parse_date_columns(crm_status_df, DATE_COLUMNS_CRM2)

    invalid_date_counts: Dict[str, int] = {**invalid_dates_crm1, **invalid_dates_crm2}
    return crm_enrollment_df, crm_status_df, invalid_date_counts


def run_pipeline(output_dir: Path = OUTPUT_DIR) -> None:
    """Run the complete churn analysis pipeline."""
    ensure_output_directory(output_dir)

    crm_enrollment_df, crm_status_df, invalid_date_counts = _prepare_data()
    merged_clients_df = merge_crm_data(crm_enrollment_df, crm_status_df, JOIN_KEY)
    merged_clients_df = enrich_business_columns(merged_clients_df)

    quality_snapshot = build_data_quality_snapshot(
        crm_enrollment_df=crm_enrollment_df,
        crm_status_df=crm_status_df,
        merged_clients_df=merged_clients_df,
        join_key=JOIN_KEY,
        critical_columns_crm1=CRM1_REQUIRED_COLUMNS,
        critical_columns_crm2=CRM2_REQUIRED_COLUMNS,
    )

    reports_payload = build_all_reports(merged_clients_df)

    csv_paths = export_report_tables(reports_payload, output_dir)

    cleaning_decisions = [
        "Fechas parseadas con pd.to_datetime(errors='coerce').",
        "Valores numéricos limpiados removiendo '$', comas y espacios; conversion con to_numeric(errors='coerce').",
        "Definición de churn estricta aplicada: Status == 'Case Completed Failed'.",
        "effective_activation_date usa Activation_Date__c con fallback a Pre_Activation_Date__c.",
        "A1 removió outliers de income con método IQR.",
        "Duplicados y IDs sin match se reportan, no se eliminan silenciosamente.",
    ]
    data_quality_path = write_data_quality_report(
        output_dir=output_dir,
        quality_snapshot=quality_snapshot,
        invalid_date_counts=invalid_date_counts,
        cleaning_decisions=cleaning_decisions,
    )

    total_clients = int(len(merged_clients_df))
    total_churned = int(merged_clients_df["is_churned"].sum())
    overall_churn_rate = (total_churned / total_clients) if total_clients else 0.0
    total_churn_revenue = float(merged_clients_df["churn_revenue"].sum())

    overall_metrics = {
        "total_clients": total_clients,
        "total_churned": total_churned,
        "overall_churn_rate": overall_churn_rate,
        "total_churn_revenue": total_churn_revenue,
    }
    executive_summary_path = write_executive_summary(output_dir, overall_metrics, reports_payload)
    interpretations_path = write_report_interpretations(output_dir, reports_payload)
    workbook_path = export_excel_workbook(output_dir, reports_payload, executive_summary_path, data_quality_path)

    print("=== Churn Analysis Pipeline Completed ===")
    print(f"CRM 1 rows loaded: {len(crm_enrollment_df)}")
    print(f"CRM 2 rows loaded: {len(crm_status_df)}")
    print(f"Total clients after join: {total_clients}")
    print(f"Total churned clients: {total_churned}")
    print(f"Overall churn rate: {overall_churn_rate:.2%}")
    print(f"Outputs directory: {output_dir.resolve()}")
    print(f"CSV reports generated: {len(csv_paths)}")
    print(f"Executive summary: {executive_summary_path.resolve()}")
    print(f"Data quality report: {data_quality_path.resolve()}")
    print(f"Report interpretations: {interpretations_path.resolve()}")
    print(f"Excel workbook: {workbook_path.resolve()}")


if __name__ == "__main__":
    run_pipeline()

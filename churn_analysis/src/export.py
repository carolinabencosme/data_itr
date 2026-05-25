"""Export utilities for churn analysis outputs."""

from pathlib import Path
from typing import Dict, List

import pandas as pd

from config import OUTPUT_FILES


def ensure_output_directory(output_dir: Path) -> None:
    """Create output directory if needed."""
    output_dir.mkdir(parents=True, exist_ok=True)


def export_report_tables(report_payload: Dict[str, Dict[str, object]], output_dir: Path) -> Dict[str, Path]:
    """Export report dataframes to CSV files."""
    exported_paths: Dict[str, Path] = {}
    for report_key in ["S1", "S2", "S3", "A1", "A2", "A3", "A4"]:
        output_name = OUTPUT_FILES[report_key]
        output_path = output_dir / output_name
        report_payload[report_key]["table"].to_csv(output_path, index=False)
        exported_paths[report_key] = output_path
    return exported_paths


def write_data_quality_report(
    output_dir: Path,
    quality_snapshot: Dict[str, object],
    invalid_date_counts: Dict[str, int],
    cleaning_decisions: List[str],
) -> Path:
    """Write markdown data quality report."""
    path = output_dir / OUTPUT_FILES["DATA_QUALITY"]
    content = [
        "# Data Quality Report",
        "",
        "## Row Counts",
        f"- CRM 1 rows: {quality_snapshot['rows_crm1']}",
        f"- CRM 2 rows: {quality_snapshot['rows_crm2']}",
        f"- Rows after join: {quality_snapshot['rows_after_join']}",
        "",
        "## Duplicates by `ITR Id`",
        f"- CRM 1 duplicate rows: {quality_snapshot['crm1_duplicate_count']}",
        f"- CRM 2 duplicate rows: {quality_snapshot['crm2_duplicate_count']}",
        f"- CRM 1 duplicate IDs sample: {quality_snapshot['crm1_duplicate_ids'][:20]}",
        f"- CRM 2 duplicate IDs sample: {quality_snapshot['crm2_duplicate_ids'][:20]}",
        "",
        "## IDs Without Match",
        f"- IDs in CRM 1 without CRM 2 match: {quality_snapshot['crm1_ids_without_match_in_crm2_count']}",
        f"- IDs in CRM 2 without CRM 1 match: {quality_snapshot['crm2_ids_without_match_in_crm1_count']}",
        f"- CRM 1-only IDs sample: {quality_snapshot['crm1_ids_without_match_in_crm2_sample']}",
        f"- CRM 2-only IDs sample: {quality_snapshot['crm2_ids_without_match_in_crm1_sample']}",
        "",
        "## Nulls in Critical Columns (CRM 1)",
    ]

    for column, null_count in quality_snapshot["crm1_nulls_critical"].items():
        content.append(f"- {column}: {null_count}")

    content.extend(["", "## Nulls in Critical Columns (CRM 2)"])
    for column, null_count in quality_snapshot["crm2_nulls_critical"].items():
        content.append(f"- {column}: {null_count}")

    content.extend(["", "## Invalid Date Values After Parsing"])
    for column, invalid_count in invalid_date_counts.items():
        content.append(f"- {column}: {invalid_count}")

    content.extend(["", "## Cleaning Decisions"])
    for decision in cleaning_decisions:
        content.append(f"- {decision}")

    path.write_text("\n".join(content), encoding="utf-8")
    return path


def write_executive_summary(
    output_dir: Path,
    overall_metrics: Dict[str, float],
    report_payload: Dict[str, Dict[str, object]],
) -> Path:
    """Write executive summary for leadership."""
    path = output_dir / OUTPUT_FILES["EXEC_SUMMARY"]

    churn_rate = overall_metrics["overall_churn_rate"]
    total_clients = int(overall_metrics["total_clients"])
    total_churned = int(overall_metrics["total_churned"])
    total_churn_revenue = overall_metrics["total_churn_revenue"]

    s1_table = report_payload["S1"]["table"]
    a1_table = report_payload["A1"]["table"]
    a2_table = report_payload["A2"]["table"]
    a3_table = report_payload["A3"]["table"]
    a4_table = report_payload["A4"]["table"]

    s2_before = report_payload["S2"]["metrics"]["before_activation_pct_clients"]
    s2_after = report_payload["S2"]["metrics"]["after_activation_pct_clients"]
    possflip_dollars = report_payload["S3"]["metrics"]["possflip_churn_dollars"]

    s1_distribution = s1_table[s1_table["timing_bucket"].str.startswith("STAT_") == False].copy()
    top_timing_row = s1_distribution.sort_values("churned_clients", ascending=False).head(1)
    top_timing_bucket = top_timing_row["timing_bucket"].iloc[0] if not top_timing_row.empty else "N/A"
    top_timing_pct = float(top_timing_row["pct_total_churn_clients"].iloc[0]) if not top_timing_row.empty else 0.0

    a1_churned = a1_table[a1_table["churn_group"] == "Churned"].head(1)
    a1_active = a1_table[a1_table["churn_group"] == "Active / Non-Churned"].head(1)
    churned_median_income = float(a1_churned["median_income"].iloc[0]) if not a1_churned.empty else 0.0
    active_median_income = float(a1_active["median_income"].iloc[0]) if not a1_active.empty else 0.0

    a2_top_rate = a2_table.sort_values("churn_rate", ascending=False).head(1)
    top_service_type = a2_top_rate["core_service_type"].iloc[0] if not a2_top_rate.empty else "N/A"
    top_service_rate = float(a2_top_rate["churn_rate"].iloc[0]) if not a2_top_rate.empty else 0.0

    a3_top_volume = a3_table.sort_values("churned_quantity", ascending=False).head(1)
    top_lead_source = a3_top_volume["Lead Source"].iloc[0] if not a3_top_volume.empty else "N/A"
    top_lead_churn_qty = int(a3_top_volume["churned_quantity"].iloc[0]) if not a3_top_volume.empty else 0

    a4_top_revenue = a4_table.sort_values("churn_revenue", ascending=False).head(1)
    top_invoice_bucket = a4_top_revenue["invoice_bucket"].iloc[0] if not a4_top_revenue.empty else "N/A"
    top_invoice_revenue = float(a4_top_revenue["churn_revenue"].iloc[0]) if not a4_top_revenue.empty else 0.0

    summary_lines = [
        "# Executive Summary",
        "",
        "## 1. Executive conclusion",
        "Con la evidencia disponible, el churn parece ser una combinación de servicio y avatar, con mayor peso relativo de señales de servicio por concentración temporal y activación incompleta.",
        (
            f"Sobre {total_clients} clientes, {total_churned} cumplen la definición estricta de churn "
            f"(`Status == \"Case Completed Failed\"`), equivalente a una churn rate general de {churn_rate:.2%}."
        ),
        "",
        "## 2. Key evidence from service reports",
        (
            f"- Evidencia fuerte: en S1, el bucket {top_timing_bucket} concentra {top_timing_pct:.2f}% del churn, "
            "lo que muestra patrón temporal identificable en el ciclo de servicio."
        ),
        (
            f"- Evidencia fuerte: en S2, {s2_before:.2f}% del churn ocurre before activation y "
            f"{s2_after:.2f}% after activation, mientras una porción material cae en no activation date available, "
            "señal de fricción en onboarding/documentación y trazabilidad operativa."
        ),
        (
            f"- Evidencia moderada: en S3, el possflip churn suma ${possflip_dollars:,.2f}. "
            "Esto apunta a revisar handoff entre originación financiera y operación del caso."
        ),
        "",
        "## 3. Key evidence from avatar reports",
        (
            f"- Evidencia moderada: en A1, mediana de income churned (${churned_median_income:,.0f}) "
            f"vs active/non-churned (${active_median_income:,.0f}) sugiere posible diferencia de perfil económico."
        ),
        (
            f"- Evidencia moderada: en A2, la mayor churn rate aparece en {top_service_type} ({top_service_rate:.2%}), "
            "indicando heterogeneidad por mix de servicio ofertado."
        ),
        (
            f"- Evidencia moderada: en A3, {top_lead_source} concentra el mayor volumen churn ({top_lead_churn_qty} clientes), "
            f"y en A4 el bucket {top_invoice_bucket} concentra ${top_invoice_revenue:,.2f} de churn revenue."
        ),
        (
            f"- El churn revenue total observado bajo la definición estricta es ${total_churn_revenue:,.2f}, "
            "que permite priorizar segmentos por impacto económico."
        ),
        "",
        "## 4. Limitations",
        "- El análisis es observacional y no prueba causalidad.",
        "- S2 contiene una porción relevante sin fecha de activación efectiva, lo que limita inferencia de etapa exacta.",
        "- Tasa de churn en grupos de bajo volumen puede ser inestable.",
        "",
        "## 5. Recommended next steps",
        "- Priorizar cohortes con mayor churn revenue y mayor churn rate para deep-dive operativo.",
        "- Diseñar tests por segmento (avatar) y por etapa del funnel/servicio (onboarding vs post-activation).",
        "- Instrumentar tracking adicional de motivos de churn para fortalecer inferencias causales.",
    ]

    path.write_text("\n".join(summary_lines), encoding="utf-8")
    return path


def write_report_interpretations(output_dir: Path, report_payload: Dict[str, Dict[str, object]]) -> Path:
    """Write a markdown file with 2-4 sentence interpretations per report."""
    path = output_dir / OUTPUT_FILES["REPORT_NOTES"]
    lines = ["# Report Interpretations", ""]
    for report_key in ["S1", "S2", "S3", "A1", "A2", "A3", "A4"]:
        lines.append(f"## {report_key}")
        lines.append(report_payload[report_key]["interpretation"])
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def export_excel_workbook(
    output_dir: Path,
    report_payload: Dict[str, Dict[str, object]],
    executive_summary_path: Path,
    data_quality_path: Path,
) -> Path:
    """Export all report tables to one Excel workbook."""
    workbook_path = output_dir / OUTPUT_FILES["WORKBOOK"]
    with pd.ExcelWriter(workbook_path, engine="openpyxl") as writer:
        for report_key in ["S1", "S2", "S3", "A1", "A2", "A3", "A4"]:
            report_payload[report_key]["table"].to_excel(writer, sheet_name=report_key, index=False)

        executive_lines = executive_summary_path.read_text(encoding="utf-8").splitlines()
        quality_lines = data_quality_path.read_text(encoding="utf-8").splitlines()
        pd.DataFrame({"Executive Summary": executive_lines}).to_excel(
            writer, sheet_name="Executive Summary", index=False
        )
        pd.DataFrame({"Data Quality": quality_lines}).to_excel(writer, sheet_name="Data Quality", index=False)
    return workbook_path

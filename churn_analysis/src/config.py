"""Configuration constants for churn analysis pipeline."""

from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

CRM1_FILENAME = "data from CRM 1 (1).csv"
CRM2_FILENAME = "data from CRM 2 (1).csv"

CRM1_PATH = DATA_DIR / CRM1_FILENAME
CRM2_PATH = DATA_DIR / CRM2_FILENAME

# Business rules
CHURN_STATUS = "Case Completed Failed"
JOIN_KEY = "ITR Id"

# Expected columns
CRM1_REQUIRED_COLUMNS = [
    "ITR Id",
    "2nd Trade Received Agreement Date",
    "Lead Source",
    "Approximate Gross Monthly household income",
    "Service/Resolution Type 1.1",
    "Service/Resolution Type 2.1",
    "Service/Resolution Type 3.1",
    "Service/Resolution Type 4.1",
    "Service/Resolution Type 5.1",
    "Service/Resolution Type 6.1",
    "Financing Lender Used",
    "Offered Client Financing",
    "Agreed Client Financing",
    "Approved For Financing",
    "Financing Amount Approved",
    "Clients first payment date",
    "Net Net Resolution Costs",
    "Rating",
]

CRM2_REQUIRED_COLUMNS = [
    "ITR Id",
    "Status",
    "Sub_status",
    "ITR_Close_Date",
    "Activation_Date__c",
    "Pre_Activation_Date__c",
]

DATE_COLUMNS_CRM1 = [
    "2nd Trade Received Agreement Date",
    "Clients first payment date",
]

DATE_COLUMNS_CRM2 = [
    "ITR_Close_Date",
    "Activation_Date__c",
    "Pre_Activation_Date__c",
]

NUMERIC_COLUMNS_CRM1 = [
    "Approximate Gross Monthly household income",
    "Financing Amount Approved",
    "Net Net Resolution Costs",
]

SERVICE_COLS_2_3 = [
    "Service/Resolution Type 2.1",
    "Service/Resolution Type 3.1",
]

SERVICE_COLS_3_6 = [
    "Service/Resolution Type 3.1",
    "Service/Resolution Type 4.1",
    "Service/Resolution Type 5.1",
    "Service/Resolution Type 6.1",
]

SERVICE_COLS_4_6 = [
    "Service/Resolution Type 4.1",
    "Service/Resolution Type 5.1",
    "Service/Resolution Type 6.1",
]

# Output files
OUTPUT_FILES = {
    "S1": "report_S1_churn_timing.csv",
    "S2": "report_S2_activation_timing.csv",
    "S3": "report_S3_financing_lender_churn.csv",
    "A1": "report_A1_income_churn_vs_active.csv",
    "A2": "report_A2_churn_by_core_service_type.csv",
    "A3": "report_A3_churn_by_lead_source.csv",
    "A4": "report_A4_churn_by_invoice_size.csv",
    "EXEC_SUMMARY": "executive_summary.md",
    "DATA_QUALITY": "data_quality_report.md",
    "REPORT_NOTES": "report_interpretations.md",
    "WORKBOOK": "churn_analysis_reports.xlsx",
}

S1_BUCKET_LABELS = [
    "0-30 days",
    "31-60 days",
    "61-90 days",
    "91-180 days",
    "181-365 days",
    ">365 days",
    "Insufficient Date Data",
]

INVOICE_BUCKETS = [
    (29950.0, float("inf"), "> $29,950"),
    (19950.0, 29949.9999, "$19,950 - $29,949"),
    (14950.0, 19949.9999, "$14,950 - $19,949"),
    (9950.0, 14949.9999, "$9,950 - $14,949"),
    (4000.0, 9949.9999, "$4,000 - $9,949"),
    (1.0, 3999.9999, "$1 - $3,999"),
]

INVOICE_MISSING_LABEL = "Missing / Zero / Invalid"

# Churn Analysis Pipeline

Pipeline profesional de análisis de churn para el assessment de Data Analyst, diseñado para ejecución reproducible y entregables para liderazgo.

## Project Structure

- `data/`: archivos de entrada CRM 1 y CRM 2.
- `outputs/`: reportes generados (CSV, Markdown y Excel).
- `src/`: código modular del pipeline.
  - `config.py`: constantes y definiciones de negocio.
  - `load_data.py`: carga de archivos.
  - `validation.py`: validaciones de esquema y calidad de datos.
  - `clean_data.py`: limpieza de fechas, strings y numéricos.
  - `transformations.py`: join, flags de churn y variables derivadas.
  - `reports.py`: construcción de reportes S1-S3 y A1-A4.
  - `export.py`: exportación de archivos de salida.
  - `main.py`: orquestación end-to-end.

## Churn Definition (Critical Rule)

Un cliente es churned **únicamente** cuando en CRM 2:

`Status == "Case Completed Failed"`

Ninguna otra condición se usa para definir churn.

## Core Service Classification Rule

La función `classify_core_service(row)` aplica prioridad estricta (first match wins):

1. `Hardship`: si alguna de `Service/Resolution Type 4.1`, `5.1`, `6.1` contiene `hardship` (case-insensitive).
2. `Fresh Start`: si alguna de `Service/Resolution Type 3.1`, `4.1`, `5.1`, `6.1` contiene `Fresh Start` (case-insensitive).
3. `Tax Prep Only`: si `Service/Resolution Type 2.1` o `3.1` contiene `File` y ninguna de `4.1`, `5.1`, `6.1` contiene `File`.
4. `Other/Unknown`: cualquier otro caso.

## Setup

1. Crear y activar entorno virtual (recomendado):
   - Windows PowerShell:
     - `python -m venv .venv`
     - `.venv\\Scripts\\Activate.ps1`
2. Instalar dependencias:
   - `pip install -r requirements.txt`

## Run

Desde la carpeta `churn_analysis`:

`python src/main.py`

El pipeline imprime en consola:
- filas cargadas por CRM,
- total de clientes,
- total churned,
- churn rate general,
- ubicación de outputs.

## Generated Outputs

- `report_S1_churn_timing.csv`
- `report_S2_activation_timing.csv`
- `report_S3_financing_lender_churn.csv`
- `report_A1_income_churn_vs_active.csv`
- `report_A2_churn_by_core_service_type.csv`
- `report_A3_churn_by_lead_source.csv`
- `report_A4_churn_by_invoice_size.csv`
- `executive_summary.md`
- `data_quality_report.md`
- `report_interpretations.md`
- `churn_analysis_reports.xlsx` (opcional deseable implementado)

## Assumptions and Data Handling

- Se usan los nombres reales de columnas observados en los CSV.
- Join por `ITR Id` con validación de duplicados y no-match en ambos sentidos.
- Fechas parseadas con `pd.to_datetime(..., errors="coerce")`.
- Numéricos limpiados removiendo `$`, comas y valores vacíos antes de `pd.to_numeric(..., errors="coerce")`.
- Outliers en A1 removidos con IQR; la regla se documenta en outputs.
- Si faltan columnas requeridas, el pipeline falla con error explícito.

## Reading the Reports

- `churn rate` siempre significa: churned del grupo / total clients del grupo.
- `% of total churn` siempre significa: churned del grupo / total churned general.
- Para distribución de churn (ej. timing), los porcentajes usan como base el total churned.
- El análisis es descriptivo/correlacional y evita inferencias causales fuertes.

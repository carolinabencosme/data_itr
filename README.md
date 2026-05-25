# data_itr — Análisis de churn (CRM)

Este repositorio contiene los datos CRM y el **pipeline de análisis de churn** listo para ejecutar de punta a punta.

## Dónde está la implementación

Todo el código, dependencias y documentación del assessment viven en:

**[`churn_analysis/`](churn_analysis/)**

La guía completa (estructura de carpetas, definición de churn, reglas de clasificación de servicio, supuestos e interpretación de reportes) está en:

**[`churn_analysis/README.md`](churn_analysis/README.md)**

## Implementación end-to-end (rápida)

1. **Requisitos:** Python 3.10+ (recomendado), `pip`.

2. **Datos:** Los CSV deben estar en `churn_analysis/data/` con los nombres que espera el pipeline (por ejemplo `data from CRM 1 (1).csv` y `data from CRM 2 (1).csv`). Las rutas se configuran en `churn_analysis/src/config.py`.

3. **Entorno e instalación** (desde la raíz del repo):

   ```powershell
   cd churn_analysis
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

4. **Ejecución:**

   ```powershell
   python src/main.py
   ```

5. **Salidas:** Se generan en `churn_analysis/outputs/` (CSV por reporte S1–S3 y A1–A4, `executive_summary.md`, `data_quality_report.md`, `report_interpretations.md`, y el Excel `churn_analysis_reports.xlsx`).

6. **Consola:** Al terminar, el script imprime filas cargadas, totales, churn rate global y rutas absolutas de los artefactos.

## Cómo entender el flujo del código

Orden sugerido de lectura en `churn_analysis/src/`:

| Orden | Archivo            | Rol |
|-------|--------------------|-----|
| 1     | `config.py`        | Constantes: churn, columnas, rutas, buckets. |
| 2     | `load_data.py`     | Carga de CSV. |
| 3     | `validation.py`    | Columnas requeridas, duplicados `ITR Id`, IDs sin match. |
| 4     | `clean_data.py`    | Fechas y numéricos robustos. |
| 5     | `transformations.py` | Join, `is_churned`, `churn_revenue`, activación efectiva, `classify_core_service`. |
| 6     | `reports.py`       | Tablas S1–S3, A1–A4. |
| 7     | `export.py`        | CSV, Markdown, Excel. |
| 8     | `main.py`          | Orquestación end-to-end. |

**Regla crítica de negocio:** churn solo si `Status == "Case Completed Failed"` en CRM 2 (ver `config.py` y el README dentro de `churn_analysis/`).

## Archivos en la raíz de este repo

Los CSV en la raíz (`data from CRM 1 (1).csv`, etc.) pueden coexistir con las copias bajo `churn_analysis/data/`; el pipeline lee por defecto los de `churn_analysis/data/`. Si actualizas datos, copia o sincroniza allí antes de volver a correr `main.py`.

# Executive Summary

## 1. Executive conclusion
Con la evidencia disponible, el churn parece ser una combinación de servicio y avatar, con mayor peso relativo de señales de servicio por concentración temporal y activación incompleta.
Sobre 420 clientes, 94 cumplen la definición estricta de churn (`Status == "Case Completed Failed"`), equivalente a una churn rate general de 22.38%.

## 2. Key evidence from service reports
- Evidencia fuerte: en S1, el bucket 181-365 days concentra 43.62% del churn, lo que muestra patrón temporal identificable en el ciclo de servicio.
- Evidencia fuerte: en S2, 18.09% del churn ocurre before activation y 14.89% after activation, mientras una porción material cae en no activation date available, señal de fricción en onboarding/documentación y trazabilidad operativa.
- Evidencia moderada: en S3, el possflip churn suma $662,010.00. Esto apunta a revisar handoff entre originación financiera y operación del caso.

## 3. Key evidence from avatar reports
- Evidencia moderada: en A1, mediana de income churned ($4,710) vs active/non-churned ($4,990) sugiere posible diferencia de perfil económico.
- Evidencia moderada: en A2, la mayor churn rate aparece en Hardship (27.13%), indicando heterogeneidad por mix de servicio ofertado.
- Evidencia moderada: en A3, Aged 365 Legacy HAP concentra el mayor volumen churn (21 clientes), y en A4 el bucket $9,950 - $14,949 concentra $274,710.00 de churn revenue.
- El churn revenue total observado bajo la definición estricta es $1,217,860.00, que permite priorizar segmentos por impacto económico.

## 4. Limitations
- El análisis es observacional y no prueba causalidad.
- S2 contiene una porción relevante sin fecha de activación efectiva, lo que limita inferencia de etapa exacta.
- Tasa de churn en grupos de bajo volumen puede ser inestable.

## 5. Recommended next steps
- Priorizar cohortes con mayor churn revenue y mayor churn rate para deep-dive operativo.
- Diseñar tests por segmento (avatar) y por etapa del funnel/servicio (onboarding vs post-activation).
- Instrumentar tracking adicional de motivos de churn para fortalecer inferencias causales.
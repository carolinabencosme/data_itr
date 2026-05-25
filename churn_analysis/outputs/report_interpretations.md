# Report Interpretations

## S1
El churn se concentra más en el bucket 181-365 days (43.62% de churned clients). El tiempo promedio desde acuerdo a churn es 147.0 días y la mediana 121.0 días. Esto ayuda a identificar si la fricción ocurre temprano o tardío en el ciclo del cliente.

## S2
El churn before activation representa 18.09% de churned clients, mientras after activation representa 14.89%. Una proporción alta before activation sugiere fricción de onboarding/expectativas; una proporción alta after activation sugiere posible problema de ejecución del servicio.

## S3
El churn de clientes con lender (possflip churn) suma $662,010.00. El breakdown por lender permite separar si el riesgo está concentrado en pocos originadores o distribuido. Este reporte debe leerse junto al volumen total por lender para evitar sobre-interpretar tasas en bases pequeñas.

## A1
La comparación de income se hizo excluyendo outliers con método IQR para evitar sesgo por extremos. Diferencias de mediana entre churned y active/non-churned sugieren posible desalineación de avatar financiero, pero deben interpretarse junto a mix de servicio y lead source.

## A2
Este corte muestra si el churn está más concentrado por tipo de servicio entregado. Si una categoría combina alto volumen y alta churn rate, se vuelve candidata prioritaria para investigación operativa.

## A3
Lead sources con alto churn volume o churn revenue deben revisarse en targeting y expectativa comercial. Nota: fuentes con pocos clientes pueden mostrar churn rates inestables, por lo que la lectura debe ponderar volumen.

## A4
Este reporte permite ver si el churn está concentrado en tickets bajos, medios o altos. Combinar churn rate con participación del churn revenue evita sesgo por solo volumen de clientes.

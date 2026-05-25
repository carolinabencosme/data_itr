# Data Quality Report

## Row Counts
- CRM 1 rows: 420
- CRM 2 rows: 420
- Rows after join: 420

## Duplicates by `ITR Id`
- CRM 1 duplicate rows: 0
- CRM 2 duplicate rows: 0
- CRM 1 duplicate IDs sample: []
- CRM 2 duplicate IDs sample: []

## IDs Without Match
- IDs in CRM 1 without CRM 2 match: 0
- IDs in CRM 2 without CRM 1 match: 0
- CRM 1-only IDs sample: []
- CRM 2-only IDs sample: []

## Nulls in Critical Columns (CRM 1)
- ITR Id: 0
- 2nd Trade Received Agreement Date: 0
- Lead Source: 0
- Approximate Gross Monthly household income: 0
- Service/Resolution Type 1.1: 0
- Service/Resolution Type 2.1: 0
- Service/Resolution Type 3.1: 0
- Service/Resolution Type 4.1: 111
- Service/Resolution Type 5.1: 156
- Service/Resolution Type 6.1: 159
- Financing Lender Used: 267
- Offered Client Financing: 0
- Agreed Client Financing: 0
- Approved For Financing: 0
- Financing Amount Approved: 0
- Clients first payment date: 0
- Net Net Resolution Costs: 0
- Rating: 0

## Nulls in Critical Columns (CRM 2)
- ITR Id: 0
- Status: 0
- Sub_status: 326
- ITR_Close_Date: 326
- Activation_Date__c: 181
- Pre_Activation_Date__c: 181

## Invalid Date Values After Parsing
- 2nd Trade Received Agreement Date: 0
- Clients first payment date: 0
- ITR_Close_Date: 0
- Activation_Date__c: 0
- Pre_Activation_Date__c: 0

## Cleaning Decisions
- Fechas parseadas con pd.to_datetime(errors='coerce').
- Valores numéricos limpiados removiendo '$', comas y espacios; conversion con to_numeric(errors='coerce').
- Definición de churn estricta aplicada: Status == 'Case Completed Failed'.
- effective_activation_date usa Activation_Date__c con fallback a Pre_Activation_Date__c.
- A1 removió outliers de income con método IQR.
- Duplicados y IDs sin match se reportan, no se eliminan silenciosamente.
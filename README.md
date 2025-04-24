
# Azure Serverless ETL for Bsale + PostgreSQL + Shopify

This project implements a **low-cost, automated ETL architecture** that combines data from the **Bsale ERP** and **Shopify**, integrating the information into a **PostgreSQL database hosted on Azure** and connecting it to **Power BI** for visualization. The goal is to create a scalable, serverless, and efficient solution for analyzing sales and inventory for a multichannel retail company (physical and online).

---

## 🎯 Dashboard Objective

Build a comprehensive dashboard for a sporting goods company, consolidating sales, inventory, and performance across all channels (physical stores, marketplaces, e-commerce, and ad campaigns), supporting real-time strategic decision-making.

---

## 🔗 Data Sources

1. **Physical Store**: Managed via the Bsale ERP (also acts as POS).
2. **Marketplaces**: Mercadolibre, Falabella, Ripley, Paris, MCO, and Shopify. All inject data into the Bsale ERP.
3. **Online Campaigns**: Google Ads and Meta (Facebook/Instagram), queried separately via API.

---

## ⚙️ Architecture & Azure Resources

- **Azure Function App (Consumption Plan)**: serverless and cost-effective.
- **Azure Blob Storage**: `.csv` backups per folder (`raw-data/documentos/`, etc.).
- **Azure PostgreSQL Flexible Server**
- **Power BI**: star schema connected to PostgreSQL.

---

## 🧩 Automation: Scripts & Functions

### 1. **Azure Functions**

- **UpdateDocuments**: Downloads documents, clients, and sellers from Bsale, backs up to Blob Storage, and updates `documentos` table in PostgreSQL.
- **UpdatePayments**: Downloads payments from Bsale and updates PostgreSQL.
- **Triggers:**  
  - `UpdateDocuments`: Daily at 6:00 AM  
  - `UpdatePayments`: Daily at 6:30 AM

### 2. **Additional Script: `fix_missing_details.py`**

- Identifies `document_id` values missing in `document_details`.
- Downloads details from Bsale using `details_url`.
- Backs up to Blob and appends to PostgreSQL.

### 3. **Local to Blob to PostgreSQL Upload**

- Reads local files (SharePoint synced).
- Uploads to Blob Storage with timestamp.
- Loads into PostgreSQL (replacing or appending based on existence).

---

## 🗂 Repository Structure
```
sports-retail-powerbi/
├── data/                  # Local data per source (documents, details, etc.)
├── images/                # Diagrams and visual aids
├── pbix/                  # Power BI reports
├── scripts/
│   ├── azure_functions/   # Azure Functions: UpdateDocuments, UpdatePayments
│   ├── upload_to_postgres/ (etl_blob_to_postgres.py, fix_missing_details.py)
│   └── download_csvs/     (update_documents.py, update_payments.py, etc.)
├── config/                # .env files and configuration
├── requirements.txt
└── main.py
```
---

## 💾 PostgreSQL Tables

### Fact Tables
- `documentos`, `document_details`, `pagos`

### Dimension Tables
- `clients`, `products`, `product_types`, `users`, `variants`, `document_types`, `tipos_de_pago`, `categories`, `Date`, `metas_2025`, `Measures`

---

## 🧠 Data Model & Power BI

Star schema composed of:

- Fact: `documentos`, `document_details`, `pagos`
- Dimensions: `products`, `users`, `clients`, `product_types`, `variants`, `categories`, `Date`, etc.

Key relationships:
- `documentos.document_type_id` → `document_types.id`
- `documentos.document_id` → `document_details.document_id`
- `variants` → `products` → `categories`

![Power BI Schema](images/pbi_schema.png)

---

## ⏱️ Date Handling

- Dates are transformed to **epoch timestamp** to:
  - Filter by range (`emissiondaterange`)
  - Normalize cutoffs to UTC midnight
  - Perform incremental loads from `MAX(emission_date)`

---

## 🛍️ Shopify Integration

- API: GraphQL (endpoint `/admin/api/2024-01/graphql.json`)
- Fetches real (non-test/cancelled) orders
- Converts timestamps to **America/Santiago** timezone
- Aggregates daily sales
- CSV saved to `data/shopify_sales/ventas_shopify.csv`

---

## 📈 Automation & Deployment

- Local dev: Azure Functions Core Tools + `.venv`
- Requirements: `azure-functions`, `pandas`, `sqlalchemy`, `psycopg2`, `dotenv`
- Deploy:

func azure functionapp publish <app_name> --python

az functionapp function invoke --resource-group <RG> --name <app_name> --function-name <FunctionName>

---

## 🧪 Common Errors & Fixes

| Error                                       | Solution                                                  |
|--------------------------------------------|-----------------------------------------------------------|
| '_Environ' object is not callable          | Use `os.environ[]` instead of `os.environ()`              |
| KeyError: 'VARIABLE'                       | Ensure variable exists in `local.settings.json` or App Settings |
| Did not find functions with language [python] | Reinstall Azure Functions Core Tools with correct Python |
| 127.0.0.1:10000 connection refused         | Misconfigured `AzureWebJobsStorage`                      |

---

## 💰 Cost Optimization Strategy

- **Azure Functions (Linux Consumption Plan)**: no cost if idle.
- **No Azure Data Factory**: replaced with custom scripts.
- Functions run in < 1 second.

---

## 🚀 Future Enhancements

- Add endpoints: stock, credit notes, invoices
- Push data to Power BI via DirectQuery
- Blob versioning for auditability
- Retry policies for network/API issues
- Integration with Application Insights

---

## 🔍 Current Status

✅ Operational architecture  
✅ Daily automation  
✅ Data available for Power BI modeling  
✅ Shopify integration complete  
🚧 Pending: campaign integration & product segmentation


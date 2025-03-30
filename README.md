# Sales Dashboard for Sporting Goods

## Project Objective

The objective of this project is to create a **complete dashboard** for a sporting goods company. This company manages sales through various channels, both physical and digital. The dashboard will consolidate data from different sources to provide a comprehensive view of the company's sales and inventory.

## Data Sources

The company obtains sales and stock data from various sources:

1. **In-store sales**: Sales data from the physical store is managed directly through the **ERP Bsale**, which also serves as the POS system.
2. **Online sales**:
   - **Marketplaces**: The company sells through the following marketplaces: **Mercadolibre**, **Falabella**, **Ripley**, **Paris**, **MCO (Rideshop)**, and **Shopify** (Store web). These marketplaces inject sales and stock data directly into the **ERP Bsale**.
3. **Online Marketing**: The data from advertising campaigns does not get injected into the ERP but is obtained directly from the online marketing platforms:
   - **Google Ads**
   - **Meta (Facebook, Instagram)**

## ERP and Marketplace Integration

The company uses the **ERP Bsale** as the system to manage sales and stock. This ERP is directly connected to the marketplaces and the store's POS system, allowing for continuous updates of sales and stock data.

## Information Flow Diagram

The following diagram illustrates the flow of information between the different systems:

- **In-store sales**: Directly recorded in the ERP Bsale.
- **Online sales from Marketplace (Mercadolibre, Falabella, Ripley, Paris, MCO)**: Sales and stock data are injected directly into the ERP Bsale.
- **Online Marketing (Google Ads and Meta)**: Campaign data is obtained directly from the marketing platforms and is not injected into the ERP.

![Information Flow](images/flujo_datos.jpg)


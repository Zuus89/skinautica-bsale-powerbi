import requests
import pandas as pd
from dotenv import load_dotenv
import os

# === Load API Token ===
load_dotenv(dotenv_path="config/.env")
ACCESS_TOKEN = os.getenv("BSALE_ACCESS_TOKEN")

# === API Configuration ===
BASE_URL = "https://api.bsale.cl/v1/products.json"

# Parameters for the API request (pagination)
params = {
    "limit": 50,  # Limit of products per request
    "offset": 0   # Starting point for pagination
}

headers = {
    "access_token": ACCESS_TOKEN
}

# === Download Product Data ===
product_data = []
print("🔄 Downloading products...")

while True:
    response = requests.get(BASE_URL, headers=headers, params=params)
    
    # Check if the request was successful
    if response.status_code != 200:
        print(f"❌ Error: {response.status_code}, {response.text}")
        break

    data = response.json()
    products = data.get("items", [])
    
    if not products:
        break

    for product in products:
        # Extract the necessary product data, handling nested structures
        product_info = {
            "product_id": product.get("id"),
            "name": product.get("name"),
            "description": product.get("description"),
            "classification": product.get("classification"),
            "ledger_account": product.get("ledgerAccount"),
            "cost_center": product.get("costCenter"),
            "allow_decimal": product.get("allowDecimal"),
            "stock_control": product.get("stockControl"),
            "print_detail_pack": product.get("printDetailPack"),
            "state": product.get("state"),
            "prestashop_product_id": product.get("prestashopProductId"),
            "prestashop_attribute_id": product.get("presashopAttributeId"),
            # Handle nested "product_type"
            "product_type_id": product.get("product_type", {}).get("id"),
        }
        product_data.append(product_info)

    # Update the offset for pagination
    params["offset"] += params["limit"]

# === Save Data to CSV ===
if product_data:
    output_dir = "data/products/"
    os.makedirs(output_dir, exist_ok=True)

    filename = "products_data.csv"
    filepath = os.path.join(output_dir, filename)

    # Save to CSV
    df = pd.DataFrame(product_data)
    df.to_csv(filepath, index=False)

    print(f"✅ {len(df)} product records saved to '{filepath}'")
else:
    print("⚠️ No products found.")

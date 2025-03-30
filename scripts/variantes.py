import requests
import pandas as pd
from dotenv import load_dotenv
import os

# === Load API Token ===
load_dotenv(dotenv_path="config/.env")
ACCESS_TOKEN = os.getenv("BSALE_ACCESS_TOKEN")

# === API Configuration ===
BASE_URL = "https://api.bsale.cl/v1/variants.json"

# Parameters for the API request (pagination)
params = {
    "limit": 50,  # Limit of variants per request
    "offset": 0   # Starting point for pagination
}

headers = {
    "access_token": ACCESS_TOKEN
}

# === Download Variant Data ===
variant_data = []
print("🔄 Downloading variants...")

while True:
    response = requests.get(BASE_URL, headers=headers, params=params)
    
    # Check if the request was successful
    if response.status_code != 200:
        print(f"❌ Error: {response.status_code}, {response.text}")
        break

    data = response.json()
    variants = data.get("items", [])
    
    if not variants:
        break

    for variant in variants:
        # Extract the necessary variant data, handling nested structures
        variant_info = {
            "variant_id": variant.get("id"),
            "description": variant.get("description"),
            "unlimited_stock": variant.get("unlimitedStock"),
            "allow_negative_stock": variant.get("allowNegativeStock"),
            "state": variant.get("state"),
            "bar_code": variant.get("barCode"),
            "code": variant.get("code"),
            "imagestion_center_cost": variant.get("imagestionCenterCost"),
            "imagestion_account": variant.get("imagestionAccount"),
            "imagestion_concept_cod": variant.get("imagestionConceptCod"),
            "imagestion_project_cod": variant.get("imagestionProyectCod"),
            "imagestion_category_cod": variant.get("imagestionCategoryCod"),
            "imagestion_product_id": variant.get("imagestionProductId"),
            "serial_number": variant.get("serialNumber"),
            "prestashop_combination_id": variant.get("prestashopCombinationId"),
            "prestashop_value_id": variant.get("prestashopValueId"),
            # Handle nested "product" and extract "id" as product_id
            "product_id": variant.get("product", {}).get("id"),
            # Handle nested "costs" and extract "href" for costs
            "costs_href": variant.get("costs", {}).get("href"),
        }
        variant_data.append(variant_info)

    # Update the offset for pagination
    params["offset"] += params["limit"]

# === Save Data to CSV ===
if variant_data:
    output_dir = "data/variants/"
    os.makedirs(output_dir, exist_ok=True)

    filename = "variants_data.csv"
    filepath = os.path.join(output_dir, filename)

    # Save to CSV
    df = pd.DataFrame(variant_data)
    df.to_csv(filepath, index=False)

    print(f"✅ {len(df)} variant records saved to '{filepath}'")
else:
    print("⚠️ No variants found.")

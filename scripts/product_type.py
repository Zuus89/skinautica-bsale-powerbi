import requests
import pandas as pd
from dotenv import load_dotenv
import os

# === Load API Token ===
load_dotenv(dotenv_path="config/.env")
ACCESS_TOKEN = os.getenv("BSALE_ACCESS_TOKEN")

# === API Configuration ===
BASE_URL = "https://api.bsale.cl/v1/product_types.json"

# Parameters for the API request (pagination)
params = {
    "limit": 50,  # Limit of product types per request
    "offset": 0   # Starting point for pagination
}

headers = {
    "access_token": ACCESS_TOKEN
}

# === Download Product Types ===
product_types_data = []
print("🔄 Downloading product types...")

while True:
    response = requests.get(BASE_URL, headers=headers, params=params)
    
    # Check if the request was successful
    if response.status_code != 200:
        print(f"❌ Error: {response.status_code}, {response.text}")
        break

    data = response.json()
    product_types = data.get("items", [])
    
    if not product_types:
        break

    for product_type in product_types:
        # Extract only the necessary product type data
        product_type_info = {
            "product_type_id": product_type.get("id"),
            "name": product_type.get("name"),
        }
        product_types_data.append(product_type_info)

    # Update the offset for pagination
    params["offset"] += params["limit"]

# === Save Data to CSV ===
if product_types_data:
    output_dir = "data/product_types/"
    os.makedirs(output_dir, exist_ok=True)

    filename = "product_types_data.csv"
    filepath = os.path.join(output_dir, filename)

    # Save to CSV
    df = pd.DataFrame(product_types_data)
    df.to_csv(filepath, index=False)

    print(f"✅ {len(df)} product types records saved to '{filepath}'")
else:
    print("⚠️ No product types found.")

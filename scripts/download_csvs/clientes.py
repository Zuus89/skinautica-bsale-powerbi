import requests
import pandas as pd
from dotenv import load_dotenv
import os

# === Load API Token ===
load_dotenv(dotenv_path=".env")
ACCESS_TOKEN = os.getenv("BSALE_ACCESS_TOKEN")

# === API Configuration ===
BASE_URL = "https://api.bsale.cl/v1/clients.json"

# Parameters for the API request (pagination)
params = {
    "limit": 50,  # Limit of clients per request
    "offset": 0   # Starting point for pagination
}

headers = {
    "access_token": ACCESS_TOKEN
}

# === Download Client Data ===
client_data = []
print("🔄 Downloading clients...")

while True:
    response = requests.get(BASE_URL, headers=headers, params=params)
    
    # Check if the request was successful
    if response.status_code != 200:
        print(f"❌ Error: {response.status_code}, {response.text}")
        break

    data = response.json()
    clients = data.get("items", [])
    
    if not clients:
        break

    for client in clients:
        # Extract only the necessary client data
        client_info = {
            "client_id": client.get("id"),
            "first_name": client.get("firstName"),
            "last_name": client.get("lastName"),
            "email": client.get("email"),
            "rut": client.get("code"),
        }
        client_data.append(client_info)

    # Update the offset for pagination
    params["offset"] += params["limit"]

# === Save Data to CSV ===
if client_data:
    output_dir = "data/clients/"
    os.makedirs(output_dir, exist_ok=True)

    filename = "clients_data.csv"
    filepath = os.path.join(output_dir, filename)

    # Save to CSV
    df = pd.DataFrame(client_data)
    df.to_csv(filepath, index=False)

    print(f"✅ {len(df)} client records saved to '{filepath}'")
else:
    print("⚠️ No clients found.")

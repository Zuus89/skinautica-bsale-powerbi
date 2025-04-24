import requests
import pandas as pd
from dotenv import load_dotenv
import os

# === Load API Token ===
load_dotenv(dotenv_path=".env")
ACCESS_TOKEN = os.getenv("BSALE_ACCESS_TOKEN")

# === API Configuration ===
BASE_URL = "https://api.bsale.cl/v1/users.json"

# Parameters for the API request (pagination)
params = {
    "limit": 50,  # Limit of users per request
    "offset": 0   # Starting point for pagination
}

headers = {
    "access_token": ACCESS_TOKEN
}

# === Download User Data ===
user_data = []
print("🔄 Downloading users...")

while True:
    response = requests.get(BASE_URL, headers=headers, params=params)
    
    # Check if the request was successful
    if response.status_code != 200:
        print(f"❌ Error: {response.status_code}, {response.text}")
        break

    data = response.json()
    users = data.get("items", [])
    
    if not users:
        break

    for user in users:
        # Extract only the necessary user data
        user_info = {
            "user_id": user.get("id"),
            "first_name": user.get("firstName"),
            "last_name": user.get("lastName"),
        }
        user_data.append(user_info)

    # Update the offset for pagination
    params["offset"] += params["limit"]

# === Save Data to CSV ===
if user_data:
    output_dir = "data/users/"
    os.makedirs(output_dir, exist_ok=True)

    filename = "users_data.csv"
    filepath = os.path.join(output_dir, filename)

    # Save to CSV
    df = pd.DataFrame(user_data)
    df.to_csv(filepath, index=False)

    print(f"✅ {len(df)} user records saved to '{filepath}'")
else:
    print("⚠️ No users found.")

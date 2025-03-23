import requests
import pandas as pd
from dotenv import load_dotenv
import os

# === Load the API Token from .env ===
# This will load your Bsale API token stored in the .env file
load_dotenv(dotenv_path="config/.env")
ACCESS_TOKEN = os.getenv("BSALE_ACCESS_TOKEN")

# === API Configuration ===
# Base URL for the Bsale API
BASE_URL = "https://api.bsale.cl/v1/document_types.json"

# Set the headers with the API token for authentication
headers = {
    "access_token": ACCESS_TOKEN
}

# === Function to Download Document Types ===
def download_document_types():
    print("🔄 Downloading document types...")

    # Make a GET request to the Bsale API to fetch document types
    response = requests.get(BASE_URL, headers=headers)

    # Check if the request was successful (HTTP status code 200)
    if response.status_code != 200:
        print("❌ Error:", response.status_code, response.text)
        return

    # Parse the JSON response to extract document types
    document_types = response.json().get("items", [])

    # Check if we received any document types
    if not document_types:
        print("⚠️ No document types found.")
        return

    # Initialize an empty list to store the document types data
    document_type_details = []

    # Loop through each document type and extract relevant details
    for doc_type in document_types:
        document_type_data = {
            "document_type_id": doc_type.get("id"),
            "description": doc_type.get("description"),
            "code": doc_type.get("code"),
            "created_at": doc_type.get("createdAt"),
            "updated_at": doc_type.get("updatedAt")
        }
        document_type_details.append(document_type_data)

    # === Save the document types data to a CSV file ===
    output_dir = "data/document_types/"
    os.makedirs(output_dir, exist_ok=True)

    filename = "document_types.csv"
    filepath = os.path.join(output_dir, filename)

    # Convert the document types data to a pandas DataFrame and save it to CSV
    df = pd.DataFrame(document_type_details)
    df.to_csv(filepath, index=False)

    # Print the number of document types saved
    print(f"✅ {len(df)} document types saved to '{filepath}'")

    # Optionally, print the first 5 rows of the DataFrame for verification
    print("\nFirst 5 rows of the document types:")
    print(df.head())

# === Execute the function ===
download_document_types()

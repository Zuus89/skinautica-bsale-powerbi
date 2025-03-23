import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import os
import time

# === Load token ===
load_dotenv(dotenv_path="config/.env")
ACCESS_TOKEN = os.getenv("BSALE_ACCESS_TOKEN")

# === Set the start and end dates for February 2025 ===
start_date = datetime(2025, 2, 1)  # February 1, 2025
end_date = datetime(2025, 2, 28)  # February 28, 2025

# Convert dates to UNIX timestamp (seconds since 1970-01-01)
start_timestamp = int(time.mktime(start_date.timetuple()))
end_timestamp = int(time.mktime(end_date.timetuple()))

# === API Configuration ===
BASE_URL = "https://api.bsale.cl/v1/documents.json"

# Parameters for the query with dates in UNIX timestamp format
params = {
    "emissiondate__gte": start_timestamp,  # Start date (February 1)
    "emissiondate__lte": end_timestamp,    # End date (February 28)
    "expand": "details",  # To expand and get details for each document
    "limit": 50,  # Limit the number of documents per request
    "offset": 0  # Pagination, starting at 0
}

headers = {
    "access_token": ACCESS_TOKEN
}

# === Download details ===
document_details = []
page_count = 0  # Initialize the page counter
document_count = 0  # Initialize the document counter
print(f"🔄 Downloading document details for February 2025...")

while True:
    response = requests.get(BASE_URL, headers=headers, params=params)

    # Check if the response is successful
    if response.status_code != 200:
        print("❌ Error:", response.status_code, response.text)
        break

    data = response.json()
    documents = data.get("items", [])
    if not documents:
        break

    page_count += 1  # Increment the page counter

    for document in documents:
        document_data = {}

        # Extract general document information
        document_data["document_id"] = document.get("id")
        document_data["emission_date"] = document.get("emissionDate")
        document_data["total_amount"] = document.get("totalAmount")
        document_data["net_amount"] = document.get("netAmount")
        document_data["tax_amount"] = document.get("taxAmount")
        document_data["address"] = document.get("address")
        document_data["municipality"] = document.get("municipality")
        document_data["city"] = document.get("city")
        document_data["state"] = document.get("state")
        document_data["number"] = document.get("number")
        document_data["expiration_date"] = document.get("expirationDate")

        # Get client_id, document_type_id, and user_id from the href
        client_url = document.get("client", {}).get("href")
        document_type_url = document.get("document_type", {}).get("href")
        user_url = document.get("user", {}).get("href")

        # Get client_id
        client_id = None
        if client_url:
            client_response = requests.get(client_url, headers=headers)
            if client_response.status_code == 200:
                client_data = client_response.json()
                client_id = client_data.get("id")

        # Get document_type_id
        document_type_id = None
        if document_type_url:
            document_type_response = requests.get(document_type_url, headers=headers)
            if document_type_response.status_code == 200:
                document_type_data = document_type_response.json()
                document_type_id = document_type_data.get("id")

        # Get user_id
        user_id = None
        if user_url:
            user_response = requests.get(user_url, headers=headers)
            if user_response.status_code == 200:
                user_data = user_response.json()
                user_id = user_data.get("id")

        # Get document details (href for details)
        details_url = document.get("details", {}).get("href")
        
        if details_url:
            details_response = requests.get(details_url, headers=headers)
            if details_response.status_code == 200:
                details_data = details_response.json()

                # If "details" has more than one item
                for detail in details_data.get("items", []):
                    # Extract specific details for the item (product)
                    variant_id = detail.get("variant", {}).get("id")
                    variant_description = detail.get("variant", {}).get("description")
                    variant_code = detail.get("variant", {}).get("code")

                    # Add the details along with the general document information
                    document_details.append({
                        "document_id": document_data["document_id"],
                        "emission_date": document_data["emission_date"],
                        "total_amount": document_data["total_amount"],
                        "net_amount": document_data["net_amount"],
                        "tax_amount": document_data["tax_amount"],
                        "address": document_data["address"],
                        "municipality": document_data["municipality"],
                        "city": document_data["city"],
                        "state": document_data["state"],
                        "number": document_data["number"],
                        "expiration_date": document_data["expiration_date"],
                        "client_id": client_id,
                        "document_type_id": document_type_id,
                        "user_id": user_id,
                        "variant_id": variant_id,
                        "variant_description": variant_description,
                        "variant_code": variant_code,
                        "quantity": detail.get("quantity", 0),
                        "unit_price": detail.get("netUnitValue", 0),
                        "net_amount_detail": detail.get("netAmount", 0),
                        "tax_amount_detail": detail.get("taxAmount", 0),
                        "total_amount_detail": detail.get("totalAmount", 0),
                    })
                    document_count += 1  # Increment the document counter

    # Show progress for each page
    print(f"📄 Page {page_count}: {document_count} documents processed.")

    # Check if there is a next page
    next_page = data.get("next")
    if not next_page:
        break
    else:
        params["offset"] += params["limit"]  # Move to the next page

# === Save CSV ===
if document_details:
    output_dir = "data/documentos/"
    os.makedirs(output_dir, exist_ok=True)

    filename = f"detalle_documentos_febrero_2025.csv"
    filepath = os.path.join(output_dir, filename)

    df = pd.DataFrame(document_details)
    df.to_csv(filepath, index=False)

    print(f"✅ {len(df)} detail lines saved in '{filepath}'")
    print(f"📊 Completed processing: {document_count} documents processed across {page_count} pages.")

    # Show the first 5 rows of the DataFrame
    print("\nFirst 5 rows of the DataFrame:")
    print(df.head())  # Display the first 5 rows of the DataFrame
else:
    print(f"⚠️ No documents were found for February 2025.")

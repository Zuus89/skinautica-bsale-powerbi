import requests
import pandas as pd
from dotenv import load_dotenv
import os
import time

# === Load the API Token from .env ===
load_dotenv(dotenv_path="config/.env")
ACCESS_TOKEN = os.getenv("BSALE_ACCESS_TOKEN")

# === Path to the 'documentos.csv' file ===
documents_file_path = "C:/Users/celto/OneDrive - Personal/OneDrive/Data/Github/skinautica-bsale-powerbi/data/documentos/documentos.csv"

# Read the documents data from the CSV file
documents_df = pd.read_csv(documents_file_path)

# === Extract the details_url and Fetch Details ===
document_details_data = []

# Initialize a counter for tracking processed documents
processed_documents = 0

for index, row in documents_df.iterrows():
    # Get the details URL for each document
    details_url = row['details_url']
    
    if details_url:
        # Send a GET request to the details URL
        response = requests.get(details_url, headers={"access_token": ACCESS_TOKEN})
        
        if response.status_code == 200:
            details_data = response.json()
            
            for item in details_data.get("items", []):
                # Extract the details for each line item in the document
                document_detail = {
                    "document_id": row["document_id"],  # Document ID from the main documents file
                    "line_number": item.get("lineNumber"),
                    "quantity": item.get("quantity"),
                    "net_unit_value": item.get("netUnitValue"),
                    "total_unit_value": item.get("totalUnitValue"),
                    "net_amount": item.get("netAmount"),
                    "tax_amount": item.get("taxAmount"),
                    "total_amount": item.get("totalAmount"),
                    "variant_id": item.get("variant", {}).get("id"),
                    "related_detail_id": item.get("relatedDetailId")
                }
                document_details_data.append(document_detail)
        
        else:
            print(f"❌ Error fetching details for document {row['document_id']}: {response.status_code}")
    
    # Increment the counter after processing each document
    processed_documents += 1

    # Print progress for every 100 documents processed
    if processed_documents % 100 == 0:
        print(f"🔄 Processed {processed_documents} documents...")

    time.sleep(1)  # Add a slight delay between requests to avoid rate limiting

# === Save Data to CSV ===
if document_details_data:
    output_dir = "C:/Users/celto/OneDrive - Personal/OneDrive/Data/Github/skinautica-bsale-powerbi/data/document_details/"
    os.makedirs(output_dir, exist_ok=True)
    
    details_file_path = os.path.join(output_dir, "document_details.csv")
    
    # Save to CSV
    details_df = pd.DataFrame(document_details_data)
    details_df.to_csv(details_file_path, index=False)
    
    print(f"✅ {len(details_df)} document details saved to '{details_file_path}'")
else:
    print("⚠️ No document details found.")

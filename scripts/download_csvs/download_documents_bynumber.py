import requests
import pandas as pd
from dotenv import load_dotenv
import os
from tkinter import Tk, Label, Entry, Button

# === Load the API Token from .env ===
load_dotenv(dotenv_path=".env")
ACCESS_TOKEN = os.getenv("BSALE_ACCESS_TOKEN")

# === Path to the 'documentos.csv' file ===
documents_file_path = "C:/Users/celto/OneDrive - Personal/OneDrive/Data/Github/skinautica-bsale-powerbi/data/documentos/documentos.csv"
document_details_file_path = "C:/Users/celto/OneDrive - Personal/OneDrive/Data/Github/skinautica-bsale-powerbi/data/document_details/document_details.csv"

# === Function to get Document Number and Type ===
def get_document_info():
    # Create a new Tkinter window
    root = Tk()
    root.title("Select Document Information")

    # Create a label for the document number
    Label(root, text="Enter Document Number:").grid(row=0, column=0, padx=10, pady=5)

    # Create the entry widget for document number
    document_number_entry = Entry(root)
    document_number_entry.grid(row=0, column=1, padx=10, pady=5)

    # Create a label for the document type
    Label(root, text="Enter Document Type:").grid(row=1, column=0, padx=10, pady=5)

    # Create the entry widget for document type
    document_type_entry = Entry(root)
    document_type_entry.grid(row=1, column=1, padx=10, pady=5)

    # Function to close the window and get the selected inputs
    def fetch_and_close():
        document_number = document_number_entry.get()
        document_type = document_type_entry.get()
        
        # Close the window after input
        root.quit()

        # Call the function to download data using the inputs
        download_data(document_number, document_type)
    
    # Add a button to fetch the data and start download
    Button(root, text="Download Data", command=fetch_and_close).grid(row=2, column=0, columnspan=2, pady=10)

    # Run the Tkinter window
    root.mainloop()

# Function to download data based on document number and type
def download_data(document_number, document_type):
    # === API Configuration ===
    BASE_URL = "https://api.bsale.cl/v1/documents.json"
    
    # Parameters for the API request based on document number and type
    params = {
        "number": document_number,  # Document number to filter by
        "documenttypeid": document_type,  # Document type to filter by
        "expand": "details",  # To expand and get the details of each document
        "limit": 50,  # Limit the number of documents per request (pagination)
        "offset": 0    # Starting point for pagination
    }
    
    headers = {
        "access_token": ACCESS_TOKEN
    }

    # === Download Documents ===
    document_details = []
    print(f"🔄 Downloading documents for document number {document_number} and document type {document_type}...")

    while True:
        response = requests.get(BASE_URL, headers=headers, params=params)

        # Check if the request was successful
        if response.status_code != 200:
            print(f"❌ Error: {response.status_code}, {response.text}")
            break

        data = response.json()
        documents = data.get("items", [])

        if not documents:
            break

        for document in documents:
            # Extract basic information about the document
            document_data = {
                "document_id": document.get("id"),
                "emission_date": document.get("emissionDate"),
                "total_amount": document.get("totalAmount"),
                "net_amount": document.get("netAmount"),
                "tax_amount": document.get("taxAmount"),
                "address": document.get("address"),
                "municipality": document.get("municipality"),
                "city": document.get("city"),
                "state": document.get("state"),
                "number": document.get("number"),
                "client_id": document.get("client", {}).get("id"),
                "document_type_id": document.get("document_type", {}).get("id"),
                "user_id": document.get("user", {}).get("id"),
                "details_url": document.get("details", {}).get("href"),  # Extract href for details
                "seller_url": document.get("sellers", {}).get("href")  # Extract href for sellers
            }

            # Now, let's fetch the seller's details using the 'sellers_url' 
            sellers_url = document_data["seller_url"]
            if sellers_url:
                seller_response = requests.get(sellers_url, headers={"access_token": ACCESS_TOKEN})

            if seller_response.status_code == 200:
                seller_data = seller_response.json()
                # Extract the seller's ID
                if seller_data.get("items"):
                    seller_id = seller_data["items"][0].get("id")
                    document_data["seller_id"] = seller_id
                else:
                    document_data["seller_id"] = None
            else:
                document_data["seller_id"] = None

            document_details.append(document_data)

        # Update the offset to fetch the next set of documents
        params["offset"] += params["limit"]

    # === Save Data to CSV ===
    if document_details:
        output_dir = "data/documentos/"
        os.makedirs(output_dir, exist_ok=True)

        filename = f"documentos_{document_number}_{document_type}.csv"
        filepath = os.path.join(output_dir, filename)

        df = pd.DataFrame(document_details)
        df.to_csv(filepath, index=False)

        print(f"✅ {len(df)} document records saved to '{filepath}'")

        # Append the newly downloaded documents to the global documentos.csv using pd.concat
        global_df = pd.read_csv(documents_file_path)
        global_df = pd.concat([global_df, df], ignore_index=True)
        global_df.to_csv(documents_file_path, index=False)

        print(f"✅ {len(df)} document records saved to '{filepath}' and appended to global documentos.csv")

        # Print the first 5 rows for verification
        print("\nFirst 5 rows of the documents data:")
        print(df.head())
    else:
        print(f"⚠️ No documents found for the given document number and document type.")

    # === Download Document Details ===
    print(f"🔄 Downloading document details for documents saved for {document_number} and {document_type}...")

    document_details_data = []
    for index, row in df.iterrows():
        details_url = row['details_url']
        
        if details_url:
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

    # === Save Document Details to CSV ===
    if document_details_data:
        details_output_dir = "data/document_details/"
        os.makedirs(details_output_dir, exist_ok=True)

        details_filename = f"document_details_{document_number}_{document_type}.csv"
        details_filepath = os.path.join(details_output_dir, details_filename)

        details_df = pd.DataFrame(document_details_data)
        details_df.to_csv(details_filepath, index=False)

        # Append the newly downloaded document details to the global document_details.csv using pd.concat
        global_details_df = pd.read_csv(document_details_file_path)
        global_details_df = pd.concat([global_details_df, details_df], ignore_index=True)
        global_details_df.to_csv(document_details_file_path, index=False)

        print(f"✅ {len(details_df)} document details saved to '{details_filepath}' and appended to global document_details.csv")
    else:
        print(f"⚠️ No document details found.")
        
# === Start the process ===
get_document_info()

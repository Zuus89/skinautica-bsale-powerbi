import requests
import pandas as pd
from dotenv import load_dotenv
import os
import time
from tkinter import Tk, Label, Button
from tkinter import messagebox
from tkcalendar import Calendar

# === Load the API Token ===
load_dotenv(dotenv_path="config/.env")
ACCESS_TOKEN = os.getenv("BSALE_ACCESS_TOKEN")

# Function to handle the date input and conversion
def get_dates():
    # Create a new Tkinter window
    root = Tk()
    root.title("Select Date Range")

    # Create a label for the start date
    Label(root, text="Select Start Date:").grid(row=0, column=0, padx=10, pady=5)

    # Create the calendar widget for start date
    start_date_picker = Calendar(root, date_pattern="yyyy-mm-dd")
    start_date_picker.grid(row=0, column=1, padx=10, pady=5)
    
    # Create a label for the end date
    Label(root, text="Select End Date:").grid(row=0, column=2, padx=10, pady=5)
    
    # Create the calendar widget for end date
    end_date_picker = Calendar(root, date_pattern="yyyy-mm-dd")
    end_date_picker.grid(row=0, column=3, padx=10, pady=5)

    # Function to close the window and get the selected dates
    def fetch_and_close():
        start_date_str = start_date_picker.get_date()
        end_date_str = end_date_picker.get_date()
        
        # Close the window after selecting the dates
        root.quit()

        # Convert selected dates to UNIX timestamps
        start_timestamp = int(time.mktime(time.strptime(start_date_str, "%Y-%m-%d")))
        end_timestamp = int(time.mktime(time.strptime(end_date_str, "%Y-%m-%d")))
        
        print(f"Start Date: {start_date_str}, End Date: {end_date_str}")
        print(f"Start Timestamp: {start_timestamp}, End Timestamp: {end_timestamp}")

        # Call the function to download data using these timestamps
        download_data(start_timestamp, end_timestamp)
    
    # Add a button to fetch the dates and start download
    Button(root, text="Download Data", command=fetch_and_close).grid(row=1, column=0, columnspan=4, pady=10)

    # Run the Tkinter window
    root.mainloop()

# Function to download data based on the date range
def download_data(start_timestamp, end_timestamp):
    # === API Configuration ===
    BASE_URL = "https://api.bsale.cl/v1/documents.json"
    
    # Parameters for the API request
    params = {
        "emissiondaterange": f"[{start_timestamp},{end_timestamp}]",  # Date range in UNIX timestamp format
        "expand": "details",  # To expand and get the details of each document
        "limit": 50,  # Limit the number of documents per request (pagination)
        "offset": 0    # Starting point for pagination
    }
    
    headers = {
        "access_token": ACCESS_TOKEN
    }

    # === Download Documents ===
    document_details = []
    print(f"🔄 Downloading documents from {start_timestamp} to {end_timestamp}...")

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
            # Extract basic document information
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

        filename = f"documentos_{start_timestamp}_to_{end_timestamp}.csv"
        filepath = os.path.join(output_dir, filename)

        df = pd.DataFrame(document_details)
        df.to_csv(filepath, index=False)

        print(f"✅ {len(df)} document records saved to '{filepath}'")

        # Print the first 5 rows for verification
        print("\nFirst 5 rows of the documents data:")
        print(df.head())
    else:
        print(f"⚠️ No documents found for the given date range.")

# === Start the process ===
get_dates()

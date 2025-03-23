# Bsale API Integration

This project connects to the Bsale API to fetch and process document types from the Bsale platform. It includes scripts to download document details and store them in a structured format (CSV) for further analysis or integration.

## Table of Contents

- [Description](#description)
- [Setup](#setup)
- [Usage](#usage)

---

## Description

This project includes a Python script that:

1. **Fetches document types** from the Bsale API.
2. **Stores the details of these document types** (e.g., `id`, `description`, `code`, `created_at`, `updated_at`) in a **CSV file**.
3. Allows easy export of Bsale document data for further processing or integration with other tools like **Power BI**.

---

### Next Steps:

In the next sections, we will cover how to set up the project, install dependencies, and run the script.

## Setup

To get started, you'll need to set up the environment and install the necessary dependencies.

### 1. Clone the repository

Run the following command to clone the repository:

git clone https://github.com/yourusername/bsale-api-integration.git

### 2. Install dependencies

Make sure you have **Python 3.x** installed on your system. Install the required libraries using **pip**:

pip install -r requirements.txt

The `requirements.txt` file contains the following dependencies:
- `requests` - For making API requests to the Bsale API.
- `pandas` - For processing and saving the data to CSV files.
- `python-dotenv` - For loading environment variables (like API tokens) securely from a `.env` file.

### 3. Set up environment variables

Create a **.env** file in the root of the project directory. This file will store your **Bsale API token**.

Example `.env` file:

BSALE_ACCESS_TOKEN=your-bsale-api-token-here

Replace `your-bsale-api-token-here` with your actual API token provided by Bsale.

## Usage

### Running the Script to Download Document Types

To fetch and save document type details from the Bsale API, simply run the `download_document_type.py` script:

python scripts/download_document_type.py

This will:

1. Download the document types data from the Bsale API.
2. Save the results in a CSV file located in the `data/document_types/` directory.
3. Display the first 5 rows of the downloaded data in the console for verification.

### File Structure

The downloaded data will be saved in the following directory:

```
data/document_types/
  └── document_types.csv  # Contains the document types data in CSV format
```


### Example of Document Type Data

The following fields will be saved in the CSV:

- **document_type_id**: The unique identifier of the document type.
- **description**: The description of the document type.
- **code**: The code of the document type.
- **created_at**: The date and time when the document type was created.
- **updated_at**: The date and time when the document type was last updated.

### Running the Script to Download Document Details (Documents)

To fetch and save document details from the Bsale API for a specific date range (e.g., February 2025), run the `download_documents.py` script:


This will:

1. Download the document details (such as `id`, `number`, `total_amount`, `net_amount`, `tax_amount`, and others) for documents created within the specified date range.
2. Fetch additional data for each document, including information about the client, document type, and user.
3. Save the results in a CSV file located in the `data/documentos/` directory.
4. Display the first 5 rows of the downloaded data in the console for verification.

---

### File Structure

The downloaded data will be saved in the following directorie:
  
- `data/documentos/`:
  - `detalle_documentos_febrero_2025.csv` - Contains the details of the documents fetched for February 2025 (or any other specified date range).

---

### Example of Document Type Data

The following fields will be saved in the **document_types.csv**:

- **document_type_id**: The unique identifier of the document type.
- **description**: The description of the document type.
- **code**: The code of the document type.
- **created_at**: The date and time when the document type was created.
- **updated_at**: The date and time when the document type was last updated.

---

### Example of Document Details Data

The following fields will be saved in the **detalle_documentos_febrero_2025.csv** (or the respective date range file):

- **document_id**: The unique identifier of the document.
- **emission_date**: The emission date of the document.
- **total_amount**: The total amount of the document.
- **net_amount**: The net amount of the document.
- **tax_amount**: The tax amount of the document.
- **address**: The address linked to the document.
- **municipality**: The municipality linked to the document.
- **state**: The state linked to the document.
- **number**: The document number.
- **client_id**: The ID of the client associated with the document.
- **document_type_id**: The ID of the document type.
- **user_id**: The ID of the user who created the document.
- **variant_id**: The ID of the product variant.
- **variant_description**: Description of the product variant.
- **variant_code**: The code of the product variant.
- **quantity**: The quantity of the product in the document.
- **unit_price**: The unit price of the product.
- **net_amount_detail**: The net amount for the product.
- **tax_amount_detail**: The tax amount for the product.
- **total_amount_detail**: The total amount for the product.

## Scripts

### `download_document_type.py`

This script is responsible for downloading document types from the Bsale API. 

It performs the following actions:

1. Sends a `GET` request to the **`/v1/document_types.json`** endpoint of the Bsale API to fetch all document types.
2. Saves the results in a **CSV** file (`document_types.csv`) located in the `data/document_types/` directory.
3. Displays the first 5 rows of the data for quick verification.

### Example Output

After running the script, you'll see the following output in your terminal:

### Example Output

After running the script, you'll see the following output in your terminal:

🔄 Downloading document types...  
✅ 5 document types saved to 
``` 
`data/document_types/document_types.csv`
```  

First 5 rows of the document types:

| document_type_id | description   | code | created_at                | updated_at                |
|------------------|---------------|------|---------------------------|---------------------------|
| 1                | Invoice Type  | 101  | 2021-01-01T12:00:00Z      | 2022-01-01T12:00:00Z      |
| 2                | Receipt Type  | 102  | 2021-02-01T12:00:00Z      | 2022-02-01T12:00:00Z      |
| ...              | ...           | ...  | ...                       | ...                       |


### `download_documents.py`

This script downloads detailed document information for a specific date range from the Bsale API. 

It performs the following actions:

1. Sends a `GET` request to the **`/v1/documents.json`** endpoint to fetch document details created within a specified date range.
2. Retrieves additional information about each document, including client information, document type, and user.
3. Downloads the details of each document using the document's `details` URL and stores them in a CSV file (`detalle_documentos_febrero_2025.csv`) located in the `data/documentos/` directory.
4. Displays the first 5 rows of the data for verification.

### Example Output

After running the script, you'll see the following output in your terminal:

### Example Output

After running the script, you'll see the following output in your terminal:

🔄 Downloading details of documents for February 2025...  
✅ 50 document details saved to 
```
data/documentos/detalle_documentos_febrero_2025.csv
```

First 5 rows of the document details:

| document_id | emission_date | total_amount | net_amount | tax_amount | address   | municipality | city   | state | number |
|-------------|---------------|--------------|------------|------------|-----------|--------------|--------|-------|--------|
| 4139        | 2025-02-01    | 5000000      | 4300000    | 700000     | Santiago  | Santiago     | RM     | Chile | 1      |
| 4140        | 2025-02-02    | 2000000      | 1900000    | 100000     | Santiago  | Santiago     | RM     | Chile | 2      |
| ...         | ...           | ...          | ...        | ...        | ...       | ...          | ...    | ...   | ...    |

### How to Run the Scripts

- **Download Document Types**:
  - To download the document types from Bsale:
    ```
    python scripts/download_document_type.py
    ```

- **Download Document Details**:
  - To download the document details for a specific date range (e.g., February 2025):
    ```
    `python scripts/download_documents.py`
    ```

Both scripts fetch data from the Bsale API and save it to CSV files for further processing.

---

Let me know if you need any further adjustments or additional sections!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgment

All code in this repository was written by **Cristóbal Elton**.

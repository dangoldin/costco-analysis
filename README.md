# Costco Analysis

This project contains scripts to fetch and analyze Costco receipt data using the Costco API. Note that you need to log in to costco.com manually and look at the network requests to get the bearer token, the client ID, and the client identifier.

## Setup

1. Install dependencies:

   ```bash
   uv sync
   ```

2. Set up environment variables:

   ```bash
   cp .env.example .env
   ```

   Then edit `.env` and add your actual Costco API credentials. You can get these by looking at the network requests in your browser when you're logged in to costco.com and looking at the headers in the graphql requests.

   - `COSTCO_BEARER_TOKEN` - Your bearer token
   - `COSTCO_CLIENT_ID` - Your client ID
   - `COSTCO_CLIENT_IDENTIFIER` - Your client identifier

## Scripts

- `fetch_receipts.py` - Fetches receipt lists for date ranges
- `fetch_receipt_details.py` - Fetches detailed receipt information by barcode
- `fetch_all_receipt_details.py` - Batch fetches detailed receipts for all barcodes found in data files

## Environment Variables

- `COSTCO_BEARER_TOKEN` - Your Costco API bearer token
- `COSTCO_CLIENT_ID` - Your Costco API client ID
- `COSTCO_CLIENT_IDENTIFIER` - Your Costco API client identifier

## Usage

All scripts will automatically load the required credentials from your `.env` file. Make sure to set up all the environment variables before running any scripts.

```bash
python fetch_receipts.py
python fetch_all_receipt_details.py
```

## CSV Export

Use the `generate_csv_file.py` script to export all receipt data to CSV:

```bash
python generate_csv_file.py
```

This script uses the following DuckDB query to process the JSON data and save as `costco-items.csv`:

```sql
WITH receipts AS (
    SELECT
    json_extract(data, '$.receiptsWithCounts.receipts[0]') AS r
    FROM read_json_auto('costco-analysis/data/receipts/*json')
)
SELECT
    r ->> 'transactionDate'      AS transaction_date,
    r ->> 'transactionBarcode'   AS transaction_barcode,
    r ->> 'warehouseName'        AS warehouse_name,
    item ->> 'itemNumber'        AS item_number,
    item ->> 'itemDescription01' AS description,
    item ->> 'itemDescription02' AS description2,
    description || ' ' || description2 AS combined_description,
    (item ->> 'itemUnitPriceAmount')::DOUBLE AS item_unit_price
FROM receipts,
        UNNEST(json_extract(r, '$.itemArray[*]')) AS t(item)
```

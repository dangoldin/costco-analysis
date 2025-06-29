# Costco Analysis

This project contains scripts to fetch and analyze Costco receipt data using the Costco API.

## Setup

1. Install dependencies:

   ```bash
   uv sync
   ```

2. Set up environment variables:

   ```bash
   cp .env.example .env
   ```

   Then edit `.env` and replace `your_bearer_token_here` with your actual Costco API bearer token.

## Scripts

- `fetch_receipt_list.py` - Fetches receipt lists for date ranges
- `fetch_receipt.py` - Fetches detailed receipt information by barcode
- `fetch_receipt_details.py` - Batch fetches detailed receipts for all barcodes found in data files

## Environment Variables

- `COSTCO_BEARER_TOKEN` - Your Costco API bearer token (required)

## Usage

All scripts will automatically load the bearer token from your `.env` file. Make sure to set up the environment variables before running any scripts.

```bash
python fetch_receipt_list.py
python fetch_receipt.py
python fetch_receipt_details.py
```

## CSV Export

TODO: Add script for this.

In the meantime, you can export the data to CSV using the following DuckDB query and save as `costco_data.csv`:

```sql
WITH receipts AS (
    SELECT
    json_extract(data, '$.receiptsWithCounts.receipts[0]') AS r
    FROM read_json_auto('costco-analysis/data/receipts/*json')
)
SELECT
    r ->> 'transactionDate'      AS transaction_date,
    r ->> 'transactionBarcode'   AS transaction_barcode,
    item ->> 'itemNumber'        AS item_number,
    item ->> 'itemDescription01' AS description,
    item ->> 'itemDescription02' AS description2,
    description || ' ' || description2 AS combined_description,
    (item ->> 'itemUnitPriceAmount')::DOUBLE AS item_unit_price
FROM receipts,
        UNNEST(json_extract(r, '$.itemArray[*]')) AS t(item)
```

#!/usr/bin/env python3
"""
Script to export Costco receipt data to CSV using DuckDB.

This script executes the SQL query defined in the README to process
JSON receipt files and export the results to costco-items.csv.
"""

from pathlib import Path

import duckdb


def generate_csv_file():
    """Generate CSV file from Costco receipt JSON data using DuckDB."""

    # Get the project root directory
    project_root = Path(__file__).parent

    # Define input and output paths
    data_dir = project_root / "data" / "receipts"
    output_file = project_root / "costco-items.csv"

    # Check if data directory exists
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    # Check if there are JSON files in the receipts directory
    json_files = list(data_dir.glob("*.json"))
    if not json_files:
        raise FileNotFoundError(f"No JSON files found in: {data_dir}")

    print(f"Found {len(json_files)} JSON files in {data_dir}")

    # Connect to DuckDB (in-memory database)
    conn = duckdb.connect()

    # SQL query from the README
    query = """
    WITH receipts AS (
        SELECT
        json_extract(data, '$.receiptsWithCounts.receipts[0]') AS r
        FROM read_json_auto('data/receipts/*.json')
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
    """

    try:
        print("Executing DuckDB query...")

        # Execute the query and export to CSV
        result = conn.execute(query)

        # Export results to CSV
        conn.execute(
            f"COPY ({query}) TO '{output_file}' (HEADER, DELIMITER ',')")
        # Get row count for confirmation
        row_count = conn.execute(
            f"SELECT COUNT(*) FROM ({query}) AS subquery").fetchone()
        if row_count is not None:
            row_count = row_count[0]
            print(f"Successfully exported {row_count:,} rows to {output_file}")
        else:
            print(
                f"Successfully exported file to {output_file}, but could not get row count")

    except Exception as e:
        print(f"Error executing query: {e}")
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    generate_csv_file()

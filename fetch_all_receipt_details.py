#!/usr/bin/env python3
"""
Script to fetch detailed receipt information for all transaction barcodes
found in the Costco data files.

This script:
1. Reads all JSON files in the data/ directory
2. Extracts all transactionBarcode values from the receipts
3. Uses fetch_receipt.py to download detailed receipt information for each barcode
4. Saves detailed receipts to data/receipts/ directory
"""

import importlib.util
import json
import os
import time
from pathlib import Path
from typing import List, Set

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import the fetch_receipt function
spec = importlib.util.spec_from_file_location(
    "fetch_receipt_details", "fetch_receipt_details.py")
if spec is None or spec.loader is None:
    raise ImportError("Could not load fetch_receipt_details.py module")
fetch_receipt_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fetch_receipt_module)


def get_transaction_barcodes_from_file(filepath: str) -> Set[str]:
    """Extract all transactionBarcode values from a single data file."""
    barcodes = set()

    try:
        with open(filepath, 'r') as f:
            data = json.load(f)

        # Navigate to the receipts array
        receipts = data.get('data', {}).get(
            'receiptsWithCounts', {}).get('receipts', [])

        for receipt in receipts:
            barcode = receipt.get('transactionBarcode')
            if barcode:
                barcodes.add(barcode)

        print(f"Found {len(barcodes)} unique barcodes in {filepath}")

    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error reading {filepath}: {e}")

    return barcodes


def get_all_transaction_barcodes(data_dir: str = "data") -> Set[str]:
    """Extract all unique transactionBarcode values from all data files."""
    all_barcodes = set()
    data_path = Path(data_dir)

    # Find all JSON files that match the pattern (excluding receipt detail files)
    json_files = [
        f for f in data_path.glob("*.json")
        if f.name.startswith("costco_data_") and not f.name.startswith("costco_data_receipt_")
    ]

    print(f"Processing {len(json_files)} data files...")

    for json_file in sorted(json_files):
        print(f"Processing: {json_file.name}")
        barcodes = get_transaction_barcodes_from_file(str(json_file))
        all_barcodes.update(barcodes)

    return all_barcodes


def get_existing_receipt_barcodes(receipts_dir: str = "data/receipts") -> Set[str]:
    """Get barcodes for receipts that have already been downloaded."""
    existing_barcodes = set()
    receipts_path = Path(receipts_dir)

    if not receipts_path.exists():
        return existing_barcodes

    # Look for files matching the pattern costco_data_receipt_*.json
    receipt_files = receipts_path.glob("costco_data_receipt_*.json")

    for receipt_file in receipt_files:
        # Extract barcode from filename: costco_data_receipt_{barcode}.json
        filename = receipt_file.name
        if filename.startswith("costco_data_receipt_") and filename.endswith(".json"):
            barcode = filename[len("costco_data_receipt_"):-len(".json")]
            existing_barcodes.add(barcode)

    return existing_barcodes


def fetch_receipt_details(
    barcodes: Set[str],
    output_dir: str = "data/receipts",
    delay_seconds: float = 1.0,
    skip_existing: bool = True
) -> None:
    """Fetch detailed receipt information for all provided barcodes."""

    # Check if bearer token is available
    bearer_token = os.getenv('COSTCO_BEARER_TOKEN')
    if not bearer_token:
        raise ValueError(
            "COSTCO_BEARER_TOKEN environment variable is required. Please set it in your .env file.")

    if skip_existing:
        existing_barcodes = get_existing_receipt_barcodes(output_dir)
        barcodes_to_fetch = barcodes - existing_barcodes

        if existing_barcodes:
            print(
                f"Skipping {len(existing_barcodes)} receipts that already exist")

        if not barcodes_to_fetch:
            print("All receipts have already been downloaded!")
            return

        barcodes = barcodes_to_fetch

    print(
        f"Fetching detailed receipt information for {len(barcodes)} barcodes...")

    successful_downloads = 0
    failed_downloads = 0

    for i, barcode in enumerate(sorted(barcodes), 1):
        print(f"\n[{i}/{len(barcodes)}] Processing barcode: {barcode}")

        try:
            success = fetch_receipt_module.fetch_costco_receipt(
                barcode, output_dir)

            if success:
                successful_downloads += 1
                print(f"✅ Successfully downloaded receipt {barcode}")
            else:
                failed_downloads += 1
                print(f"❌ Failed to download receipt {barcode}")

            # Add delay between requests to be respectful to the API
            if i < len(barcodes):  # Don't delay after the last request
                print(
                    f"Waiting {delay_seconds} seconds before next request...")
                time.sleep(delay_seconds)

        except KeyboardInterrupt:
            print(f"\n⚠️  Process interrupted by user after {i-1} receipts")
            break
        except Exception as e:
            failed_downloads += 1
            print(f"❌ Unexpected error processing barcode {barcode}: {e}")

    print(f"\n📊 Summary:")
    print(f"   • Successful downloads: {successful_downloads}")
    print(f"   • Failed downloads: {failed_downloads}")
    print(f"   • Total processed: {successful_downloads + failed_downloads}")


def main():
    """Main function to orchestrate the receipt fetching process."""
    print("🔍 Costco Receipt Details Fetcher")
    print("=" * 50)

    # Step 1: Extract all transaction barcodes
    print("\n📂 Step 1: Extracting transaction barcodes from data files...")
    all_barcodes = get_all_transaction_barcodes()

    if not all_barcodes:
        print("❌ No transaction barcodes found in data files!")
        return

    print(f"✅ Found {len(all_barcodes)} unique transaction barcodes")

    # Step 2: Fetch detailed receipt information
    print(f"\n📥 Step 2: Fetching detailed receipt information...")
    fetch_receipt_details(all_barcodes)

    print(f"\n🎉 Process completed!")


if __name__ == "__main__":
    main()

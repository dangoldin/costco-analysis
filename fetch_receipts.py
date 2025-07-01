import json
import os
from datetime import datetime, timedelta

import requests
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def generate_quarters(start_date, end_date):
    """Generate quarterly date ranges from start_date to end_date"""
    quarters = []
    current = start_date

    while current < end_date:
        # Calculate quarter end (3 months later, minus 1 day)
        quarter_end = current + relativedelta(months=3) - timedelta(days=1)
        if quarter_end > end_date:
            quarter_end = end_date

        quarters.append((current, quarter_end))
        current = current + relativedelta(months=3)

    return quarters


def fetch_costco_data(start_date, end_date, output_dir="data"):
    """Fetch Costco receipt data for the given date range"""

    # Get bearer token from environment
    bearer_token = os.getenv('COSTCO_BEARER_TOKEN')
    if not bearer_token:
        raise ValueError(
            "COSTCO_BEARER_TOKEN environment variable is required. Please set it in your .env file.")

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    url = "https://ecom-api.costco.com/ebusiness/order/v1/orders/graphql"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:140.0) Gecko/20100101 Firefox/140.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'costco.service': 'restOrders',
        'costco.env': 'ecom',
        'costco-x-authorization': f'Bearer {bearer_token}',
        'Content-Type': 'application/json-patch+json',
        'costco-x-wcs-clientId': os.getenv('COSTCO_CLIENT_ID'),
        'client-identifier': os.getenv('COSTCO_CLIENT_IDENTIFIER'),
        'Origin': 'https://www.costco.com',
        'DNT': '1',
        'Sec-GPC': '1',
        'Connection': 'keep-alive',
        'Referer': 'https://www.costco.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site'
    }

    query = """query receiptsWithCounts($startDate: String!, $endDate: String!,$documentType:String!,$documentSubType:String!) {
    receiptsWithCounts(startDate: $startDate, endDate: $endDate,documentType:$documentType,documentSubType:$documentSubType) {
    inWarehouse
    gasStation
    carWash
    gasAndCarWash
    receipts{
    warehouseName receiptType  documentType transactionDateTime transactionBarcode warehouseName transactionType total
    totalItemCount
    itemArray {
      itemNumber
    }
    tenderArray {
      tenderTypeCode
      tenderDescription
      amountTender
    }
    couponArray {
      upcnumberCoupon
    }
  }
}
  }"""

    # Format dates for the API (M/DD/YYYY format)
    start_str = start_date.strftime("%-m/%d/%Y")
    end_str = end_date.strftime("%-m/%d/%Y")

    payload = {
        "query": query,
        "variables": {
            "startDate": start_str,
            "endDate": end_str,
            "text": f"{start_str} to {end_str}",
            "documentType": "all",
            "documentSubType": "all"
        }
    }

    try:
        print(f"Fetching data for {start_str} to {end_str}...")
        print(f"Request URL: {url}")
        print(f"Request payload: {json.dumps(payload, indent=2)}")

        response = requests.post(url, headers=headers, json=payload)

        print(f"Response status: {response.status_code}")
        if response.status_code != 200:
            print(f"Response headers: {dict(response.headers)}")
            print(f"Response body: {response.text[:500]}...")

        response.raise_for_status()

        # Generate filename based on date range
        filename = f"costco_data_{start_date.strftime('%Y-%m-%d')}_to_{end_date.strftime('%Y-%m-%d')}.json"
        filepath = os.path.join(output_dir, filename)

        # Save the response data
        with open(filepath, 'w') as f:
            json.dump(response.json(), f, indent=2)

        print(f"Data saved to {filepath}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {start_str} to {end_str}: {e}")
        return False


def test_single_request():
    """Test a single request to verify token and setup"""
    test_start = datetime(2024, 12, 1)
    test_end = datetime(2024, 12, 31)

    print("Testing single request first...")
    success = fetch_costco_data(test_start, test_end)

    if success:
        print("✅ Single request test passed! Token appears to be valid.")
        return True
    else:
        print("❌ Single request test failed. Check token and headers.")
        return False


def main():
    # Test single request first
    if not test_single_request():
        print("Exiting due to failed test request.")
        return

    # Define date range - starting with a recent date to test if token is valid
    start_date = datetime(2020, 1, 1)
    end_date = datetime.now()

    # Generate quarterly date ranges
    quarters = generate_quarters(start_date, end_date)

    print(
        f"Fetching data for {len(quarters)} quarters from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

    successful_fetches = 0
    total_quarters = len(quarters)

    for i, (quarter_start, quarter_end) in enumerate(quarters, 1):
        print(f"\nProcessing quarter {i}/{total_quarters}")
        if fetch_costco_data(quarter_start, quarter_end):
            successful_fetches += 1

        # Add a small delay between requests to be respectful
        import time
        time.sleep(1)

    print(
        f"\nCompleted: {successful_fetches}/{total_quarters} quarters successfully fetched")


if __name__ == "__main__":
    main()

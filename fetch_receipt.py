import json
import os
from datetime import datetime

import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def fetch_costco_receipt(barcode, output_dir="data/receipts"):
    """Fetch a single Costco receipt by barcode"""

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
        'Sec-Fetch-Site': 'same-site',
        'Priority': 'u=0'
    }

    query = """query receiptsWithCounts($barcode: String!,$documentType:String!) {
    receiptsWithCounts(barcode: $barcode,documentType:$documentType) {
receipts{
      warehouseName
      receiptType
      documentType
      transactionDateTime
      transactionDate
      companyNumber
      warehouseNumber
      operatorNumber
      warehouseName
      warehouseShortName
      registerNumber
      transactionNumber
      transactionType
      transactionBarcode
      total
      warehouseAddress1
      warehouseAddress2
      warehouseCity
      warehouseState
      warehouseCountry
      warehousePostalCode
      totalItemCount
      subTotal
      taxes
      total
      invoiceNumber
      sequenceNumber
      itemArray {
        itemNumber
        itemDescription01
        frenchItemDescription1
        itemDescription02
        frenchItemDescription2
        itemIdentifier
        itemDepartmentNumber
        unit
        amount
        taxFlag
        merchantID
        entryMethod
        transDepartmentNumber
        fuelUnitQuantity
        fuelGradeCode
        fuelUnitQuantity
        itemUnitPriceAmount
        fuelUomCode
        fuelUomDescription
        fuelUomDescriptionFr
        fuelGradeDescription
        fuelGradeDescriptionFr

      }
      tenderArray {
        tenderTypeCode
        tenderSubTypeCode
        tenderDescription
        amountTender
        displayAccountNumber
        sequenceNumber
        approvalNumber
        responseCode
        tenderTypeName
         transactionID
         merchantID
         entryMethod
         tenderAcctTxnNumber
         tenderAuthorizationCode
         tenderTypeName
         tenderTypeNameFr
         tenderEntryMethodDescription
         walletType
         walletId
         storedValueBucket
      }
        subTaxes {
          tax1
          tax2
          tax3
          tax4
          aTaxPercent
          aTaxLegend
          aTaxAmount
          aTaxPrintCode
          aTaxPrintCodeFR
          aTaxIdentifierCode
          bTaxPercent
          bTaxLegend
          bTaxAmount
          bTaxPrintCode
          bTaxPrintCodeFR
          bTaxIdentifierCode
          cTaxPercent
          cTaxLegend
          cTaxAmount
          cTaxIdentifierCode
          dTaxPercent
          dTaxLegend
          dTaxAmount
          dTaxPrintCode
          dTaxPrintCodeFR
          dTaxIdentifierCode
          uTaxLegend
          uTaxAmount
          uTaxableAmount
        }
        instantSavings
        membershipNumber
    }
  }
 }"""

    payload = {
        "query": query,
        "variables": {
            "barcode": barcode,
            "documentType": "warehouse"
        }
    }

    try:
        print(f"Fetching receipt for barcode: {barcode}")
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

        # Generate filename based on barcode
        filename = f"costco_data_receipt_{barcode}.json"
        filepath = os.path.join(output_dir, filename)

        # Save the response data
        with open(filepath, 'w') as f:
            json.dump(response.json(), f, indent=2)

        print(f"Receipt data saved to {filepath}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"Error fetching receipt for barcode {barcode}: {e}")
        return False


def main():
    """Example usage - fetch a receipt by barcode"""
    # Example barcode from the curl command
    test_barcode = "21133401100522303241037"

    print(f"Fetching receipt for barcode: {test_barcode}")
    success = fetch_costco_receipt(test_barcode)

    if success:
        print("✅ Receipt fetched successfully!")
    else:
        print("❌ Failed to fetch receipt.")


if __name__ == "__main__":
    # You can either run main() for the example, or call fetch_costco_receipt() directly
    # with your own barcode
    main()

    # Or use it like this:
    # fetch_costco_receipt("your_barcode_here")

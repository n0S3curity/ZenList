# api_routes.py
import traceback
from urllib.parse import urlparse, parse_qs

import requests
from flask import Blueprint
from flask import request, jsonify

from server.helpers import *

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/list', methods=['GET'])
def get_shopping_list():
    """Returns the content of list.json (the shopping list)."""
    # In a real app, you'd load this from your List.json file
    return jsonify(shopping_list_data)


@api_bp.route('/stats', methods=['GET'])
def get_stats():
    with open('../databases/stats.json', 'r', encoding='utf-8') as f:
        stats_data = json.load(f)
    return jsonify(stats_data)


@api_bp.route('/stats/<barcode>', methods=['GET'])
def get__product_stats(barcode):
    with open('../databases/products.json', 'r', encoding='utf-8') as f:
        stats_data = json.load(f)
    if barcode in stats_data.keys():
        product_stats = stats_data[barcode]
        # Return only the stats of the product with the given barcode
        return jsonify(product_stats), 200
    return jsonify({"error": f"Product with barcode '{barcode}' not found."}), 404


@api_bp.route('/products', methods=['GET'])
def get_products():
    with open('../databases/products.json', 'r', encoding='utf-8') as f:
        products_data = json.load(f)
    return jsonify(products_data)


@api_bp.route('/receipts', methods=['GET'])
def get_receipts_list():
    """Returns a JSON list of the contents of the 'Receipts' folder."""
    # In a real app, you'd scan the Receipts directory
    return jsonify(receipts_folder_content)


@api_bp.route('/product/add', methods=['POST'])
def add_product_to_list():
    """Adds a product name to the 'list.json' (shopping list)."""
    data = request.get_json()
    product_name = data.get('productName')
    if product_name:
        # In a real app, you'd update your List.json file
        shopping_list_data.append({"productName": product_name, "quantity": 1, "done": False})
        return jsonify({"message": f"Product '{product_name}' added to list."}), 201
    return jsonify({"error": "Product name is required."}), 400


@api_bp.route('/product/remove', methods=['POST'])
def remove_product_from_list():
    """Removes a product from the 'list.json' (shopping list)."""
    data = request.get_json()
    product_name = data.get('productName')
    if product_name:
        global shopping_list_data
        initial_len = len(shopping_list_data)
        shopping_list_data = [item for item in shopping_list_data if item['productName'] != product_name]
        if len(shopping_list_data) < initial_len:
            return jsonify({"message": f"Product '{product_name}' removed from list."}), 200
        return jsonify({"error": f"Product '{product_name}' not found in list."}), 404
    return jsonify({"error": "Product name is required."}), 400


@api_bp.route('/product/quantity', methods=['POST'])
def update_product_quantity():
    """Updates the quantity of a product on the 'list.json' (shopping list)."""
    data = request.get_json()
    product_name = data.get('productName')
    quantity = data.get('quantity')
    if product_name and isinstance(quantity, int) and quantity >= 0:
        for item in shopping_list_data:
            if item['productName'] == product_name:
                item['quantity'] = quantity
                return jsonify({"message": f"Quantity for '{product_name}' updated to {quantity}."}), 200
        return jsonify({"error": f"Product '{product_name}' not found in list."}), 404
    return jsonify({"error": "Product name and valid quantity are required."}), 400


@api_bp.route('/product/<barcode>/settings', methods=['GET'])
def get_product_settings(barcode):
    # from products.json return only the settings of the product with the given barcode
    barcode = request.view_args.get('barcode')
    if not barcode:
        return jsonify({"error": "Barcode is required."}), 400
    with open('../databases/products.json', 'r', encoding='utf-8') as f:
        products_data = json.load(f)
    if barcode in products_data.keys():
        product = products_data[barcode]
        settings = product.get('settings', {})
        settings['barcode'] = product['barcode']
        settings['name'] = product['name']
        return jsonify(settings), 200
    return jsonify({"error": f"Product with barcode '{barcode}' not found."}), 404


@api_bp.route('/receipt/<receipt_name>', methods=['GET'])
def get_receipt_by_name(receipt_name):
    """Gets a receipt by its name and returns it as JSON."""
    # In a real app, you'd load this from your Receipts folder
    # For simplicity, let's just return a mock receipt structure
    mock_receipt = {
        "name": receipt_name,
        "date": "2025-07-29",
        "total": 100.00,
        "items": [
            {"product": "Milk", "price": 5.00, "quantity": 1},
            {"product": "Bread", "price": 10.00, "quantity": 1}
        ]
    }
    return jsonify(mock_receipt)


@api_bp.route('/receipt/download', methods=['GET'])
def download_receipt_pdf():
    """Downloads the PDF of a receipt by its transaction ID."""
    transaction_id = request.args.get('transactionID')
    if transaction_id:
        # In a real app, you'd generate or retrieve the PDF and send it
        return jsonify({"message": f"Downloading PDF for transaction ID: {transaction_id}"}), 200
    return jsonify({"error": "Transaction ID is required."}), 400


@api_bp.route('/fetchReceipt', methods=['POST'])
def fetch_receipt():
    data = request.get_json()
    raw_url = data.get('url')
    if not raw_url:
        # Return an error if no URL is provided in the request
        return jsonify({"error": "URL is required in the request body."}), 400

    try:
        # Step 1: Follow the redirect to get the actual document URL
        redirect_response = requests.get(raw_url, allow_redirects=True)
        final_url = redirect_response.url

        # Step 2: Parse the redirected URL to extract query parameters
        parsed_url = urlparse(final_url)
        query_params = parse_qs(parsed_url.query)
        doc_id = query_params.get('id', [''])[0]
        p_param = query_params.get('p', [''])[0]

        if not doc_id:
            return jsonify({"error": "Could not extract document ID from redirected URL."}), 400

        # Step 3: Construct the final document fetch URL
        base_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
        converted_url = f"{base_domain}/v1.0/documents/{doc_id}"
        if p_param:
            converted_url += f"?p={p_param}"

        # Step 4: Fetch the receipt data from the converted URL
        response = requests.get(converted_url)

        if response.status_code == 200:
            # Parse the JSON content from the response
            receipt_json = response.json()
            print(f"Fetched receipt data: {receipt_json}")
            company_name = ""
            if 'osher' in final_url:
                company_name = "osherad"
            elif 'yohananof' in final_url:
                company_name = "yohananof"

            # Use the value from 'additionalInfo' as the filename, as requested
            try:
                filename_value = receipt_json['additionalInfo'][0]['value'].replace("@", "")
                print(f"Extracted filename value: {filename_value}")
                receipt_filename = f"{filename_value}.json"

            except (KeyError, TypeError):
                # Handle cases where the key might not exist or the structure is different
                return jsonify({"error": "Could not find 'additionalInfo.value' in receipt data."}), 500
            city_english = "Unknown City"  # Default value in case we can't determine the city
            try:
                # Identify the store name from the receipt
                city_hebrew = receipt_json['store']['name']
                print(f"Branch identified: {city_hebrew}")

                # using a dictionary, which is more reliable than a generic web search
                with open('../databases/cities.json', 'r', encoding='utf-8') as f:
                    city_translation_map = json.load(f)

                # Look up the city in the translation map
                city_english = city_translation_map.get(city_hebrew, "Unknown City")
                print(f"Hebrew city '{city_hebrew}' translated to English city '{city_english}'.")

            except KeyError:
                # Handle cases where the branch name is not available in the JSON
                print("Branch name not found in receipt data.")

            # Step 5: Save the receipt to the designated path
            save_path = f"../receipts/{company_name}/{city_english}/{receipt_filename}".lower()
            # if os.path.exists(save_path):
            #     # If the file already exists, we can either overwrite or skip
            #     print(f"File {save_path} already exists. exiting")
            #     return jsonify({"error": f"receipt number {receipt_filename} already exists."}), 400

            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(receipt_json, f, ensure_ascii=False, indent=4)

            process_receipt_file(save_path)  # This is a placeholder function, you need to implement it.

            return jsonify({
                "message": "Receipt fetched and processed successfully.",
                "converted_url": converted_url,
                "saved_filename": receipt_filename.split('.')[0],  # Return the filename without extension  ),
            }), 200
        else:
            # Handle cases where the fetch from the converted URL failed
            return jsonify({
                "error": f"Failed to download receipt from {converted_url}",
                "status_code": response.status_code
            }), response.status_code

    except requests.exceptions.RequestException as e:
        # Catch network-related errors during the fetch
        return jsonify({"error": f"Network error during receipt fetch: {str(e)}"}), 500
    except Exception as e:
        # Catch any other unexpected errors
        return jsonify({"error": f"Error processing receipt: {str(e)}", "stacktrace": traceback.format_exc()}), 500

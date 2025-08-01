# api_routes.py
from urllib.parse import urlparse, parse_qs

import requests
from flask import Blueprint
from flask import request, jsonify

from server.helpers import *

api_bp = Blueprint('api', __name__, url_prefix='/api')

# For demonstration purposes, let's assume these are loaded from your JSON files
products_data = [
    {"id": "1", "name": "Milk", "barcode": "12345", "category": "Dairy"},
    {"id": "2", "name": "Bread", "barcode": "67890", "category": "Bakery"},
    {"id": "3", "name": "Apples", "barcode": "11223", "category": "Fruits"}
]

shopping_list_data = [
    {"productName": "Milk", "quantity": 1, "done": False},
    {"productName": "Bread", "quantity": 1, "done": False}
]

receipts_folder_content = {
    "osherad": ["receipt1.json", "receipt2.json"],
    "yohananof": ["receiptA.json"]
}


# --- API Endpoints ---

@api_bp.route('/list', methods=['GET'])
def get_shopping_list():
    """Returns the content of list.json (the shopping list)."""
    # In a real app, you'd load this from your List.json file
    return jsonify(shopping_list_data)


@api_bp.route('/products', methods=['GET'])
def get_products():
    """Returns the content of products.json."""
    # In a real app, you'd load this from your Products.json file
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


@api_bp.route('/product/settings', methods=['GET'])
def get_product_settings():
    """Returns the product with its settings."""
    product_name = request.args.get('product')
    if product_name:
        # In a real app, you'd fetch settings from products.json or a dedicated settings store
        product = next((p for p in products_data if p['name'] == product_name), None)
        if product:
            return jsonify(product), 200
        return jsonify({"error": f"Product '{product_name}' not found."}), 404
    return jsonify({"error": "Product name parameter is required."}), 400


@api_bp.route('/product/settings', methods=['POST'])
def update_product_settings():
    """Updates the settings of a product."""
    data = request.get_json()
    product_name = data.get('productName')
    settings = data.get('settings')
    if product_name and settings:
        # In a real app, you'd update settings in products.json
        for product in products_data:
            if product['name'] == product_name:
                product.update(settings)  # Simple update, extend as needed
                return jsonify({"message": f"Settings for '{product_name}' updated."}), 200
        return jsonify({"error": f"Product '{product_name}' not found."}), 404
    return jsonify({"error": "Product name and settings are required."}), 400


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
            save_path = f"Receipts/{company_name}/{city_english}/{receipt_filename}".lower()
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
        return jsonify({"error": f"Error processing receipt: {str(e)}"}), 500


def process_receipt_file(file_path):

    print(f"Processing receipt file: {file_path}")

    # Load the receipt content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            receipt_content = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading receipt file {file_path}: {e}")
        return

    # Initialize empty databases if they don't exist
    products_db_path = '../databases/products.json'
    stats_db_path = '../databases/stats.json'

    if not os.path.exists(os.path.dirname(products_db_path)):
        os.makedirs(os.path.dirname(products_db_path))

    try:
        with open(products_db_path, 'r', encoding='utf-8') as f:
            products = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        products = {}  # Initialize as an empty dictionary

    try:
        with open(stats_db_path, 'r', encoding='utf-8') as f:
            stats = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        stats = {
            "total_receipts": 0,
            "total_spent": 0,
            "total_items": 0,
            "average_spend_per_receipt": 0,
            "top_10_product_purchased": [],
            "top_10_price_increase": [],
            "receipts": {}
        }  # Initialize with default values

    date_and_time = receipt_content.get('createdDate', 'Unknown Date and Time').replace("T", " ")

    # Process each item in the receipt
    for item in receipt_content.get('items', []):
        barcode = item.get('code')
        product_name = item.get('name')
        price = item.get('price')
        quantity = item.get('quantity')
        total = item.get('total')

        # Check if product exists in the products database
        if barcode in products:
            # Update existing product
            product_data = products[barcode]
            product_data['total_quantity'] = product_data.get('total_quantity', 0) + quantity
            product_data['total_price'] = product_data.get('total_price', 0) + total

            # Update price history and min/max prices
            current_price = price
            cheapest_price = product_data.get('cheapest_price', current_price)
            highest_price = product_data.get('highest_price', current_price)
            last_price = product_data.get('last_price', current_price)

            # Update price increase before setting new last price
            if cheapest_price > 0:
                product_data['price_increase'] = ((last_price - cheapest_price) / cheapest_price) * 100

            product_data['last_price'] = current_price
            product_data['cheapest_price'] = min(cheapest_price, current_price)
            product_data['highest_price'] = max(highest_price, current_price)

            # Add to purchase history
            history = product_data.get('history', [])
            history.append({
                "date": date_and_time,
                "quantity": quantity,
                "price": price
            })
            product_data['history'] = history
        else:
            # Add new product
            products[barcode] = {
                "barcode": barcode,
                "name": product_name,
                "price": price,
                "total_quantity": quantity,
                "total_price": total,
                "history": [{
                    "date": date_and_time,
                    "quantity": quantity,
                    "price": price
                }],
                "cheapest_price": price,
                "highest_price": price,
                "price_increase": 0,
                "last_price": price
            }

    # Update stats.json
    total_receipt_price = receipt_content.get('total', 0)
    number_of_items = receipt_content.get('numberOfItems', 0)
    receipt_barcode = receipt_content.get('barcode', 'Unknown Barcode')

    stats['total_receipts'] += 1
    stats['total_spent'] += total_receipt_price
    stats['total_items'] += number_of_items
    stats['average_spend_per_receipt'] = stats['total_spent'] / stats['total_receipts'] if stats[
                                                                                               'total_receipts'] > 0 else 0

    # Sort products for top 10 purchased
    top_10_product_purchased = sorted(
        products.values(),
        key=lambda x: x.get('total_quantity', 0),
        reverse=True
    )[:10]
    stats['top_10_product_purchased'] = top_10_product_purchased

    # Calculate and update top 10 price increases
    top_10_price_increase = calculate_top_10_price_increase(products)
    stats['top_10_price_increase'] = top_10_price_increase

    stats['receipts'][receipt_barcode] = {
        "total_price": total_receipt_price,
        "date_and_time": date_and_time
    }

    # Save the updated databases
    try:
        with open(products_db_path, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=4)
        print("Updated products.json successfully.")

        with open(stats_db_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=4)
        print("Updated stats.json successfully.")
    except IOError as e:
        print(f"Error saving database files: {e}")

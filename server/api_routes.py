# api_routes.py
from flask import Blueprint, jsonify, request

# Create a Blueprint instance
# The first argument is the blueprint's name (used internally)
# The second argument is the import name, which Flask uses to locate resources
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Example data (replace with actual database/file loading)
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
    """
    Gets a URL from the body, converts it, downloads the receipt,
    saves it, and triggers processing.
    """
    data = request.get_json()
    raw_url = data.get('url')
    if not raw_url:
        return jsonify({"error": "URL is required in the request body."}), 400

    # Example URL conversion logic
    # This is a simplified example; real parsing might be more complex
    try:
        # Extract ID and p parameter from the original URL
        from urllib.parse import urlparse, parse_qs
        parsed_url = urlparse(raw_url)
        query_params = parse_qs(parsed_url.query)
        doc_id = query_params.get('id', [''])[0]
        p_param = query_params.get('p', [''])[0]

        if not doc_id:
            return jsonify({"error": "Could not extract document ID from URL."}), 400

        # Construct the new URL
        base_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
        converted_url = f"{base_domain}/v1.0/documents/{doc_id}"
        if p_param:
            converted_url += f"?p={p_param}"

        # Simulate downloading and saving the file
        # In a real application, you would use requests.get() to download
        # and then save the content to your 'receipts' folder.
        # Example:
        # import requests
        # response = requests.get(converted_url)
        # if response.status_code == 200:
        #     company_name = "osherad" # You'd extract this from the URL or receipt content
        #     receipt_filename = f"{doc_id}.json"
        #     save_path = f"Receipts/{company_name}/{receipt_filename}"
        #     os.makedirs(os.path.dirname(save_path), exist_ok=True)
        #     with open(save_path, 'w', encoding='utf-8') as f:
        #         json.dump(response.json(), f, ensure_ascii=False, indent=4)
        #     # Trigger processing flow (mocked here)
        #     process_receipt_file(save_path)
        #     return jsonify({"message": "Receipt fetched and processed successfully.", "converted_url": converted_url}), 200
        # else:
        #     return jsonify({"error": f"Failed to download receipt from {converted_url}", "status_code": response.status_code}), response.status_code

        # For demonstration, just return the converted URL
        return jsonify({"message": "Simulated receipt fetch and processing.", "converted_url": converted_url}), 200

    except Exception as e:
        return jsonify({"error": f"Error processing URL: {str(e)}"}), 500


def process_receipt_file(file_path):
    """
    Simulates the processing flow for a receipt file.
    Opens the receipt file and for each item, if barcode doesn't exist
    on products.json, adds to products.json.
    """
    print(f"Processing receipt file: {file_path}")
    # In a real app:
    # 1. Load receipt JSON from file_path
    # 2. Iterate through 'items'
    # 3. Check if barcode exists in products_data (or actual products.json)
    # 4. If not, add new product to products_data (and save to products.json)
    # Example:
    # with open(file_path, 'r', encoding='utf-8') as f:
    #     receipt_content = json.load(f)
    # for item in receipt_content.get('items', []):
    #     barcode = item.get('barcode')
    #     product_name = item.get('productName')
    #     if barcode and product_name and not any(p['barcode'] == barcode for p in products_data):
    #         products_data.append({"id": str(len(products_data) + 1), "name": product_name, "barcode": barcode, "category": ""})
    #         # Save updated products_data to Products.json
    #         print(f"Added new product: {product_name} ({barcode})")
    pass  # Placeholder for actual processing logic

# api_routes.py
import traceback
from urllib.parse import urlparse, parse_qs

import requests
from flask import Blueprint, send_file
from flask import request, jsonify

from helpers import *

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/list', methods=['GET'])
def get_shopping_list():
    with open('../databases/list.json', 'r', encoding='utf-8') as f:
        shopping_list = json.load(f)
    with open('../databases/categories.json', 'r', encoding='utf-8') as f:
        categories = json.load(f)
    shopping_list['categories'] = categories
    # add also the suggestions from suggestions.json
    with open('../databases/suggestions.json', 'r', encoding='utf-8') as f:
        suggestions = json.load(f)
        # print(suggestions)
    shopping_list['suggestions'] = suggestions["items"]
    return jsonify(shopping_list)


@api_bp.route('/list/add', methods=['POST'])
def add_item_to_list():
    with open('../databases/list.json', 'r', encoding='utf-8') as f:
        item_list = json.load(f)

    item_name = request.get_json().get('item', '').strip()
    quantity = request.get_json().get('quantity', 1)
    category = request.get_json().get('category', 'כללי')

    # Check if item name already exists in the list (by name, not by ID)
    for item in item_list.values():
        if item['name'] == item_name:
            return jsonify({"error": f"Item already exists in the list. on {item['category']}"}), 400

    # --- Handle categories ---
    with open('../databases/categories.json', 'r', encoding='utf-8') as f:
        categories = json.load(f)

    if category not in categories:
        categories[category] = category
        with open('../databases/categories.json', 'w', encoding='utf-8') as f:
            json.dump(categories, f, ensure_ascii=False, indent=4)

    # --- Handle suggestions ---
    with open('../databases/suggestions.json', 'r', encoding='utf-8') as f:
        suggestions = json.load(f)

    if item_name not in suggestions["items"]:
        suggestions["items"].append(item_name)
        with open('../databases/suggestions.json', 'w', encoding='utf-8') as f:
            json.dump(suggestions, f, ensure_ascii=False, indent=4)

    # --- Create and add item ---
    item = {
        "id": generate_item_id(),
        "name": item_name,
        "done": False,
        "quantity": quantity,
        "category": category
    }

    item_list[item['id']] = item

    with open('../databases/list.json', 'w', encoding='utf-8') as f:
        json.dump(item_list, f, ensure_ascii=False, indent=4)

    return jsonify({"message": f"Item '{item['id']}' added to the list."}), 201

@api_bp.route('/list/remove', methods=['POST'])
def remove_product_from_list():
    with open('../databases/list.json', 'r', encoding='utf-8') as f:
        l = json.load(f)
    itemID = request.get_json()['itemID']
    if itemID not in l:
        return jsonify({"error": "Item not found in the list."}), 404
    del l[itemID]
    with open('../databases/list.json', 'w', encoding='utf-8') as f:
        json.dump(l, f, ensure_ascii=False, indent=4)
    return jsonify({"message": f"Item removed from the list."}), 200


@api_bp.route('/list/quantity', methods=['POST'])
def change_product_quantity():
    with open('../databases/list.json', 'r', encoding='utf-8') as f:
        l = json.load(f)
    itemID = request.get_json()['itemID']
    new_quantity = request.get_json()['quantity']
    if itemID not in l:
        return jsonify({"error": "Item not found in the list."}), 404
    if not isinstance(new_quantity, int) or new_quantity < 0:
        return jsonify({"error": "Quantity must be a non-negative integer."}), 400
    l[itemID]['quantity'] = new_quantity
    with open('../databases/list.json', 'w', encoding='utf-8') as f:
        json.dump(l, f, ensure_ascii=False, indent=4)
    return jsonify({"message": f"Quantity for item '{itemID}' updated to {new_quantity}."}), 200


@api_bp.route('/list/done', methods=['POST'])
def set_item_as_done():
    with open('../databases/list.json', 'r', encoding='utf-8') as f:
        l = json.load(f)
    itemID = str(request.get_json()['itemID'])
    print(f"Incoming itemID: {itemID}, Current list keys: {l.keys()}")
    if itemID not in l.keys():
        print(f"DEBUG: Item ID '{itemID}' not found in list, returning 404.")  # Add this line
        return jsonify({"error": "Item not found in the list."}), 404
    l[itemID]['done'] = True
    with open('../databases/list.json', 'w', encoding='utf-8') as f:
        json.dump(l, f, ensure_ascii=False, indent=4)
    print(f"DEBUG: Item ID '{itemID}' marked as done, returning 200.")  # Add this line
    return jsonify({"message": f"Item marked as done."}), 200


@api_bp.route('/list/undone', methods=['POST'])
def set_item_as_undone():
    with open('../databases/list.json', 'r', encoding='utf-8') as f:
        l = json.load(f)
    itemID = request.get_json()['itemID']
    if itemID not in l:
        return jsonify({"error": "Item not found in the list."}), 404
    l[itemID]['done'] = False
    with open('../databases/list.json', 'w', encoding='utf-8') as f:
        json.dump(l, f, ensure_ascii=False, indent=4)
    return jsonify({"message": f"Item marked as undone."}), 200


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


@api_bp.route('/receipts', methods=['GET'])
def get_receipts_list():
    """Returns a list of all receipts. list all files of the receipts folder, keep on hierarchy, and return as JSON.
    :return as: {
    "companyName": {"cityName": ["receipt1.json", "receipt2.json", ...], ...},....
    for every receipt, open the file and select from the json the following fields:
    total, createdDate. and attach it to the json
    }
    """
    receipts = []
    base_path = '../receipts'
    try:
        for company_name in os.listdir(base_path):
            company_path = os.path.join(base_path, company_name)
            if os.path.isdir(company_path):
                for city_name in os.listdir(company_path):
                    city_path = os.path.join(company_path, city_name)
                    if os.path.isdir(city_path):
                        for receipt_file in os.listdir(city_path):
                            if receipt_file.endswith('.json'):
                                receipt_path = os.path.join(city_path, receipt_file)
                                with open(receipt_path, 'r', encoding='utf-8') as f:
                                    receipt_data = json.load(f)
                                    receipts.append({
                                        "company": "אושר עד" if company_name == "osherad" else "יוחננוף" if company_name == "yohananof" else company_name,
                                        "city": get_hebrew_city_name(city_name),
                                        "file": receipt_file.replace('.json', ''),
                                        "total": receipt_data.get('total', 0),
                                        "createdDate": receipt_data.get('createdDate', 'Unknown')
                                    })
    except Exception as e:
        return jsonify({"error": f"Error reading receipts directory: {str(e)}"}), 500
    return jsonify(receipts), 200


@api_bp.route('/receipts/<receipt_number>/download', methods=['GET'])
def download_receipt(receipt_number):
    base_path = '../original_receipts_backup'
    try:
        print("Searching for receipt:", receipt_number + '.pdf', "in path:", os.listdir(base_path))
        filename = receipt_number + '.pdf'
        if filename in os.listdir(base_path):
            receipt_path = os.path.join(base_path, filename)
            return send_file(receipt_path, as_attachment=True,
                             download_name=f'{generate_receipt_filename()}.pdf')
        else:
            return jsonify({"error": f"Receipt '{receipt_number}' not found."}), 404
    except Exception as e:
        return jsonify({"error": f"Error reading receipts directory: {str(e)}"}), 500


@api_bp.route('/receipts/<receipt_number>/show', methods=['GET'])
def show_receipt(receipt_number):
    base_path = '../original_receipts_backup'
    try:
        print("Searching for receipt:", receipt_number + '.pdf', "in path:", os.listdir(base_path))
        filename = receipt_number + '.pdf'
        if filename in os.listdir(base_path):
            receipt_path = os.path.join(base_path, filename)
            # Return the PDF file directly
            return send_file(receipt_path, as_attachment=False,
                             download_name=f'{generate_receipt_filename()}.pdf')
        else:
            return jsonify({"error": f"Receipt '{receipt_number}' not found."}), 404
    except Exception as e:
        return jsonify({"error": f"Error reading receipts directory: {str(e)}"}), 500


@api_bp.route('/products', methods=['GET'])
def get_products():
    with open('../databases/products.json', 'r', encoding='utf-8') as f:
        products_data = json.load(f)
    return jsonify(products_data)


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
        print(f"Converted URL: {converted_url}")

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
                # download original receipt for original_receipts_backup
                original_receipt_path = f"https://pdf.pairzon.com/pdf/{doc_id}/{p_param}"
                print(f"downloading original receipt for backup - {original_receipt_path}")
                # save the original receipt as pdf to ../receipts/original_receipts_backup
                original_receipt_response = requests.get(original_receipt_path)
                if original_receipt_response.status_code == 200:
                    original_receipt_filename = f"original_receipt_{doc_id}_{p_param}.pdf"
                    original_receipt_save_path = f"../original_receipts_backup/{filename_value}.pdf"
                    os.makedirs(os.path.dirname(original_receipt_save_path), exist_ok=True)
                    with open(original_receipt_save_path, 'wb') as f:
                        f.write(original_receipt_response.content)
                    print(f"Original receipt saved to {original_receipt_save_path}")
            except requests.exceptions.RequestException as e:
                print(f"Error downloading original receipt: {str(e)}")
                return jsonify({"error": f"Failed to download original receipt: {str(e)}"}), 500

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
            if os.path.exists(save_path):
                # If the file already exists, we can either overwrite or skip
                print(f"File {save_path} already exists. exiting")
                return jsonify({"error": f"receipt number {receipt_filename} already exists."}), 400

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

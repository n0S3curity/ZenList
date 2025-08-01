import json
import os


def calculate_top_10_price_increase(products):
    # return list of top 10 products with the highest value of "price_increase" value
    sorted_products = sorted(products, key=lambda x: x.get('price_increase', 0), reverse=True)
    top_10 = sorted_products[:10]
    return top_10


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

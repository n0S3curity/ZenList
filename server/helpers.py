import json
import os


def calculate_top_10_price_increase(products):
    price_increases = []
    # Iterate over the values (the product dictionaries) of the products dictionary
    for barcode, product in products.items():
        if barcode == "901046":
            # Skip the product with barcode "901046"
            continue
        cheapest_price = product.get('cheapest_price')
        last_price = product.get('last_price')

        # Calculate price increase only if both prices are valid and cheapest_price is not zero
        if cheapest_price is not None and last_price is not None and cheapest_price > 0:
            price_increase_percent = ((last_price - cheapest_price) / cheapest_price) * 100
            price_increases.append({
                "name": product['name'],
                "barcode": barcode,
                "price_increase": price_increase_percent,
                "old_price": cheapest_price,
                "new_price": last_price
            })

    # Sort by price increase percentage in descending order and take the top 10
    return sorted(price_increases, key=lambda x: x['price_increase'], reverse=True)[:10]


# --- Main function to process a single receipt file ---
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

    # Define a default stats dictionary to ensure all keys are present
    default_stats = {
        "total_receipts": 0,
        "total_spent": 0.0,
        "total_items": 0,
        "average_spend_per_receipt": 0.0,
        "top_10_product_purchased": [],
        "top_10_price_increase": [],
        "receipts": {}
    }
    stats = default_stats.copy()

    # Load existing stats from file, if it exists
    try:
        with open(stats_db_path, 'r', encoding='utf-8') as f:
            existing_stats = json.load(f)
        stats.update(existing_stats)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    # Load existing products from file, if it exists
    try:
        with open(products_db_path, 'r', encoding='utf-8') as f:
            products = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        products = {}  # Initialize as an empty dictionary

    date_and_time = receipt_content.get('createdDate', 'Unknown Date and Time').replace("T", " ")

    # Process each item in the receipt
    for item in receipt_content.get('items', []):
        barcode = item.get('code')
        product_name = item.get('name')
        price = item.get('price')
        quantity = item.get('quantity', 1)
        total = item.get('total')

        # Robust check to ensure all critical fields exist before conversion
        if not all([barcode, product_name, price is not None, quantity is not None, total is not None]):
            print(f"Skipping malformed item: {item}")
            continue

        # Convert to appropriate types
        try:
            price = float(price)
            quantity = int(quantity)
            total = float(total)
        except (ValueError, TypeError) as e:
            print(f"Skipping item due to invalid number format: {item}, Error: {e}")
            continue

        # Check if product exists in the products database
        if barcode in products:
            # Update existing product
            product_data = products[barcode]
            product_data['total_quantity'] = int(product_data.get('total_quantity', 0)) + quantity
            product_data['total_price'] = float(product_data.get('total_price', 0.0)) + total

            # Update price history and min/max prices
            current_price = price
            cheapest_price = float(product_data.get('cheapest_price', current_price))
            highest_price = float(product_data.get('highest_price', current_price))
            last_price = float(product_data.get('last_price', current_price))

            # Update price increase before setting new last price
            if cheapest_price > 0:
                product_data['price_increase'] = ((last_price - cheapest_price) / cheapest_price) * 100
            else:
                product_data['price_increase'] = 0.0

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
            if barcode == "901046":
                # Skip the product with barcode "901046"
                continue
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
                "price_increase": 0.0,
                "last_price": price
            }

    # Update stats.json
    total_receipt_price = receipt_content.get('total', 0.0)
    number_of_items = int(receipt_content.get('numberOfItems', 0))
    receipt_barcode = receipt_content.get('barcode', 'Unknown Barcode')

    stats['total_receipts'] += 1
    stats['total_spent'] += total_receipt_price
    stats['total_items'] += number_of_items
    stats['average_spend_per_receipt'] = stats['total_spent'] / stats['total_receipts'] if stats[
                                                                                               'total_receipts'] > 0 else 0.0

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

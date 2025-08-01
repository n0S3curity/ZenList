# frontend_routes.py
from flask import Blueprint, redirect, url_for, render_template

# Create a Blueprint for frontend routes
# We'll set a url_prefix of '/' to indicate these are root-level routes,
# but you could also omit it if you prefer.
frontend_bp = Blueprint('frontend', __name__, url_prefix='/')


# --- Frontend API Endpoints (these would typically render HTML) ---

# This will be your new root route for the frontend
@frontend_bp.route('/')
def home_page():
    """
    The main landing page for the frontend, which redirects to the shopping list.
    """
    # Assuming 'shopping_list_page' is the function name for the /list route
    # within this 'frontend_bp' blueprint.
    return redirect(url_for('frontend.shopping_list_page'))


@frontend_bp.route('/list', methods=['GET'])
def shopping_list_page():
    return render_template('list.html')

@frontend_bp.route('/stats', methods=['GET'])
def overall_stats_page():
    """
    Shows overall shop stats.
    In a real app, this would fetch data from backend APIs
    and then render an HTML template.
    """
    # return render_template('stats.html')
    return "<h1>Overall Shop Statistics</h1><p>Displaying overall statistics here. (Frontend)</p>"


@frontend_bp.route('/stats/<product_barcode>', methods=['GET'])
def specific_product_stats_page(product_barcode):
    """
    Shows specific product stats by barcode.
    In a real app, this would fetch data from backend APIs using the barcode
    and then render an HTML template.
    """
    # return render_template('product_stats.html', barcode=product_barcode)
    return f"<h1>Statistics for Product Barcode: {product_barcode}</h1><p>Displaying specific product statistics here. (Frontend)</p>"


@frontend_bp.route('/receipts', methods=['GET'])
def receipts_list_page():
    """
    Displays a list of receipts available by company and branch.
    In a real app, this would fetch data from /api/receipts
    and then render an HTML template.
    """
    return render_template('receipts.html')


@frontend_bp.route('/receipts/<receipt_name>', methods=['GET'])
def display_receipt_page(receipt_name):
    """
    Displays the receipt itself as designed HTML.
    In a real app, this would fetch data from /api/receipt/{receipt_name}
    and then render an HTML template to display the receipt.
    """
    # return render_template('receipt_detail.html', receipt_name=receipt_name)
    return f"<h1>Receipt: {receipt_name}</h1><p>Displaying the detailed receipt content. (Frontend)</p>"


@frontend_bp.route('/products', methods=['GET'])
def products_list_page():
    """
    Displays the products list with search filter by name, barcode.
    Has a button (camera icon) that triggers barcode scanner.
    In a real app, this would fetch data from /api/products
    and then render an HTML template.
    """
    return render_template('products.html')


# Assuming 'frontend_bp' is a Blueprint for your frontend routes
@frontend_bp.route('/product/<product_barcode>/settings', methods=['GET'])
def product_settings_page(product_barcode):
    """
    Lets the user update settings of a product.
    This route captures the product barcode from the URL path.
    In a real app, this would fetch product settings from the backend
    and then render an HTML form for updating.
    """
    if product_barcode:
        # Here you would use the 'product_barcode' to fetch data,
        # for example, by sending a request to your API.
        # This is the correct way to access the barcode from the URL path.
        #
        # Example for a real app:
        # product_data = get_product_data_by_barcode(product_barcode)
        # return render_template('product_settings.html', product=product_data)

        # For demonstration, we'll return a string with the captured barcode.
        return render_template('settings.html', barcode=product_barcode)

    # This return statement is now less likely to be reached,
    # as the route requires a barcode in the URL.
    return "<h1>Product Settings</h1><p>Please specify a product barcode to view/edit its settings. (Frontend)</p>"

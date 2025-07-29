# main.py
from flask import Flask

from api_routes import api_bp  # Import your blueprint
from frontend_routes import frontend_bp  # Import your frontend blueprint


def main():
    app = Flask(__name__)

    # Register the Blueprint
    # All routes defined in api_bp will now be accessible under the /api prefix
    app.register_blueprint(api_bp)
    app.register_blueprint(frontend_bp)

    # listen on all ips
    app.run(host='0.0.0.0', debug=True, port=5000)


if __name__ == '__main__':
    main()

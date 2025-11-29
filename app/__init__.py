"""Application factory for the Cognito demo API."""

from flask import Flask
from flask_cors import CORS
from flasgger import Swagger

from .config import settings
from .routes import register_blueprints
from .swagger import build_swagger_template


def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = settings.flask_secret_key

    CORS(app, resources={r"/*": {"origins": "*"}}, allow_headers=["Content-Type", "Authorization"], methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"])

    # Ensure CORS headers are added even for errors or unhandled routes
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS,PATCH')
        return response

    # Disable the favicon to prevent the UnicodeDecodeError with aws-wsgi
    swagger_config = Swagger.DEFAULT_CONFIG
    swagger_config["favicon"] = ""

    Swagger(
        app,
        template=build_swagger_template(settings),
        config=swagger_config
    )
    register_blueprints(app)
    return app


app = create_app()

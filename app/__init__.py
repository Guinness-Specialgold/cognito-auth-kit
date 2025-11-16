"""Application factory for the Cognito demo API."""

from flask import Flask
from flasgger import Swagger

from .config import settings
from .routes import register_blueprints
from .swagger import build_swagger_template


def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = settings.flask_secret_key

    Swagger(app, template=build_swagger_template(settings))
    register_blueprints(app)
    return app


app = create_app()

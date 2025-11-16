"""Blueprint registration."""

from .password import bp as password_bp
from .profile import bp as profile_bp
from .registration import bp as registration_bp
from .session import bp as session_bp
from .social import bp as social_bp


def register_blueprints(app):
    app.register_blueprint(registration_bp)
    app.register_blueprint(session_bp)
    app.register_blueprint(password_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(social_bp)

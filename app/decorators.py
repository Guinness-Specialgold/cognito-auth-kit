"""Shared Flask decorators."""

from functools import wraps
from flask import jsonify, request

from .cognito import verify_jwt


def require_bearer_token(fn):
    """Verify Bearer token and store token + claims on the request."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error": "Missing Bearer token"}), 401

        token = auth.split(" ", 1)[1]
        try:
            claims = verify_jwt(token)
        except Exception as exc:  # passthrough error message for debugging
            return jsonify({"error": f"Invalid token: {exc}"}), 401

        request.token = token
        request.claims = claims
        return fn(*args, **kwargs)

    return wrapper

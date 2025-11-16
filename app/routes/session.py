"""Session/login endpoints."""

from flask import Blueprint, jsonify, request

from ..cognito import cognito, get_secret_hash
from ..config import settings
from ..decorators import require_bearer_token


bp = Blueprint("session", __name__)


@bp.route("/auth/login", methods=["POST"])
def login():
    """
    Login with email + password using Cognito USER_PASSWORD_AUTH.
    ---
    tags:
      - Session
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/LoginRequest'
        examples:
          application/json:
            email: new.user@example.com
            password: Str0ngP@ssw0rd!
    responses:
      200:
        description: Tokens from Cognito.
        schema:
          $ref: '#/definitions/TokenResponse'
      400:
        description: Missing payload or unexpected error.
        schema:
          $ref: '#/definitions/ErrorResponse'
      401:
        description: Wrong password.
        schema:
          $ref: '#/definitions/ErrorResponse'
      403:
        description: User not confirmed yet.
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "email and password required"}), 400

    try:
        resp = cognito.initiate_auth(
            ClientId=settings.client_id,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": email,
                "PASSWORD": password,
                "SECRET_HASH": get_secret_hash(email),
            },
        )
    except cognito.exceptions.NotAuthorizedException:
        return jsonify({"error": "Incorrect email or password"}), 401
    except cognito.exceptions.UserNotConfirmedException:
        return jsonify({"error": "User not confirmed"}), 403
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    result = resp.get("AuthenticationResult", {})
    return jsonify({
        "access_token": result.get("AccessToken"),
        "id_token": result.get("IdToken"),
        "refresh_token": result.get("RefreshToken"),
        "expires_in": result.get("ExpiresIn"),
        "token_type": result.get("TokenType"),
    })


@bp.route("/auth/refresh", methods=["POST"])
def refresh_tokens():
    """
    Refresh tokens using a refresh_token.
    ---
    tags:
      - Session
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/RefreshRequest'
        examples:
          application/json:
            email: new.user@example.com
            refresh_token: <REFRESH_TOKEN>
    responses:
      200:
        description: New tokens minted with the refresh token.
        schema:
          $ref: '#/definitions/TokenResponse'
      400:
        description: Missing fields or invalid request.
        schema:
          $ref: '#/definitions/ErrorResponse'
      401:
        description: Refresh token expired or revoked.
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
    data = request.get_json() or {}
    email = data.get("email")
    refresh_token = data.get("refresh_token")

    if not email or not refresh_token:
        return jsonify({"error": "email and refresh_token required"}), 400

    try:
        resp = cognito.initiate_auth(
            ClientId=settings.client_id,
            AuthFlow="REFRESH_TOKEN_AUTH",
            AuthParameters={
                "REFRESH_TOKEN": refresh_token,
                "SECRET_HASH": get_secret_hash(email),
            },
        )
    except cognito.exceptions.NotAuthorizedException:
        return jsonify({"error": "Invalid refresh token"}), 401
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    result = resp.get("AuthenticationResult", {})
    return jsonify({
        "access_token": result.get("AccessToken"),
        "id_token": result.get("IdToken"),
        "expires_in": result.get("ExpiresIn"),
        "token_type": result.get("TokenType"),
    })


@bp.route("/me", methods=["GET"])
@require_bearer_token
def me():
    """
    Protected endpoint – requires Bearer token from /auth/login.
    ---
    tags:
      - Session
    produces:
      - application/json
    security:
      - bearerAuth: []
    parameters:
      - in: header
        name: Authorization
        required: true
        description: Format `Bearer <access_token>` returned by `/auth/login`.
        type: string
        default: "Bearer <ACCESS_TOKEN>"
    responses:
      200:
        description: Decoded token claims.
        schema:
          $ref: '#/definitions/ClaimsResponse'
      401:
        description: Missing or invalid token.
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
    return jsonify({"claims": request.claims})

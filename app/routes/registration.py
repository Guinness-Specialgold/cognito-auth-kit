"""Registration endpoints."""

from flask import Blueprint, jsonify, request

from ..cognito import cognito, get_secret_hash
from ..config import settings


bp = Blueprint("registration", __name__)


@bp.route("/auth/signup", methods=["POST"])
def signup():
    """
    Sign up a new user (no UI, pure API).
    ---
    tags:
      - Registration
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        description: Email becomes the Cognito username.
        required: true
        schema:
          $ref: '#/definitions/SignupRequest'
        examples:
          application/json:
            email: new.user@example.com
            password: Str0ngP@ssw0rd!
    responses:
      200:
        description: Signup initiated and verification code sent.
        schema:
          $ref: '#/definitions/SignupResponse'
      400:
        description: Missing or invalid payload.
        schema:
          $ref: '#/definitions/ErrorResponse'
      409:
        description: User already exists.
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "email and password required"}), 400

    try:
        resp = cognito.sign_up(
            ClientId=settings.client_id,
            SecretHash=get_secret_hash(email),
            Username=email,
            Password=password,
            UserAttributes=[{"Name": "email", "Value": email}],
        )
    except cognito.exceptions.UsernameExistsException:
        return jsonify({"error": "User already exists"}), 409
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify({
        "message": "Signup ok",
        "userSub": resp.get("UserSub"),
        "userConfirmed": resp.get("UserConfirmed"),
        "codeDelivery": resp.get("CodeDeliveryDetails"),
    })


@bp.route("/auth/confirm", methods=["POST"])
def confirm_signup():
    """
    Confirm user with the code they received from Cognito.
    ---
    tags:
      - Registration
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/ConfirmRequest'
        examples:
          application/json:
            email: new.user@example.com
            code: 123456
    responses:
      200:
        description: Account confirmed.
        schema:
          $ref: '#/definitions/MessageResponse'
      400:
        description: Invalid confirmation code or payload.
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
    data = request.get_json() or {}
    email = data.get("email")
    code = data.get("code")

    if not email or not code:
        return jsonify({"error": "email and code required"}), 400

    try:
        cognito.confirm_sign_up(
            ClientId=settings.client_id,
            SecretHash=get_secret_hash(email),
            Username=email,
            ConfirmationCode=code,
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify({"message": "Account confirmed"})

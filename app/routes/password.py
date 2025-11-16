"""Password recovery endpoints."""

from flask import Blueprint, jsonify, request

from ..cognito import cognito, get_secret_hash
from ..config import settings


bp = Blueprint("password", __name__)


@bp.route("/auth/forgot-password", methods=["POST"])
def forgot_password():
    """
    Start reset password flow – sends code by email/SMS.
    ---
    tags:
      - Password
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/ForgotPasswordRequest'
        examples:
          application/json:
            email: new.user@example.com
    responses:
      200:
        description: Reset code sent if account exists.
        schema:
          $ref: '#/definitions/ForgotPasswordResponse'
      400:
        description: Invalid payload or Cognito error.
        schema:
          $ref: '#/definitions/ErrorResponse'
      404:
        description: User not found (only returned for debugging configs).
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
    data = request.get_json() or {}
    email = data.get("email")
    if not email:
        return jsonify({"error": "email required"}), 400

    try:
        resp = cognito.forgot_password(
            ClientId=settings.client_id,
            Username=email,
            SecretHash=get_secret_hash(email),
        )
    except cognito.exceptions.UserNotFoundException:
        return jsonify({"error": "User not found"}), 404
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify({
        "message": "If the account exists, a reset code has been sent",
        "codeDelivery": resp.get("CodeDeliveryDetails"),
    })


@bp.route("/auth/reset-password", methods=["POST"])
def reset_password():
    """
    Complete reset password with code + new password.
    ---
    tags:
      - Password
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/ResetPasswordRequest'
        examples:
          application/json:
            email: new.user@example.com
            code: 123456
            new_password: EvenStrongerP@ss1
    responses:
      200:
        description: Password reset successful.
        schema:
          $ref: '#/definitions/MessageResponse'
      400:
        description: Invalid code or weak password.
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
    data = request.get_json() or {}
    email = data.get("email")
    code = data.get("code")
    new_password = data.get("new_password")

    if not email or not code or not new_password:
        return jsonify({"error": "email, code and new_password required"}), 400

    try:
        cognito.confirm_forgot_password(
            ClientId=settings.client_id,
            Username=email,
            ConfirmationCode=code,
            Password=new_password,
            SecretHash=get_secret_hash(email),
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify({"message": "Password reset successful"})

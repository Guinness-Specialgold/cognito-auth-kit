"""Profile endpoints that read/write Cognito user attributes."""

from flask import Blueprint, jsonify, request

from ..cognito import cognito
from ..decorators import require_bearer_token


bp = Blueprint("profile", __name__)


@bp.route("/profile", methods=["GET"])
@require_bearer_token
def get_profile():
    """
    Get current user's attributes from Cognito.
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
        description: Current user attributes from Cognito.
        schema:
          $ref: '#/definitions/ProfileAttributesResponse'
      401:
        description: Missing or invalid token.
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
    resp = cognito.get_user(AccessToken=request.token)
    attrs = {a["Name"]: a["Value"] for a in resp.get("UserAttributes", [])}
    return jsonify({"attributes": attrs})


@bp.route("/profile", methods=["POST"])
@require_bearer_token
def update_profile():
    """
    Update current user's attributes in Cognito.
    ---
    tags:
      - Session
    consumes:
      - application/json
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
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/ProfileUpdateRequest'
        examples:
          application/json:
            name: Ismail Amouma
            given_name: Ismail
            family_name: Amouma
            phone_number: "+212600000000"
            'custom:role': admin
    responses:
      200:
        description: Profile updated.
        schema:
          $ref: '#/definitions/MessageResponse'
      400:
        description: No valid attributes or invalid payload.
        schema:
          $ref: '#/definitions/ErrorResponse'
      401:
        description: Missing or invalid token.
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
    data = request.get_json() or {}

    allowed_keys = {
        "name",
        "given_name",
        "family_name",
        "phone_number",
        "address",
        "custom:role",
    }

    user_attrs = [
        {"Name": key, "Value": str(value)}
        for key, value in data.items()
        if key in allowed_keys and value is not None
    ]

    if not user_attrs:
        return jsonify({"error": "No valid attributes to update"}), 400

    cognito.update_user_attributes(
        AccessToken=request.token,
        UserAttributes=user_attrs,
    )

    return jsonify({"message": "Profile updated"})

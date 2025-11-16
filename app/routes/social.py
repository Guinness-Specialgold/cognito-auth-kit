"""Google social login via Cognito hosted UI."""

from urllib.parse import urlencode

import requests
from flask import Blueprint, jsonify, redirect, request, url_for

from ..config import settings


bp = Blueprint("social", __name__)


@bp.route("/auth/google/start", methods=["GET"])
def google_start():
    """
    Kick off Google sign-in through Cognito hosted UI.
    ---
    tags:
      - Social
    produces:
      - application/json
    responses:
      302:
        description: Redirect to Cognito `/oauth2/authorize` with Google as IdP.
        headers:
          Location:
            type: string
            description: URL for Cognito hosted UI where the user completes Google login.
      400:
        description: Misconfiguration preventing OAuth redirect.
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
    redirect_uri = url_for("social.google_callback", _external=True)

    params = {
        "client_id": settings.client_id,
        "response_type": "code",
        "scope": "openid email",
        "redirect_uri": redirect_uri,
        "identity_provider": "Google",
    }
    url = f"{settings.cognito_domain}/oauth2/authorize?{urlencode(params)}"
    return redirect(url)


@bp.route("/auth/google/callback", methods=["GET"])
def google_callback():
    """
    Handle OAuth2 callback from Cognito after Google login.
    ---
    tags:
      - Social
    produces:
      - application/json
    parameters:
      - in: query
        name: code
        type: string
        description: Authorization code to exchange for Cognito tokens.
      - in: query
        name: state
        type: string
        description: Optional state value propagated from `/auth/google/start`.
      - in: query
        name: error
        type: string
        description: Error returned by Cognito/Google when consent fails.
      - in: query
        name: error_description
        type: string
        description: Human description for the OAuth error.
    responses:
      200:
        description: Cognito tokens for the Google-authenticated user.
        schema:
          $ref: '#/definitions/TokenResponse'
      400:
        description: Error after redirect or missing/invalid `code`.
        schema:
          $ref: '#/definitions/OAuthErrorResponse'
    """
    error = request.args.get("error")
    error_description = request.args.get("error_description")
    if error:
        return jsonify({"error": error, "error_description": error_description}), 400

    code = request.args.get("code")
    if not code:
        return jsonify({"error": "Missing code parameter"}), 400

    redirect_uri = url_for("social.google_callback", _external=True)

    token_url = f"{settings.cognito_domain}/oauth2/token"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": settings.client_id,
        "client_secret": settings.client_secret,
        "redirect_uri": redirect_uri,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    resp = requests.post(token_url, data=data, headers=headers, timeout=10)
    if not resp.ok:
        return jsonify({"error": "Token exchange failed", "details": resp.text}), 400

    tokens = resp.json()
    return jsonify({
        "access_token": tokens.get("access_token"),
        "id_token": tokens.get("id_token"),
        "refresh_token": tokens.get("refresh_token"),
        "expires_in": tokens.get("expires_in"),
        "token_type": tokens.get("token_type"),
    })

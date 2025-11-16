"""Cognito helpers shared across routes."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
from typing import Any, Dict

import boto3
import requests
import jwt
from jwt.algorithms import RSAAlgorithm

from .config import settings


cognito = boto3.client("cognito-idp", region_name=settings.cognito_region)

_jwks_cache: Dict[str, Any] | None = None
ISSUER = f"https://cognito-idp.{settings.cognito_region}.amazonaws.com/{settings.user_pool_id}"
JWKS_URL = f"{ISSUER}/.well-known/jwks.json"


def get_jwks() -> Dict[str, Any]:
    global _jwks_cache
    if _jwks_cache is None:
        _jwks_cache = requests.get(JWKS_URL, timeout=10).json()
    return _jwks_cache


def verify_jwt(token: str) -> Dict[str, Any]:
    """Verify an ID or access token from this user pool."""

    jwks = get_jwks()
    headers = jwt.get_unverified_header(token)
    kid = headers["kid"]
    key = next(k for k in jwks["keys"] if k["kid"] == kid)
    public_key = RSAAlgorithm.from_jwk(json.dumps(key))

    return jwt.decode(
        token,
        public_key,
        algorithms=["RS256"],
        audience=settings.client_id,
        issuer=ISSUER,
    )


def get_secret_hash(username: str) -> str:
    msg = (username + settings.client_id).encode("utf-8")
    key = settings.client_secret.encode("utf-8")
    digest = hmac.new(key, msg, hashlib.sha256).digest()
    return base64.b64encode(digest).decode("utf-8")

"""Swagger template factory."""

from __future__ import annotations

from typing import Dict, Any


def build_swagger_template(settings) -> Dict[str, Any]:
    return {
        "swagger": "2.0",
        "info": {
            "title": "Cognito Auth Demo",
            "version": "1.0.0",
            "description": (
                "Endpoints to walk through Cognito user registration, login, "
                "refresh, password recovery and federated login."
            ),
            "contact": {"name": "Platform Team", "email": "platform@example.com"},
        },
        "schemes": ["http", "https"],
        "basePath": "/",
        "tags": [
            {
                "name": "Registration",
                "description": "Signup flows: create account and confirm email codes",
            },
            {
                "name": "Session",
                "description": "Login, refresh tokens and view the authenticated profile",
            },
            {
                "name": "Password",
                "description": "Password recovery and reset endpoints",
            },
            {
                "name": "Social",
                "description": "Federated login via Google using Cognito hosted UI",
            },
        ],
        "securityDefinitions": {
            "bearerAuth": {
                "description": (
                    "Copy the `access_token` from `/auth/login` and paste it as "
                    "`Bearer <token>`."
                ),
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
            }
        },
        "definitions": {
            "SignupRequest": {
                "type": "object",
                "required": ["email", "password"],
                "properties": {
                    "email": {"type": "string", "example": "new.user@example.com"},
                    "password": {"type": "string", "example": "Str0ngP@ssw0rd!"},
                },
            },
            "SignupResponse": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "userSub": {"type": "string"},
                    "userConfirmed": {"type": "boolean"},
                    "codeDelivery": {"type": "object"},
                },
                "example": {
                    "message": "Signup ok",
                    "userSub": "8f524bb7-bc8c-4b74-b9b1-bf8fb1c9eb98",
                    "userConfirmed": False,
                    "codeDelivery": {
                        "AttributeName": "email",
                        "DeliveryMedium": "EMAIL",
                        "Destination": "n***@example.com",
                    },
                },
            },
            "ProfileUpdateRequest": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "example": "Ismail Amouma"},
                    "given_name": {"type": "string", "example": "Ismail"},
                    "family_name": {"type": "string", "example": "Amouma"},
                    "phone_number": {"type": "string", "example": "+212600000000"},
                    "custom:role": {"type": "string", "example": "admin"},
                },
                "example": {
                    "name": "Ismail Amouma",
                    "given_name": "Ismail",
                    "family_name": "Amouma",
                    "phone_number": "+212600000000",
                    "custom:role": "admin",
                },
            },
            "ProfileAttributesResponse": {
                "type": "object",
                "properties": {
                    "attributes": {
                        "type": "object",
                        "additionalProperties": {"type": "string"},
                    }
                },
                "example": {
                    "attributes": {
                        "sub": "12345678-aaaa-bbbb-cccc-1234567890ab",
                        "email": "user@example.com",
                        "email_verified": "true",
                        "name": "Ismail Amouma",
                        "custom:role": "admin",
                    }
                },
            },
            "ConfirmRequest": {
                "type": "object",
                "required": ["email", "code"],
                "properties": {
                    "email": {"type": "string", "example": "new.user@example.com"},
                    "code": {"type": "string", "example": "123456"},
                },
            },
            "LoginRequest": {
                "type": "object",
                "required": ["email", "password"],
                "properties": {
                    "email": {"type": "string", "example": "new.user@example.com"},
                    "password": {"type": "string", "example": "Str0ngP@ssw0rd!"},
                },
            },
            "TokenResponse": {
                "type": "object",
                "properties": {
                    "access_token": {"type": "string"},
                    "id_token": {"type": "string"},
                    "refresh_token": {"type": "string"},
                    "expires_in": {"type": "integer"},
                    "token_type": {"type": "string", "example": "Bearer"},
                },
                "example": {
                    "access_token": "<ACCESS_TOKEN>",
                    "id_token": "<ID_TOKEN>",
                    "refresh_token": "<REFRESH_TOKEN>",
                    "expires_in": 3600,
                    "token_type": "Bearer",
                },
            },
            "RefreshRequest": {
                "type": "object",
                "required": ["email", "refresh_token"],
                "properties": {
                    "email": {"type": "string", "example": "new.user@example.com"},
                    "refresh_token": {"type": "string", "example": "<REFRESH_TOKEN>"},
                },
            },
            "ForgotPasswordRequest": {
                "type": "object",
                "required": ["email"],
                "properties": {
                    "email": {"type": "string", "example": "new.user@example.com"},
                },
            },
            "ForgotPasswordResponse": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "codeDelivery": {"type": "object"},
                },
                "example": {
                    "message": "If the account exists, a reset code has been sent",
                    "codeDelivery": {
                        "AttributeName": "email",
                        "DeliveryMedium": "EMAIL",
                        "Destination": "n***@example.com",
                    },
                },
            },
            "ResetPasswordRequest": {
                "type": "object",
                "required": ["email", "code", "new_password"],
                "properties": {
                    "email": {"type": "string"},
                    "code": {"type": "string", "example": "123456"},
                    "new_password": {"type": "string", "example": "EvenStrongerP@ss1"},
                },
            },
            "ClaimsResponse": {
                "type": "object",
                "properties": {
                    "claims": {"type": "object"},
                },
                "example": {
                    "claims": {
                        "aud": settings.client_id,
                        "email": "new.user@example.com",
                        "token_use": "id",
                    }
                },
            },
            "MessageResponse": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                },
                "example": {"message": "Account confirmed"},
            },
            "ErrorResponse": {
                "type": "object",
                "properties": {
                    "error": {"type": "string"},
                },
                "example": {"error": "email and password required"},
            },
            "OAuthErrorResponse": {
                "type": "object",
                "properties": {
                    "error": {"type": "string"},
                    "error_description": {"type": "string"},
                },
                "example": {
                    "error": "access_denied",
                    "error_description": "User closed Google consent screen",
                },
            },
        },
    }

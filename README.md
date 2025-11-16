# Cognito Auth Demo API

A Flask application that exercises every Cognito authentication flow: email/password signup, confirmation, login, refresh, password recovery, profile updates and Google (federated) login. The project is wired with Flasgger so the same Swagger definition used by AWS Lambda can be browsed locally at `/apidocs`.

## Prerequisites

- Python 3.11 (matches the AWS Lambda runtime targeted by `main.py`)
- AWS credentials with permission to call the target Cognito User Pool (configure via `aws configure` or the standard `AWS_*` environment variables)
- A Cognito User Pool client that has a secret and hosted UI configured for Google login

## Required environment variables

| Name | Purpose |
| --- | --- |
| `FLASK_SECRET_KEY` | Secret key for Flask sessions and CSRF protection. |
| `COGNITO_REGION` | AWS region where the User Pool lives (e.g. `us-east-1`). |
| `USER_POOL_ID` | Cognito User Pool ID. |
| `CLIENT_ID` | User Pool App Client ID. |
| `CLIENT_SECRET` | User Pool App Client secret (used for secret hash and OAuth exchange). |
| `COGNITO_DOMAIN` | Fully qualified hosted UI domain such as `https://your-domain.auth.<region>.amazoncognito.com`. |

> Note: Boto3 will automatically read AWS credentials from `~/.aws/credentials`, environment variables, or an attached IAM role when the code runs inside Lambda.

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# set environment variables, e.g.
export FLASK_SECRET_KEY=dev
export COGNITO_REGION=us-east-1
export USER_POOL_ID=us-east-1_XXXX
export CLIENT_ID=xxxxxxxx
export CLIENT_SECRET=yyyyyyyy
export COGNITO_DOMAIN=https://your-domain.auth.us-east-1.amazoncognito.com
```

## Running locally

```bash
python main.py
```

- The API listens on `http://127.0.0.1:5000`.
- Interactive docs powered by Flasgger are available at `http://127.0.0.1:5000/apidocs`.
- To test protected endpoints, first call `/auth/login` to obtain an access token. Supply it as `Authorization: Bearer <token>`.

## Deploying to AWS Lambda

The repository already exposes a Lambda-compatible handler via `main.lambda_handler`. Package the code plus dependencies (e.g. with AWS SAM, Serverless Framework or `lambda_package.zip`) and deploy using the Python 3.11 runtime. Ensure the Lambda function has outbound network access to Cognito and that its execution role can call `cognito-idp`.

## REST API reference

The table below mirrors the `app/swagger.py` definition. Unless stated otherwise, all bodies and responses are JSON.

### Registration

#### `POST /auth/signup`
- **Description:** Creates a new Cognito user. Cognito emails a confirmation code.
- **Body:** 
```json
{
  "email": "new.user@example.com",
  "password": "Str0ngP@ssw0rd!"
}
```
- **Responses:** `200` signup response (see `SignupResponse`), `400` invalid payload, `409` user already exists.

#### `POST /auth/confirm`
- **Description:** Confirms the signup using the emailed code.
- **Body:**
```json
{
  "email": "new.user@example.com",
  "code": "123456"
}
```
- **Responses:** `200` confirmation message, `400` invalid code/payload.

### Session & Profile

#### `POST /auth/login`
- **Description:** USER_PASSWORD_AUTH login that returns `access_token`, `id_token`, `refresh_token`, `expires_in`, and `token_type`.
- **Body:** same shape as `SignupRequest`.
- **Responses:** `200` tokens, `400` invalid payload or error, `401` wrong password, `403` user not confirmed.

#### `POST /auth/refresh`
- **Description:** Exchanges a refresh token for a new access/id token pair.
- **Body:**
```json
{
  "email": "new.user@example.com",
  "refresh_token": "<REFRESH_TOKEN>"
}
```
- **Responses:** `200` tokens, `400` invalid payload, `401` refresh token revoked/expired.

#### `GET /me`
- **Auth:** `Authorization: Bearer <access_token>`
- **Description:** Returns the decoded claims of the bearer token (`ClaimsResponse`).
- **Responses:** `200` claims, `401` missing/invalid token.

#### `GET /profile`
- **Auth:** `Authorization: Bearer <access_token>`
- **Description:** Reads the user’s Cognito attributes and returns them as `{ "attributes": { ... } }`.
- **Responses:** `200` attributes, `401` missing/invalid token.

#### `POST /profile`
- **Auth:** `Authorization: Bearer <access_token>`
- **Description:** Updates a subset of attributes (`name`, `given_name`, `family_name`, `phone_number`, `address`, `custom:role`).
- **Body:** At least one allowed attribute, e.g.
```json
{
  "name": "Ismail Amouma",
  "custom:role": "admin"
}
```
- **Responses:** `200` confirmation message, `400` no valid attributes or invalid payload, `401` missing/invalid token.

### Password recovery

#### `POST /auth/forgot-password`
- **Description:** Triggers Cognito to email/SMS a reset code.
- **Body:** `{ "email": "new.user@example.com" }`
- **Responses:** `200` message with delivery info, `400` invalid payload, `404` user not found (when Cognito is configured to disclose it).

#### `POST /auth/reset-password`
- **Description:** Completes the password reset flow with the emailed code and a new password.
- **Body:**
```json
{
  "email": "new.user@example.com",
  "code": "123456",
  "new_password": "EvenStrongerP@ss1"
}
```
- **Responses:** `200` success message, `400` invalid code or weak password.

### Google (federated) login

#### `GET /auth/google/start`
- **Description:** Redirects (302) the browser to Cognito’s hosted UI with Google selected as the identity provider.
- **Responses:** `302` with `Location` header, `400` if redirect cannot be built.

#### `GET /auth/google/callback`
- **Description:** Handles the OAuth callback from Cognito, exchanges the `code` for tokens via `/oauth2/token`, and returns the standard token payload.
- **Query parameters:** `code` (required), plus pass-through `state`, `error`, `error_description`.
- **Responses:** `200` tokens, `400` OAuth error or missing code payload.

## Troubleshooting

- **`Invalid token` on protected endpoints:** Ensure the full `Authorization: Bearer <access_token>` header from `/auth/login` is forwarded and that `CLIENT_ID` matches the app client that issued the token.
- **`NotAuthorizedException` on `/auth/login` or `/auth/refresh`:** The client secret is required; double-check `CLIENT_SECRET` and that the configured Cognito app client has the USER_PASSWORD_AUTH and refresh token flows enabled.
- **Google login hangs:** Verify that the hosted UI domain, redirect URI and Google IdP configuration all match the values registered in the Cognito app client.

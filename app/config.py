"""Application configuration and Cognito defaults."""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    flask_secret_key: str = os.getenv("FLASK_SECRET_KEY")
    cognito_region: str = os.getenv("COGNITO_REGION")
    user_pool_id: str = os.getenv("USER_POOL_ID")
    client_id: str = os.getenv("CLIENT_ID")
    client_secret: str = os.getenv("CLIENT_SECRET")
    cognito_domain: str = os.getenv("COGNITO_DOMAIN")


settings = Settings()

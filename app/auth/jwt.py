from datetime import datetime, timedelta, timezone
from typing import Any

import jwt


class JWTService:
    """Small, shared JWT encoder/decoder used by API authentication."""

    def __init__(self, secret: str):
        if not secret or not secret.strip():
            raise ValueError("JWT secret must be configured")
        self.secret = secret

    def create_token(self, user_id: str, *, expires_in: timedelta | None = None) -> str:
        expires_in = expires_in or timedelta(hours=2)
        now = datetime.now(timezone.utc)
        payload = {
            "sub": user_id,
            "iat": now,
            "exp": now + expires_in,
        }
        return jwt.encode(payload, self.secret, algorithm="HS256")

    def decode_token(self, token: str) -> dict[str, Any]:
        try:
            payload = jwt.decode(token, self.secret, algorithms=["HS256"])
        except jwt.InvalidTokenError as exc:
            raise ValueError("Invalid or expired access token") from exc

        subject = payload.get("sub")
        if not isinstance(subject, str) or not subject:
            raise ValueError("Access token subject is missing")
        return payload

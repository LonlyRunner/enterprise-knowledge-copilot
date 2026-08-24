import hashlib
import hmac
import os
import uuid
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import JWTService
from app.auth.models import User
from app.core.config import get_settings
from app.models.user import UserModel


def hash_password(password: str) -> str:
    if len(password) < 8:
        raise ValueError("Password must contain at least 8 characters")
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 240_000)
    return f"pbkdf2_sha256$240000${salt.hex()}${digest.hex()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, rounds, salt_hex, digest_hex = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), int(rounds))
        return hmac.compare_digest(digest.hex(), digest_hex)
    except (ValueError, TypeError):
        return False


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.settings = get_settings()

    async def register(self, username: str, password: str, role: str = "employee") -> User:
        username = username.strip().lower()
        if not username:
            raise ValueError("Username is required")
        existing = await self.session.scalar(select(UserModel).where(UserModel.username == username))
        if existing:
            raise ValueError("Username already exists")
        if role not in {"admin", "manager", "employee"}:
            raise ValueError("Unsupported role")
        model = UserModel(username=username, password_hash=hash_password(password), tenant_id=self.settings.default_tenant_id, role=role)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self.to_user(model)

    async def authenticate(self, username: str, password: str) -> User:
        model = await self.session.scalar(select(UserModel).where(UserModel.username == username.strip().lower()))
        if model is None or not model.is_active or not verify_password(password, model.password_hash):
            raise ValueError("Invalid username or password")
        return self.to_user(model)

    def issue_token(self, user: User) -> str:
        return JWTService(self.settings.jwt_secret).create_token(
            str(user.id), expires_in=timedelta(minutes=self.settings.access_token_expire_minutes)
        )

    @staticmethod
    def to_user(model: UserModel) -> User:
        return User(id=str(model.id), username=model.username, password_hash=model.password_hash, tenant_id=model.tenant_id, role=model.role)


async def get_user_by_id(session: AsyncSession, user_id: str) -> User | None:
    try:
        parsed_id = uuid.UUID(user_id)
    except ValueError:
        return None
    model = await session.get(UserModel, parsed_id)
    if model is None or not model.is_active:
        return None
    return AuthService.to_user(model)

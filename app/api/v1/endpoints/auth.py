from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.auth.service import AuthService
from app.core.config import get_settings
from app.db.dependencies import get_db
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/auth")


def _user_response(user: User) -> UserResponse:
    return UserResponse(id=user.id, username=user.username, tenant_id=user.tenant_id, role=user.role)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    user = await AuthService(db).register(request.username, request.password, request.role)
    return _user_response(user)


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    user = await service.authenticate(request.username, request.password)
    settings = get_settings()
    return TokenResponse(access_token=service.issue_token(user), expires_in=settings.access_token_expire_minutes * 60, user=_user_response(user))


@router.get("/me", response_model=UserResponse)
async def me(user: User = Depends(get_current_user)):
    return _user_response(user)

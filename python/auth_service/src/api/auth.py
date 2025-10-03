# src/api/auth.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import APIRouter, Depends, Request, Response, HTTPException, status


from src.core.database import get_db_session
from src.core.security import decode_token
from src.models.user import User
from src.server.schemas import (UserRegisterRequest, UserLoginRequest, VerifyEmailRequest, RefreshRequest, ResendVerificationRequest, UserResponse, RefreshTokenResponse, TokenResponse, RegisterResponse, OkMessage)
from src.services.auth_service import AuthService


router = APIRouter(tags=["auth"])
security_scheme = HTTPBearer()


@router.post("/register", response_model=RegisterResponse, status_code=201)
async def register(
    data: UserRegisterRequest, 
    request: Request, 
    db: AsyncSession = Depends(get_db_session)):
    
    """Registrar nuevo usuario"""
    remote_ip = request.client.host if request.client else None
    
    return await AuthService.register_user(db, data.username, data.email, data.password, data.captcha_token, remote_ip)


@router.post("/verify-email", response_model=TokenResponse)
async def verify_email(
    data: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db_session)):
    
    """Verificar email con token"""
    return await AuthService.verify_email(db, data.token)


@router.post("/login", response_model=TokenResponse)
async def login(
    data: UserLoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db_session)):
    
    """Login de usuario"""
    remote_ip = request.client.host if request.client else None
    return await AuthService.login(db, data.email, data.password, data.captcha_token, remote_ip)


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    data: RefreshRequest,
    db: AsyncSession = Depends(get_db_session)):
    
    """Renovar access token"""
    return await AuthService.refresh_access_token(db, data.refresh_token)


@router.post("/resend-verification", response_model=OkMessage)
async def resend_verification(
    data: ResendVerificationRequest,
    db: AsyncSession = Depends(get_db_session)):
    
    """Reenviar email de verificación"""
    return await AuthService.resend_verification(db, data.email)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme), 
    db: AsyncSession = Depends(get_db_session)) -> User:
    
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


@router.post("/logout", response_model=OkMessage)
async def logout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)):
    """Logout y revocar tokens"""
    
    await AuthService.logout(db, user_id=str(current_user.id))
    return {"message": "Sesión cerrada exitosamente"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Obtener información del usuario actual"""
    return current_user
    
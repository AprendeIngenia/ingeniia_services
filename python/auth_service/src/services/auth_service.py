# src/services/auth_service.py
import random
import logging as log

from fastapi import HTTPException
from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone

from src.models.user import User, EmailVerificationToken, RefreshToken
from src.core.security import hash_password, verify_password, create_access_token, create_refresh_token, generate_verification_token
from src.services.email_service import send_verification_email
from src.services.captcha_service import verify_recaptcha
from src.core.errors import AppErrorCode, raise_http
from src.core.config import settings


RESEND_COOLDOWN_SEC = 120

def suggest_usernames(base: str, k: int = 4) -> list[str]:
    base = base.lower().replace("@", "_").replace(".", "_")
    pool = []
    for salt in ["", "_ai", "_dl", "_ml", "_nn"]:
        pool.append(f"{base}{salt}")
    while len(pool) < k:
        pool.append(f"{base}_{random.randint(10,999)}")
    out, seen = [], set()
    for p in pool:
        if p not in seen:
            seen.add(p)
            out.append(p[:50])
    return out[:k]


class AuthService:
    @staticmethod
    async def register_user(
        db: AsyncSession,
        username: str,
        email: str,
        password: str,
        captcha_token: str,
        remote_ip: str = None) -> dict:
        """Registra nuevo usuario"""
        
        # Verificar captcha
        if not await verify_recaptcha(captcha_token, remote_ip):
            raise_http(400, AppErrorCode.CAPTCHA_FAILED, "No pudimos validar que seas humano. Vuelve a intentarlo en unos segundos.")
        
        # Verificar si ya existe
        email_q = await db.execute(select(User).where(User.email == email))
        email_user = email_q.scalar_one_or_none()

        user_q = await db.execute(select(User).where(User.username == username))
        username_user = user_q.scalar_one_or_none()
        
        if email_user:
            if email_user.is_verified:
                raise_http(409, AppErrorCode.EMAIL_ALREADY_VERIFIED, "Este email ya está verificado. Inicia sesión.")
                    
            # email existing but without verify
            last_token_q = await db.execute(select(EmailVerificationToken).where(EmailVerificationToken.user_id == email_user.id).order_by(EmailVerificationToken.created_at.desc()))
            last = last_token_q.scalars().first()
            
            if last:
                created = last.created_at or datetime.now(timezone.utc)
                delta = (datetime.now(timezone.utc) - created).total_seconds()
                
                if delta < RESEND_COOLDOWN_SEC:
                    retry_after = RESEND_COOLDOWN_SEC - int(delta)
                    raise_http(429, AppErrorCode.VERIFICATION_ALREADY_SENT_RECENTLY, "Ya te enviamos un correo de verificación hace poco.", retryAfterSec=max(retry_after, 30))
            
            # invalid tokens
            await db.execute(update(EmailVerificationToken).where((EmailVerificationToken.user_id == email_user.id) & (EmailVerificationToken.used_at.is_(None))).values(used_at=datetime.now(timezone.utc)))
            
            verification_token = generate_verification_token()
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.EMAIL_TOKEN_EXPIRE_MINUTES)
            db.add(EmailVerificationToken(user_id=email_user.id, token=verification_token, expires_at=expires_at))
            
            await db.commit()
            verification_url = f"{settings.FRONTEND_URL}/verify?token={verification_token}"
            await send_verification_email(email_user.email, email_user.username or email_user.email.split("@")[0], verification_url, verification_token)
            return {"message": "Ya tenías un registro pendiente. Te reenviamos el correo de verificación."}
                
        if username_user:
            raise_http(400, AppErrorCode.USERNAME_TAKEN, "Ese usuario ya está en uso. Prueba con una variante.", suggestions=suggest_usernames(username))
        
        # Create new user
        new_user = User(username=username, email=email, password_hash=hash_password(password))
        
        # add user
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        # new token
        verification_token = generate_verification_token()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.EMAIL_TOKEN_EXPIRE_MINUTES)
        
        token_record = EmailVerificationToken(
            user_id=new_user.id,
            token=verification_token,
            expires_at=expires_at,
        )
        
        db.add(token_record)
        await db.commit()
        
        verification_url = f"{settings.FRONTEND_URL}/verify?token={verification_token}"
        await send_verification_email(new_user.email, new_user.username, verification_url, verification_token)
        log.info(f"Usuario registrado: {username} ({email})")
        
        return {
            "message": "Usuario registrado. Verifica tu email.",
            "user_id": str(new_user.id),
            "email": email
        }
        
    @staticmethod
    async def verify_email(db: AsyncSession, token: str) -> dict:
        """Verifica email del usuario"""
        
        result = await db.execute(
            select(EmailVerificationToken).where(
                (EmailVerificationToken.token == token) &
                (EmailVerificationToken.used_at.is_(None)) &
                (EmailVerificationToken.expires_at > datetime.now(timezone.utc))
            )
        )
        token_record = result.scalar_one_or_none()
        
        if not token_record:
            raise_http(400, AppErrorCode.TOKEN_INVALID_OR_EXPIRED, "Token inválido o expirado. Reenvía el correo de verificación y vuelve a intentar.")
        
        # Marcar usuario como verificado
        user_result = await db.execute(select(User).where(User.id == token_record.user_id))
        user = user_result.scalar_one()
        user.is_verified = True
        
        # Marcar token como usado
        token_record.used_at = datetime.now(timezone.utc)
        
        await db.commit()
        await db.refresh(user)
        
        # Generar tokens
        access_token = create_access_token({"sub": str(user.id), "email": user.email})
        refresh_token = create_refresh_token({"sub": str(user.id)})
        
        # Guardar refresh token
        refresh_record = RefreshToken(
            user_id=user.id,
            token_hash=hash_password(refresh_token),
            expires_at=datetime.now(timezone.utc) + timedelta(days=7)
        )
        
        db.add(refresh_record)
        await db.commit()
        
        log.info(f"Email verificado: {user.email}")
        return {
            "message": "Email verificado exitosamente",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    @staticmethod
    async def login(
        db: AsyncSession,
        email: str,
        password: str,
        captcha_token: str,
        remote_ip: str = None
    ) -> dict:
        """Login de usuario"""
        
        # Verificar captcha
        if not await verify_recaptcha(captcha_token, remote_ip):
            raise_http(400, AppErrorCode.CAPTCHA_FAILED, "No pudimos validar que seas humano. Vuelve a intentarlo en unos segundos.")
        
        # Buscar usuario
        result = await db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        
        if not user or not verify_password(password, user.password_hash):
            raise_http(401, AppErrorCode.BAD_CREDENTIALS, "Email o contraseña incorrectos.")
        
        if not user.is_active:
            raise_http(403, AppErrorCode.ACCOUNT_INACTIVE, "Tu cuenta está desactivada. Contáctanos si crees que es un error.")
        
        if not user.is_verified:
            raise_http(403, AppErrorCode.EMAIL_NOT_VERIFIED, "Aún no verificas tu email. Revisa tu bandeja o reenvía el correo.")
        
        # Actualizar last_login
        user.last_login = datetime.now(timezone.utc)
        
        # Generar tokens
        access_token = create_access_token({"sub": str(user.id), "email": user.email})
        refresh_token = create_refresh_token({"sub": str(user.id)})
        
        # Guardar refresh token
        refresh_record = RefreshToken(
            user_id=user.id,
            token_hash=hash_password(refresh_token),
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        db.add(refresh_record)
        await db.commit()
        
        log.info(f"Login exitoso: {email}")
        return {
            "message": "Inicio de sesión exitoso",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    @staticmethod
    async def refresh_access_token(db: AsyncSession, refresh_token: str) -> dict:
        """Renueva access token usando refresh token"""
        
        from src.core.security import decode_token
        
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Refresh token inválido")
        
        user_id = payload.get("sub")
        
        # Verificar que el refresh token existe y no está revocado
        result = await db.execute(
            select(RefreshToken).where(
                (RefreshToken.user_id == user_id) &
                (RefreshToken.revoked_at.is_(None)) &
                (RefreshToken.expires_at > datetime.now(timezone.utc))
            )
        )
        token_records = result.scalars().all()
        
        valid_token = None
        for record in token_records:
            if verify_password(refresh_token, record.token_hash):
                valid_token = record
                break
        
        if not valid_token:
            raise HTTPException(status_code=401, detail="Refresh token inválido o expirado")
        
        # Obtener usuario
        user_result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one()
        
        # Crear nuevo access token
        new_access_token = create_access_token({"sub": str(user.id), "email": user.email})
        
        return {
            "message": "Token renovado",
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": 900
        }
        
    @staticmethod
    async def logout(db: AsyncSession, user_id: str, refresh_token: str = None):
        """Logout - revoca refresh tokens"""
        
        if refresh_token:
            # Revocar token específico
            result = await db.execute(
                select(RefreshToken).where(
                    (RefreshToken.user_id == user_id) &
                    (RefreshToken.revoked_at.is_(None))
                )
            )
            tokens = result.scalars().all()
            
            for token_record in tokens:
                if verify_password(refresh_token, token_record.token_hash):
                    token_record.revoked_at = datetime.now(timezone.utc)
                    break
        else:
            # Revocar todos los tokens del usuario
            result = await db.execute(
                select(RefreshToken).where(
                    (RefreshToken.user_id == user_id) &
                    (RefreshToken.revoked_at.is_(None))
                )
            )
            tokens = result.scalars().all()
            
            for token_record in tokens:
                token_record.revoked_at = datetime.now(timezone.utc)
        
        await db.commit()
        log.info(f"Logout: user_id={user_id}")
        
    @staticmethod
    async def resend_verification(db: AsyncSession, email: str):
        """Reenvía email de verificación"""
        
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        if user.is_verified:
            raise HTTPException(status_code=400, detail="Email ya verificado")
        
        last_token_q = await db.execute(select(EmailVerificationToken).where(EmailVerificationToken.user_id == user.id).order_by(EmailVerificationToken.created_at.desc()))
        last = last_token_q.scalars().first()
        
        if last:
            created = last.created_at or datetime.now(timezone.utc)
            delta = (datetime.now(timezone.utc) - created).total_seconds()
            
            if delta < RESEND_COOLDOWN_SEC:
                retry_after = RESEND_COOLDOWN_SEC - int(delta)
                raise_http(429, AppErrorCode.VERIFICATION_ALREADY_SENT_RECENTLY, "Ya te enviamos un correo de verificación hace poco.", retryAfterSec=max(retry_after, 30))
        
        # invalid tokens
        await db.execute(update(EmailVerificationToken).where(
            (EmailVerificationToken.user_id == user.id) & 
            (EmailVerificationToken.used_at.is_(None))).values(used_at=datetime.now(timezone.utc)))
        
        # new token
        verification_token = generate_verification_token()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.EMAIL_TOKEN_EXPIRE_MINUTES)
        
        token_record = EmailVerificationToken(
            user_id=user.id,
            token=verification_token,
            expires_at=expires_at
        )
        db.add(token_record)
        await db.commit()
        
        # send email
        verification_url = f"{settings.FRONTEND_URL}/verify?token={verification_token}"
        await send_verification_email(email, user.username, verification_url, verification_token)
        
        log.info(f"Email de verificación reenviado: {email}")
        return {"message": "Email de verificación reenviado"}
    
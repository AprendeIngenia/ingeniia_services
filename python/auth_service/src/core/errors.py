# src/core/errors.py
from enum import Enum
from fastapi import HTTPException

class AppErrorCode(str, Enum):
    USERNAME_TAKEN = "USERNAME_TAKEN"
    USERNAME_INVALID = "USERNAME_INVALID"
    EMAIL_ALREADY_VERIFIED = "EMAIL_ALREADY_VERIFIED"
    EMAIL_UNVERIFIED_EXISTING = "EMAIL_UNVERIFIED_EXISTING"
    CAPTCHA_FAILED = "CAPTCHA_FAILED"
    VERIFICATION_ALREADY_SENT_RECENTLY = "VERIFICATION_ALREADY_SENT_RECENTLY"
    TOKEN_INVALID_OR_EXPIRED = "TOKEN_INVALID_OR_EXPIRED"
    RATE_LIMITED = "RATE_LIMITED"
    BAD_CREDENTIALS = "BAD_CREDENTIALS"
    ACCOUNT_INACTIVE = "ACCOUNT_INACTIVE"
    EMAIL_NOT_VERIFIED = "EMAIL_NOT_VERIFIED"

def raise_http(status: int, code: AppErrorCode, message: str, **kwargs):
    detail = {"code": code.value, "message": message, **kwargs}
    raise HTTPException(status_code=status, detail=detail)

from datetime import datetime, timedelta
from typing import Optional, Union, Dict, Any, Set
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Token blacklist for logout functionality
_token_blacklist: Set[str] = set()

def add_to_blacklist(token: str) -> None:
    """Add token to blacklist"""
    _token_blacklist.add(token)
    logger.info(f"Token added to blacklist")

def is_token_blacklisted(token: str) -> bool:
    """Check if token is blacklisted"""
    return token in _token_blacklist

def clear_expired_blacklist() -> None:
    """Clear expired tokens from blacklist (can be called periodically)"""
    # This is a simple in-memory implementation
    # In production, you might want to use Redis or database with TTL
    logger.info(f"Blacklist cleared, current size: {len(_token_blacklist)}")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "type": "access",
        "iat": datetime.utcnow()
    })
    
    try:
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating access token: {e}")
        raise

def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({
        "exp": expire,
        "type": "refresh",
        "iat": datetime.utcnow()
    })
    
    try:
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating refresh token: {e}")
        raise

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode JWT token"""
    try:
        # Check if token is blacklisted
        if is_token_blacklisted(token):
            logger.warning("Token is blacklisted")
            return None
            
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        logger.warning(f"JWT token verification failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        return None

def generate_tokens(user_id: int, email: str, role: int) -> Dict[str, str]:
    """Generate both access and refresh tokens"""
    try:
        access_token = create_access_token(
            data={"sub": str(user_id), "email": email, "role": role}
        )
        refresh_token = create_refresh_token(
            data={"sub": str(user_id), "email": email, "role": role}
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    except Exception as e:
        logger.error(f"Error generating tokens: {e}")
        raise

def validate_password_strength(password: str) -> Dict[str, bool]:
    """Validate password strength"""
    validation = {
        "length": len(password) >= 8,
        "uppercase": any(c.isupper() for c in password),
        "lowercase": any(c.islower() for c in password),
        "digit": any(c.isdigit() for c in password),
        "special": any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    }
    validation["valid"] = all(validation.values())
    return validation 
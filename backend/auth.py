from datetime import datetime, timedelta
from jose import JWTError, jwt
import random
import string
import os
import hashlib
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ==================== PASSWORD HASHING ====================

def hash_password(password: str) -> str:
    """Hash a password using SHA256 (simple but not production-grade)."""
    # For production, use bcrypt or argon2
    salt = os.urandom(32).hex()
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}${pwd_hash.hex()}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    try:
        salt, pwd_hash = hashed_password.split('$')
        new_hash = hashlib.pbkdf2_hmac('sha256', plain_password.encode(), salt.encode(), 100000)
        return new_hash.hex() == pwd_hash
    except:
        return False

# ==================== JWT TOKENS ====================

# Use a fixed SECRET_KEY for development (change in production)
SECRET_KEY = "jobify-secret-key-2024-development-only-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

print(f"[AUTH] Using SECRET_KEY: {SECRET_KEY[:30]}...")

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

def create_refresh_token(data: dict):
    """Create JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

def verify_token(token: str):
    """Verify JWT token and extract data."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except JWTError as e:
        print(f"[AUTH] Token verification error: {str(e)}")
        return None

# ==================== OTP GENERATION ====================

def generate_otp(length: int = 6) -> str:
    """Generate a random OTP code."""
    return ''.join(random.choices(string.digits, k=length))

def verify_otp_expiry(created_at: datetime, expires_at: datetime) -> bool:
    """Check if OTP is still valid (not expired)."""
    return datetime.utcnow() < expires_at

# ==================== EMAIL VALIDATION ====================

def validate_email_format(email: str) -> bool:
    """Validate email format."""
    return '@' in email and '.' in email

# ==================== VALIDATION SCHEMAS ====================

class PasswordValidator:
    """Validate password strength."""
    
    @staticmethod
    def validate(password: str) -> tuple[bool, str]:
        """
        Validate password strength.
        Returns: (is_valid, message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not any(char.isupper() for char in password):
            return False, "Password must contain at least one uppercase letter"
        
        if not any(char.islower() for char in password):
            return False, "Password must contain at least one lowercase letter"
        
        if not any(char.isdigit() for char in password):
            return False, "Password must contain at least one digit"
        
        if not any(char in "!@#$%^&*" for char in password):
            return False, "Password must contain at least one special character (!@#$%^&*)"
        
        return True, "Password is strong"
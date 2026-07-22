from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from database import get_db, User, OTP
from schemas import SignupRequest, LoginRequest, OTPVerifyRequest, TokenResponse, UserProfile, UpdateUserRequest
from auth import hash_password, verify_password, create_access_token, create_refresh_token, verify_token, generate_otp, PasswordValidator
from email_service import send_otp_email, send_welcome_email
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])

# ==================== SIGNUP ====================

@router.post("/signup", response_model=dict)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """
    User signup endpoint.
    Validates email, password, and creates new user.
    Returns message to check email for OTP.
    """
    
    # Validate email format (basic check)
    if '@' not in request.email or '.' not in request.email:
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if username exists
    existing_username = db.query(User).filter(User.username == request.username).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Validate passwords match
    if request.password != request.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    # Validate password strength
    is_valid, message = PasswordValidator.validate(request.password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=message)
    
    # Create new user
    try:
        new_user = User(
            email=request.email,
            username=request.username,
            full_name=request.full_name,
            password_hash=hash_password(request.password),
            is_verified=False
        )
        db.add(new_user)
        db.commit()
        
        # Generate and send OTP
        otp_code = generate_otp()
        otp_expiry = datetime.utcnow() + timedelta(minutes=10)
        
        new_otp = OTP(
            email=request.email,
            otp_code=otp_code,
            expires_at=otp_expiry
        )
        db.add(new_otp)
        db.commit()
        
        # Send OTP via email
        email_sent = send_otp_email(request.email, otp_code)
        
        logger.info(f"New user registered: {request.email}. OTP sent: {email_sent}")
        
        return {
            'success': True,
            'message': 'Signup successful! Check your email for OTP verification code.',
            'email': request.email
        }
    
    except Exception as e:
        db.rollback()
        logger.error(f"Signup error: {str(e)}")
        raise HTTPException(status_code=500, detail="Signup failed. Please try again.")

# ==================== VERIFY OTP ====================

@router.post("/verify-otp", response_model=TokenResponse)
def verify_otp(request: OTPVerifyRequest, db: Session = Depends(get_db)):
    """
    Verify OTP and complete email verification.
    Returns JWT tokens for authenticated requests.
    """
    
    # Find user
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Find valid OTP
    otp_record = db.query(OTP).filter(
        OTP.email == request.email,
        OTP.otp_code == request.otp_code,
        OTP.is_used == False
    ).first()
    
    if not otp_record:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    # Check if OTP expired
    if datetime.utcnow() > otp_record.expires_at:
        raise HTTPException(status_code=400, detail="OTP expired. Please request a new one.")
    
    # Mark OTP as used and verify user
    try:
        otp_record.is_used = True
        user.is_verified = True
        db.commit()
        
        # Send welcome email
        send_welcome_email(user.email, user.full_name)
        
        # Create tokens
        access_token = create_access_token(data={"sub": user.email})
        refresh_token = create_refresh_token(data={"sub": user.email})
        
        logger.info(f"User verified: {user.email}")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user={
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'full_name': user.full_name,
                'is_verified': user.is_verified
            }
        )
    
    except Exception as e:
        db.rollback()
        logger.error(f"OTP verification error: {str(e)}")
        raise HTTPException(status_code=500, detail="Verification failed")

# ==================== RESEND OTP ====================

@router.post("/resend-otp")
def resend_otp(email: str, db: Session = Depends(get_db)):
    """
    Resend OTP to user's email.
    """
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_verified:
        raise HTTPException(status_code=400, detail="User already verified")
    
    try:
        # Generate new OTP
        otp_code = generate_otp()
        otp_expiry = datetime.utcnow() + timedelta(minutes=10)
        
        # Delete old OTP
        db.query(OTP).filter(OTP.email == email).delete()
        
        # Create new OTP
        new_otp = OTP(
            email=email,
            otp_code=otp_code,
            expires_at=otp_expiry
        )
        db.add(new_otp)
        db.commit()
        
        logger.info(f"OTP resent to {email}. OTP: {otp_code}")
        
        return {
            'success': True,
            'message': 'OTP sent to your email'
        }
    
    except Exception as e:
        db.rollback()
        logger.error(f"Resend OTP error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to resend OTP")

# ==================== LOGIN ====================

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    User login endpoint.
    Validates email and password.
    Returns JWT tokens.
    """
    
    # Find user
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Check if verified
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified. Please verify your email first.")
    
    # Verify password
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    
    logger.info(f"User logged in: {user.email}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user={
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'full_name': user.full_name,
            'is_verified': user.is_verified
        }
    )

# ==================== REFRESH TOKEN ====================

@router.post("/refresh-token", response_model=TokenResponse)
def refresh_token(refresh_token_str: str, db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token.
    """
    
    # Verify refresh token
    email = verify_token(refresh_token_str)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    # Find user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create new tokens
    access_token = create_access_token(data={"sub": user.email})
    new_refresh_token = create_refresh_token(data={"sub": user.email})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        user={
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'full_name': user.full_name,
            'is_verified': user.is_verified
        }
    )

# ==================== GET CURRENT USER ====================

def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    """
    Get current authenticated user from JWT token in Authorization header.
    Use this as dependency in protected routes.
    """
    
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    # Extract token from "Bearer <token>"
    try:
        parts = authorization.split()
        if len(parts) != 2:
            raise ValueError("Invalid format")
        scheme, token = parts
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    logger.info(f"Verifying token: {token[:20]}...")
    email = verify_token(token)
    
    if not email:
        logger.error("Token verification failed")
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        logger.error(f"User not found for email: {email}")
        raise HTTPException(status_code=404, detail="User not found")
    
    logger.info(f"User authenticated: {email}")
    return user

@router.get("/me", response_model=UserProfile)
def get_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user's profile.
    Requires authentication.
    """
    return UserProfile.from_orm(current_user)

# ==================== UPDATE PROFILE ====================

@router.put("/profile", response_model=UserProfile)
def update_profile(
    request: UpdateUserRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user profile.
    Requires authentication.
    """
    
    try:
        if request.full_name:
            current_user.full_name = request.full_name
        if request.bio:
            current_user.bio = request.bio
        if request.skills:
            current_user.skills = request.skills
        if request.phone:
            current_user.phone = request.phone
        if request.location:
            current_user.location = request.location
        
        current_user.updated_at = datetime.utcnow()
        db.commit()
        
        return UserProfile.from_orm(current_user)
    
    except Exception as e:
        db.rollback()
        logger.error(f"Profile update error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update profile")

# ==================== LOGOUT ====================

@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """
    Logout endpoint.
    In production, you'd invalidate the token in a blacklist.
    """
    
    logger.info(f"User logged out: {current_user.email}")
    
    return {
        'success': True,
        'message': 'Logged out successfully'
    }
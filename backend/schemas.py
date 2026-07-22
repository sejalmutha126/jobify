from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# ==================== AUTH SCHEMAS ====================

class SignupRequest(BaseModel):
    email: str
    username: str
    full_name: str
    password: str
    confirm_password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class OTPVerifyRequest(BaseModel):
    email: str
    otp_code: str

class OTPResendRequest(BaseModel):
    email: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: dict

class RefreshTokenRequest(BaseModel):
    refresh_token: str

# ==================== USER SCHEMAS ====================

class UserProfile(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    bio: Optional[str] = None
    skills: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    profile_pic: Optional[str] = None
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UpdateUserRequest(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str
    confirm_password: str

# ==================== JOB SCHEMAS ====================

class JobResponse(BaseModel):
    id: int
    title: str
    company: str
    location: str
    description: str
    salary: Optional[str]
    job_url: str
    source: str
    posted_date: datetime
    skills_required: str
    
    class Config:
        from_attributes = True

class SearchRequest(BaseModel):
    title: Optional[str] = None
    location: Optional[str] = None
    salary_min: Optional[int] = None

class JobCreate(BaseModel):
    title: str
    company: str
    location: str
    description: str
    salary: Optional[str]
    job_url: str
    source: str
    skills_required: str

# ==================== RESUME ANALYSIS SCHEMAS ====================

class ResumeAnalysisRequest(BaseModel):
    resume_text: str
    job_description: str

class ResumeAnalysisResponse(BaseModel):
    match_score: float
    matching_keywords: List[str]
    missing_keywords: List[str]
    suggestions: List[str]

class SkillGapRequest(BaseModel):
    user_skills: List[str]
    job_skills: List[str]

class SkillGapResponse(BaseModel):
    missing_skills: List[str]
    suggested_learning_path: List[str]

# ==================== APPLICATION SCHEMAS ====================

class ApplicationResponse(BaseModel):
    id: int
    job_id: int
    status: str
    match_score: float
    applied_date: datetime
    
    class Config:
        from_attributes = True

class CreateApplicationRequest(BaseModel):
    job_title: str
    company: str
    location: str
    job_url: str
    match_score: float = 75
    status: str = 'viewed'

class UpdateApplicationRequest(BaseModel):
    status: str

# ==================== EMAIL AUTOMATION SCHEMAS ====================

class EmailAutomationRequest(BaseModel):
    recruiter_name: str
    recruiter_email: str
    job_title: str
    company_name: str
    user_name: str
    user_skills: List[str]

class EmailAutomationResponse(BaseModel):
    email_body: str
    subject: str

class SendEmailRequest(BaseModel):
    recruiter_name: str
    recruiter_email: str
    job_title: str
    company_name: str
    user_name: str
    user_skills: List[str]
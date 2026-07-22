from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Database setup
DATABASE_URL = "sqlite:///./jobify.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==================== USER MODEL ====================

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    full_name = Column(String)
    is_verified = Column(Boolean, default=False)
    google_id = Column(String, nullable=True, unique=True)
    profile_pic = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    skills = Column(Text, nullable=True)  # JSON string
    phone = Column(String, nullable=True)
    location = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ==================== OTP MODEL ====================

class OTP(Base):
    __tablename__ = "otps"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    otp_code = Column(String)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

# ==================== JOB MODEL ====================

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    company = Column(String)
    location = Column(String)
    description = Column(Text)
    salary = Column(String, nullable=True)
    job_url = Column(String, unique=True)
    source = Column(String)
    posted_date = Column(DateTime, default=datetime.utcnow)
    skills_required = Column(Text)

# ==================== APPLICATION MODEL ====================

class Application(Base):
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    job_id = Column(Integer, index=True)
    status = Column(String, default="applied")  # applied, rejected, interview, offered
    match_score = Column(Float)
    applied_date = Column(DateTime, default=datetime.utcnow)
    follow_up_date = Column(DateTime, nullable=True)

# ==================== EMAIL CAMPAIGN MODEL ====================

class EmailCampaign(Base):
    __tablename__ = "email_campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    recruiter_email = Column(String)
    email_body = Column(Text)
    sent_date = Column(DateTime, default=datetime.utcnow)
    opened = Column(Boolean, default=False)
    replied = Column(Boolean, default=False)

# ==================== CREATE TABLES ====================

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
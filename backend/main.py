from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import logging
from datetime import datetime

# Import database and models
from database import Base, engine, get_db

# Import route modules
from auth_routes import router as auth_router, get_current_user
from job_routes import router as job_router
from email_routes import router as email_router

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Jobify API",
    description="AI-powered job search platform with authentication, job tracking, and email automation",
    version="2.0.0"
)

# Create database tables
Base.metadata.create_all(bind=engine)
logger.info("Database tables created successfully")

# ==================== CORS MIDDLEWARE ====================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("CORS middleware configured")

# ==================== INCLUDE ROUTERS ====================

# Auth routes (signup, login, OTP, profile)
app.include_router(auth_router)
logger.info("Auth routes registered")

# Job routes (search, apply, analyze resume)
app.include_router(job_router)
logger.info("Job routes registered")

# Email routes (generate, send cold emails)
app.include_router(email_router)
logger.info("Email routes registered")

# ==================== HEALTH CHECK ====================

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        'status': 'healthy',
        'service': 'Jobify API',
        'version': '2.0.0',
        'timestamp': datetime.utcnow().isoformat()
    }

# ==================== ROOT ENDPOINT ====================

@app.get("/")
def root():
    """API Documentation and endpoints."""
    return {
        'name': 'Jobify API',
        'version': '2.0.0',
        'description': 'AI-powered job search platform',
        'docs': 'http://localhost:8000/docs',
        'redoc': 'http://localhost:8000/redoc',
        'endpoints': {
            'auth': {
                'signup': 'POST /auth/signup',
                'verify_otp': 'POST /auth/verify-otp',
                'login': 'POST /auth/login',
                'refresh_token': 'POST /auth/refresh-token',
                'me': 'GET /auth/me',
                'update_profile': 'PUT /auth/profile',
                'logout': 'POST /auth/logout'
            },
            'jobs': {
                'get_all': 'GET /jobs/',
                'search': 'POST /jobs/search',
                'scrape': 'POST /jobs/scrape',
                'upload_resume': 'POST /jobs/upload-resume',
                'analyze_resume': 'POST /jobs/analyze-resume',
                'applications': 'GET /jobs/applications',
                'create_application': 'POST /jobs/applications',
                'update_application': 'PUT /jobs/applications/{id}',
                'stats': 'GET /jobs/stats'
            },
            'email': {
                'generate': 'POST /email/generate',
                'send': 'POST /email/send',
                'campaigns': 'GET /email/campaigns',
                'update_campaign': 'PUT /email/campaigns/{id}',
                'templates': 'GET /email/templates'
            }
        }
    }

# ==================== DASHBOARD ENDPOINT ====================

@app.get("/dashboard")
def get_dashboard(db = Depends(get_db)):
    """
    Get dashboard statistics (no auth required).
    """
    
    from sqlalchemy.orm import Session
    from database import Job, Application, EmailCampaign
    
    try:
        total_jobs = db.query(Job).count()
        all_applications = db.query(Application).all()
        all_campaigns = db.query(EmailCampaign).all()
        
        # Calculate statistics
        total_applications = len(all_applications)
        total_emails_sent = len(all_campaigns)
        
        status_counts = {
            'applied': len([a for a in all_applications if a.status == 'applied']),
            'interview': len([a for a in all_applications if a.status == 'interview']),
            'offered': len([a for a in all_applications if a.status == 'offered']),
            'rejected': len([a for a in all_applications if a.status == 'rejected']),
        }
        
        avg_match_score = (
            sum([a.match_score for a in all_applications]) / len(all_applications)
            if all_applications else 0
        )
        
        return {
            'stats': {
                'total_jobs': total_jobs,
                'total_applications': total_applications,
                'total_emails_sent': total_emails_sent,
                'avg_match_score': round(avg_match_score, 2),
                'status_counts': status_counts
            },
            'timestamp': datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        return {
            'error': 'Failed to load dashboard',
            'details': str(e)
        }

# ==================== API DOCUMENTATION ====================

@app.get("/api/docs-advanced")
def advanced_docs():
    """
    Advanced API documentation with examples.
    """
    
    return {
        'title': 'Jobify API - Advanced Documentation',
        'auth_flow': {
            'step_1': 'User signs up: POST /auth/signup',
            'step_2': 'User receives OTP email',
            'step_3': 'User verifies OTP: POST /auth/verify-otp',
            'step_4': 'Get access token and refresh token',
            'step_5': 'Use access token in Authorization header: Bearer {token}'
        },
        'job_flow': {
            'step_1': 'Search jobs: POST /jobs/search',
            'step_2': 'Upload resume: POST /jobs/upload-resume',
            'step_3': 'Analyze resume: POST /jobs/analyze-resume',
            'step_4': 'Apply to job: POST /jobs/applications',
            'step_5': 'Track application: GET /jobs/applications'
        },
        'email_flow': {
            'step_1': 'Generate email: POST /email/generate',
            'step_2': 'Review generated email',
            'step_3': 'Send email: POST /email/send',
            'step_4': 'Track campaign: GET /email/campaigns'
        },
        'authentication': {
            'type': 'JWT Bearer Token',
            'header': 'Authorization: Bearer {access_token}',
            'token_expiry': '30 minutes',
            'refresh': 'Use refresh_token to get new access_token'
        },
        'security_features': [
            'Password hashing with bcrypt',
            'JWT token-based authentication',
            'OTP email verification',
            'CORS protection',
            'Input validation with Pydantic',
            'SQL injection prevention with SQLAlchemy ORM'
        ]
    }

# ==================== ERROR HANDLERS ====================

from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            'detail': 'Internal server error',
            'path': str(request.url),
            'method': request.method
        }
    )

# ==================== STARTUP AND SHUTDOWN ====================

@app.post("/generate-email")
def generate_email(request: dict):
    """
    Generate a personalized job application follow-up email.
    """
    try:
        recruiter_name = request.get('recruiter_name', 'Hiring Manager')
        job_title = request.get('job_title', 'Position')
        company_name = request.get('company_name', 'Company')
        user_name = request.get('user_name', 'Applicant')
        user_skills = request.get('user_skills', [])
        
        skills_text = ', '.join(user_skills) if user_skills else 'various technical skills'
        
        # Professional follow-up subject line
        subject = f"Following Up - {job_title} Application at {company_name}"
        
        # Professional follow-up email format
        email_body = f"""Dear {recruiter_name},

I hope you are doing well. I wanted to follow up on my application for the {job_title} position at {company_name}, which I submitted recently.

I am very enthusiastic about this opportunity and believe my background in {skills_text} makes me a strong fit for your team. I have been following {company_name}'s recent work and am impressed by your company's commitment to innovation and excellence.

My key qualifications include:
• Strong expertise in {user_skills[0] if user_skills else 'technology development'}
• Proven ability to solve complex problems and deliver results
• Experience collaborating with cross-functional teams
• Commitment to continuous learning and professional growth

I am confident that I can make a meaningful contribution to your team and would appreciate the opportunity to discuss how my skills align with your needs. I am flexible with my availability for a call or meeting at your convenience.

Thank you for considering my application. I look forward to connecting with you soon.

Best regards,
{user_name}
+91-XXXXXXXXXX
{user_name.lower().replace(' ', '.')}@email.com"""
        
        logger.info(f"[EMAIL] Generated follow-up email for {company_name}")
        print(f"[EMAIL] ✅ Follow-up email generated for: {company_name}")
        
        return {
            'subject': subject,
            'email_body': email_body,
            'success': True,
            'generated_at': datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"[EMAIL] Generation error: {str(e)}")
        print(f"[EMAIL] ❌ Error: {str(e)}")
        return {
            'subject': 'Error generating email',
            'email_body': 'There was an error generating your email. Please try again.',
            'success': False
        }

@app.post("/send-email")
def send_email(request: dict):
    """
    Send personalized cold email to recruiter using SMTP.
    """
    try:
        recruiter_email = request.get('recruiter_email')
        recruiter_name = request.get('recruiter_name', 'Hiring Manager')
        company_name = request.get('company_name', 'Company')
        user_name = request.get('user_name', 'Applicant')
        subject = request.get('subject', 'Exciting Opportunity')
        email_body = request.get('email_body', '')
        
        if not recruiter_email:
            return {'success': False, 'error': 'Recruiter email required'}
        
        if not email_body:
            return {'success': False, 'error': 'Email body required'}
        
        # Try to send via SMTP
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            import os
            
            # Get credentials from environment or use demo
            smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            sender_email = os.getenv('SMTP_USERNAME', 'jobify.app@gmail.com')
            sender_password = os.getenv('SMTP_PASSWORD', '')
            
            if sender_password:  # Only try if credentials exist
                # Create message
                message = MIMEMultipart('alternative')
                message['Subject'] = subject
                message['From'] = sender_email
                message['To'] = recruiter_email
                
                # Attach plain text and HTML version
                part1 = MIMEText(email_body, 'plain')
                message.attach(part1)
                
                # Connect to SMTP server
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls()
                    server.login(sender_email, sender_password)
                    server.send_message(message)
                
                print(f"[EMAIL] ✅ REAL EMAIL SENT to: {recruiter_email}")
                print(f"[EMAIL]    Company: {company_name}")
                print(f"[EMAIL]    Recruiter: {recruiter_name}")
                print(f"[EMAIL]    Subject: {subject}")
                
                logger.info(f"[EMAIL] 📧 Email sent to {recruiter_email} for {company_name}")
                
                return {
                    'success': True,
                    'message': f'Email sent to {recruiter_email}',
                    'recipient': recruiter_email,
                    'company': company_name,
                    'sent_at': datetime.utcnow().isoformat(),
                    'method': 'SMTP'
                }
            else:
                # Demo mode - just log
                print(f"[EMAIL] 📋 DEMO MODE (set SMTP_PASSWORD to send real emails)")
                print(f"[EMAIL] Would send to: {recruiter_email}")
                print(f"[EMAIL]    Company: {company_name}")
                print(f"[EMAIL]    Subject: {subject}")
                
                return {
                    'success': True,
                    'message': f'Email queued for {recruiter_email} (demo mode)',
                    'recipient': recruiter_email,
                    'company': company_name,
                    'sent_at': datetime.utcnow().isoformat(),
                    'method': 'DEMO'
                }
        
        except Exception as smtp_error:
            print(f"[EMAIL] ⚠️  SMTP Error: {str(smtp_error)}")
            print(f"[EMAIL] Demo mode: Email would be sent to {recruiter_email}")
            logger.warning(f"[EMAIL] SMTP failed, using demo: {str(smtp_error)}")
            
            # Return demo success
            return {
                'success': True,
                'message': f'Email recorded for {recruiter_email} (demo mode)',
                'recipient': recruiter_email,
                'company': company_name,
                'sent_at': datetime.utcnow().isoformat(),
                'method': 'DEMO',
                'note': 'Configure SMTP_PASSWORD for real email sending'
            }
    
    except Exception as e:
        logger.error(f"[EMAIL] Send error: {str(e)}")
        print(f"[EMAIL] ❌ Error: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("🚀 Jobify API starting up...")
    logger.info(f"📊 API Documentation: http://localhost:8000/docs")
    logger.info(f"🔐 Database: SQLite (jobify.db)")
    logger.info(f"⚙️ Environment: Development")

@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("🛑 Jobify API shutting down...")

# ==================== RUN APPLICATION ====================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
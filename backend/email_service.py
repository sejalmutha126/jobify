import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

# ==================== GMAIL CONFIGURATION ====================

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

print(f"[EMAIL] SMTP Server: {SMTP_SERVER}:{SMTP_PORT}")
print(f"[EMAIL] SMTP Username: {SMTP_USERNAME[:10]}..." if SMTP_USERNAME else "[EMAIL] SMTP Username: NOT SET")

# ==================== OTP EMAIL TEMPLATE ====================

def get_otp_email_html(otp_code: str, email: str) -> str:
    """Generate HTML email template for OTP."""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f5f5f5;
            }}
            .container {{
                max-width: 600px;
                margin: 20px auto;
                background-color: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                text-align: center;
                color: #2563eb;
                margin-bottom: 30px;
            }}
            .header h1 {{
                margin: 0;
                font-size: 28px;
            }}
            .otp-section {{
                background-color: #f0f9ff;
                border: 2px solid #2563eb;
                border-radius: 8px;
                padding: 20px;
                text-align: center;
                margin: 20px 0;
            }}
            .otp-code {{
                font-size: 36px;
                font-weight: bold;
                color: #2563eb;
                letter-spacing: 5px;
                margin: 10px 0;
                font-family: 'Courier New', monospace;
            }}
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #e5e7eb;
                font-size: 12px;
                color: #666;
                text-align: center;
            }}
            .warning {{
                background-color: #fef2f2;
                border-left: 4px solid #dc2626;
                padding: 10px;
                margin: 15px 0;
                font-size: 12px;
                color: #7f1d1d;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔐 Jobify</h1>
                <p>Email Verification</p>
            </div>
            
            <p>Hi,</p>
            
            <p>Thank you for signing up for Jobify! We're excited to have you on board.</p>
            
            <p>To complete your email verification, please use the following code:</p>
            
            <div class="otp-section">
                <p>Your verification code is:</p>
                <div class="otp-code">{otp_code}</div>
                <p style="color: #666; margin: 10px 0;">This code will expire in 10 minutes</p>
            </div>
            
            <div class="warning">
                <strong>⚠️ Security Notice:</strong> Never share this code with anyone. Jobify support will never ask for your OTP code.
            </div>
            
            <p>If you didn't create this account, please ignore this email.</p>
            
            <div class="footer">
                <p>&copy; 2024 Jobify. All rights reserved.</p>
                <p>This is an automated email. Please do not reply to this message.</p>
            </div>
        </div>
    </body>
    </html>
    """

def get_welcome_email_html(full_name: str) -> str:
    """Generate HTML email template for welcome email."""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f5f5f5;
            }}
            .container {{
                max-width: 600px;
                margin: 20px auto;
                background-color: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                text-align: center;
                color: #2563eb;
                margin-bottom: 30px;
            }}
            .header h1 {{
                margin: 0;
                font-size: 28px;
            }}
            .features {{
                margin: 20px 0;
            }}
            .feature {{
                padding: 10px;
                margin: 10px 0;
                background-color: #f0f9ff;
                border-left: 4px solid #2563eb;
            }}
            .button {{
                display: inline-block;
                background-color: #2563eb;
                color: white;
                padding: 12px 30px;
                border-radius: 5px;
                text-decoration: none;
                margin: 20px 0;
            }}
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #e5e7eb;
                font-size: 12px;
                color: #666;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Welcome to Jobify!</h1>
            </div>
            
            <p>Hi {full_name},</p>
            
            <p>Your account has been successfully verified! 🎉</p>
            
            <p>You can now access all the features of Jobify:</p>
            
            <div class="features">
                <div class="feature">
                    <strong>💼 Job Search</strong> - Find jobs from multiple sources
                </div>
                <div class="feature">
                    <strong>📄 Resume Analyzer</strong> - Get AI-powered resume feedback
                </div>
                <div class="feature">
                    <strong>📧 Email Automation</strong> - Send personalized cold emails
                </div>
                <div class="feature">
                    <strong>📊 Dashboard</strong> - Track your applications
                </div>
            </div>
            
            <p>Let's get started on your journey to landing your dream job!</p>
            
            <div class="footer">
                <p>&copy; 2024 Jobify. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

# ==================== EMAIL SENDING FUNCTIONS ====================

def send_otp_email(email: str, otp_code: str) -> bool:
    """Send OTP email to user."""
    try:
        if not SMTP_USERNAME or not SMTP_PASSWORD:
            logger.warning("[EMAIL] SMTP credentials not configured. OTP not sent.")
            print(f"[EMAIL] [DEMO MODE] OTP {otp_code} would be sent to {email}")
            return True
        
        print(f"[EMAIL] 📧 Attempting to send OTP to {email}")
        print(f"[EMAIL] From: {SMTP_USERNAME}")
        
        # Create email
        message = MIMEMultipart("alternative")
        message["Subject"] = "🔐 Jobify Email Verification Code"
        message["From"] = SMTP_USERNAME
        message["To"] = email
        
        # Email body
        html_content = get_otp_email_html(otp_code, email)
        part = MIMEText(html_content, "html")
        message.attach(part)
        
        # Send email with detailed error handling
        print(f"[EMAIL] Connecting to {SMTP_SERVER}:{SMTP_PORT}")
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
            print("[EMAIL] Connected. Starting TLS...")
            server.starttls()
            print(f"[EMAIL] TLS started. Logging in as {SMTP_USERNAME}")
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            print("[EMAIL] Login successful. Sending email...")
            server.sendmail(SMTP_USERNAME, email, message.as_string())
            print("[EMAIL] Email sent successfully!")
        
        logger.info(f"[EMAIL] OTP email sent to {email}")
        print(f"[EMAIL] ✅ OTP sent to {email}")
        return True
    
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"[EMAIL] Authentication failed: {str(e)}")
        print(f"[EMAIL] ❌ SMTP Auth Error: {str(e)}")
        print(f"[EMAIL] Check: 1) Email is correct 2) App password is correct (no spaces)")
        return False
    
    except smtplib.SMTPException as e:
        logger.error(f"[EMAIL] SMTP error: {str(e)}")
        print(f"[EMAIL] ❌ SMTP Error: {str(e)}")
        return False
    
    except TimeoutError:
        logger.error("[EMAIL] Connection timeout")
        print("[EMAIL] ❌ Connection timeout - Gmail server not responding")
        return False
    
    except Exception as e:
        logger.error(f"[EMAIL] Error sending OTP: {str(e)}")
        print(f"[EMAIL] ❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def send_welcome_email(email: str, full_name: str) -> bool:
    """Send welcome email after successful verification."""
    try:
        if not SMTP_USERNAME or not SMTP_PASSWORD:
            logger.warning("[EMAIL] SMTP credentials not configured. Welcome email not sent.")
            return True
        
        # Create email
        message = MIMEMultipart("alternative")
        message["Subject"] = f"🎉 Welcome to Jobify, {full_name}!"
        message["From"] = SMTP_USERNAME
        message["To"] = email
        
        # Email body
        html_content = get_welcome_email_html(full_name)
        part = MIMEText(html_content, "html")
        message.attach(part)
        
        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, email, message.as_string())
        
        logger.info(f"[EMAIL] Welcome email sent to {email}")
        print(f"[EMAIL] ✅ Welcome email sent to {email}")
        return True
    
    except Exception as e:
        logger.error(f"[EMAIL] Error sending welcome email: {str(e)}")
        print(f"[EMAIL] ❌ Error sending welcome email: {str(e)}")
        return False

def send_password_reset_email(email: str, reset_link: str) -> bool:
    """Send password reset email."""
    try:
        if not SMTP_USERNAME or not SMTP_PASSWORD:
            return True
        
        message = MIMEMultipart("alternative")
        message["Subject"] = "🔐 Reset Your Jobify Password"
        message["From"] = SMTP_USERNAME
        message["To"] = email
        
        html_content = f"""
        <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>We received a request to reset your password.</p>
            <p><a href="{reset_link}">Click here to reset your password</a></p>
            <p>This link will expire in 1 hour.</p>
        </body>
        </html>
        """
        
        part = MIMEText(html_content, "html")
        message.attach(part)
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, email, message.as_string())
        
        logger.info(f"[EMAIL] Password reset email sent to {email}")
        return True
    
    except Exception as e:
        logger.error(f"[EMAIL] Error sending reset email: {str(e)}")
        return False
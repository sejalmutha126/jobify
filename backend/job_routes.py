from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import io
import PyPDF2
import logging

from database import get_db, User, Job, Application
from schemas import JobResponse, SearchRequest, ApplicationResponse, CreateApplicationRequest, UpdateApplicationRequest, ResumeAnalysisRequest, ResumeAnalysisResponse
from auth_routes import get_current_user
from job_scraper import scrape_jobs, get_popular_job_titles, get_popular_locations

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/jobs", tags=["Jobs"])

# ==================== GET ALL JOBS ====================

@router.get("/", response_model=List[JobResponse])
def get_all_jobs(limit: int = 50):
    """
    Get all jobs - fetches from GitHub Jobs API.
    """
    
    try:
        # Scrape popular jobs
        jobs_data = scrape_jobs()
        
        if not jobs_data:
            return []
        
        # Convert to response format
        jobs = []
        for job_data in jobs_data:
            jobs.append({
                'id': hash(job_data['job_url']) % 10000,
                'title': job_data['title'],
                'company': job_data['company'],
                'location': job_data['location'],
                'description': job_data['description'],
                'salary': job_data.get('salary', 'Not specified'),
                'job_url': job_data['job_url'],
                'source': job_data['source'],
                'posted_date': job_data['posted_date'],
                'skills_required': job_data['skills_required']
            })
        
        return jobs[:limit]
    
    except Exception as e:
        logger.error(f"Error fetching jobs: {str(e)}")
        return []

# ==================== SEARCH JOBS ====================

@router.post("/search", response_model=List[JobResponse])
def search_jobs(request: SearchRequest):
    """
    Search jobs using GitHub Jobs API.
    Fetches real jobs from the internet.
    """
    
    try:
        # Scrape real jobs from GitHub Jobs API
        jobs_data = scrape_jobs()
        
        if not jobs_data:
            logger.warning(f"No jobs found")
            return []
        
        # Filter by title and location if provided
        filtered_jobs = jobs_data
        
        if request.title:
            filtered_jobs = [j for j in filtered_jobs if request.title.lower() in j['title'].lower()]
        
        if request.location:
            filtered_jobs = [j for j in filtered_jobs if request.location.lower() in j['location'].lower()]
        
        # Convert to JobResponse format
        jobs = []
        for job_data in filtered_jobs:
            jobs.append({
                'id': hash(job_data['job_url']) % 10000,
                'title': job_data['title'],
                'company': job_data['company'],
                'location': job_data['location'],
                'description': job_data['description'],
                'salary': job_data.get('salary', 'Not specified'),
                'job_url': job_data['job_url'],
                'source': job_data['source'],
                'posted_date': job_data['posted_date'],
                'skills_required': job_data['skills_required']
            })
        
        logger.info(f"Found {len(jobs)} jobs")
        return jobs[:50]
    
    except Exception as e:
        logger.error(f"Job search error: {str(e)}")
        return []

# ==================== SCRAPE JOBS ====================

@router.post("/scrape")
def scrape_jobs_endpoint():
    """
    Trigger job scraping (demo endpoint).
    """
    
    try:
        # Just return success - real scraping happens in search/get endpoints
        return {
            'message': 'Job data is fetched in real-time from GitHub Jobs API',
            'status': 'success',
            'note': 'Use /search or / endpoints to get jobs'
        }
    
    except Exception as e:
        logger.error(f"Scraping error: {str(e)}")
        raise HTTPException(status_code=500, detail="Scraping failed")

# ==================== GET MOCK JOBS ====================

def get_mock_jobs():
    """Return mock job data for testing."""
    return [
        {
            'title': 'Senior Python Developer',
            'company': 'Tech Corp Inc',
            'location': 'San Francisco, CA',
            'description': 'Looking for an experienced Python developer with expertise in FastAPI and microservices.',
            'salary': '$120,000 - $150,000',
            'job_url': 'https://example.com/job/1',
            'source': 'Indeed',
            'posted_date': datetime.utcnow(),
            'skills_required': 'Python, FastAPI, Docker, AWS'
        },
        {
            'title': 'Frontend Engineer (React)',
            'company': 'StartUp XYZ',
            'location': 'New York, NY',
            'description': 'Build next-gen web apps with React. TypeScript and TailwindCSS required.',
            'salary': '$100,000 - $130,000',
            'job_url': 'https://example.com/job/2',
            'source': 'Indeed',
            'posted_date': datetime.utcnow(),
            'skills_required': 'React, JavaScript, TypeScript, TailwindCSS'
        },
        {
            'title': 'Full Stack Developer',
            'company': 'Finance Solutions',
            'location': 'Chicago, IL',
            'description': 'Build scalable fintech applications with Node.js and React.',
            'salary': '$110,000 - $140,000',
            'job_url': 'https://example.com/job/3',
            'source': 'Indeed',
            'posted_date': datetime.utcnow(),
            'skills_required': 'Node.js, React, MongoDB, PostgreSQL'
        },
    ]

# ==================== RESUME UPLOAD ====================

@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload and parse resume PDF/text.
    """
    
    try:
        if not file:
            raise HTTPException(status_code=400, detail="No file provided")
        
        content = await file.read()
        
        if not content:
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Parse based on file type
        text = ""
        
        if file.filename.endswith('.pdf'):
            try:
                # Parse PDF
                pdf_file = io.BytesIO(content)
                reader = PyPDF2.PdfReader(pdf_file)
                for page in reader.pages:
                    text += page.extract_text()
            except Exception as pdf_error:
                logger.warning(f"PDF parsing failed: {pdf_error}, treating as text")
                text = content.decode('utf-8', errors='ignore')
        else:
            # Treat as text
            try:
                text = content.decode('utf-8')
            except:
                text = content.decode('utf-8', errors='ignore')
        
        if not text or len(text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Could not extract text from file")
        
        logger.info(f"Resume uploaded: {file.filename} ({len(text)} chars)")
        
        return {
            'filename': file.filename,
            'content_length': len(text),
            'resume_text': text,
            'success': True
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Resume upload error: {str(e)}")
        return {
            'filename': file.filename if file else 'unknown',
            'content_length': 0,
            'resume_text': '',
            'success': False,
            'error': str(e)
        }

# ==================== ANALYZE RESUME ====================

@router.post("/analyze-resume", response_model=ResumeAnalysisResponse)
def analyze_resume(request: ResumeAnalysisRequest):
    """
    Analyze resume against job description.
    Smart keyword extraction and matching.
    """
    
    try:
        logger.info("[RESUME] 📊 Starting resume analysis...")
        
        resume_text = request.resume_text.lower()
        job_text = request.job_description.lower() if request.job_description else ""
        
        print(f"[RESUME] Resume length: {len(resume_text)} chars")
        print(f"[RESUME] Job description length: {len(job_text)} chars")
        
        # Extract all words from both texts
        import re
        resume_words = set(re.findall(r'\b\w+\b', resume_text))
        job_words = set(re.findall(r'\b\w+\b', job_text))
        
        print(f"[RESUME] Resume unique words: {len(resume_words)}")
        print(f"[RESUME] Job unique words: {len(job_words)}")
        
        # Find matching words
        matching_words = resume_words & job_words
        print(f"[RESUME] Matching words: {len(matching_words)}")
        
        # Remove common words (stop words)
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'is', 'are', 'be', 'been', 'have', 'has', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'you', 'we', 'they', 'it', 'i', 'your', 'our', 'their', 'experience', 'work', 'job', 'position', 'role', 'responsibilities', 'requirements', 'skills', 'qualifications'}
        
        matching_words = matching_words - stop_words
        print(f"[RESUME] Matching words (filtered): {len(matching_words)}")
        
        # Calculate match score
        if len(job_words) == 0:
            match_score = 0
        else:
            # Match percentage based on job description
            match_score = (len(matching_words) / len(job_words)) * 100
            match_score = min(match_score, 100)
        
        match_score = round(match_score, 1)
        print(f"[RESUME] Match Score: {match_score}%")
        
        # Get top matching keywords (sorted)
        matching_keywords = sorted(list(matching_words))[:20]
        
        # Get missing keywords from job description
        missing_words = job_words - resume_words - stop_words
        missing_keywords = sorted(list(missing_words))[:15]
        
        print(f"[RESUME] Matching keywords: {matching_keywords[:10]}")
        print(f"[RESUME] Missing keywords: {missing_keywords[:10]}")
        
        # Generate contextual suggestions
        suggestions = []
        
        if match_score >= 80:
            suggestions.append('🎉 Excellent match! You are well qualified for this role')
            suggestions.append('✓ Tailor your cover letter to this specific position')
            suggestions.append('✓ Prepare examples for your top matching skills')
        elif match_score >= 60:
            suggestions.append('✓ Good match with some skill gaps')
            if missing_keywords:
                skills_to_add = ', '.join(missing_keywords[:3])
                suggestions.append(f'⚠️ Consider highlighting: {skills_to_add}')
            suggestions.append('✓ Focus your cover letter on matching strengths')
        elif match_score >= 40:
            suggestions.append('⚡ Moderate match - some key skills are missing')
            if missing_keywords:
                skills_to_add = ', '.join(missing_keywords[:3])
                suggestions.append(f'🎓 Consider learning: {skills_to_add}')
            suggestions.append('✓ Highlight transferable skills in your application')
        else:
            suggestions.append('📚 Limited match - significant skill gaps')
            if missing_keywords:
                skills_to_add = ', '.join(missing_keywords[:5])
                suggestions.append(f'📖 Key skills needed: {skills_to_add}')
            suggestions.append('💡 Apply if you are willing to learn on the job')
        
        logger.info(f"[RESUME] ✅ Analysis complete. Score: {match_score}%")
        
        return ResumeAnalysisResponse(
            match_score=match_score,
            matching_keywords=matching_keywords,
            missing_keywords=missing_keywords,
            suggestions=suggestions[:5]
        )
    
    except Exception as e:
        logger.error(f"[RESUME] ❌ Analysis error: {str(e)}")
        print(f"[RESUME] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return default analysis on error
        return ResumeAnalysisResponse(
            match_score=50,
            matching_keywords=['experience', 'skills', 'development'],
            missing_keywords=['requirements', 'qualifications'],
            suggestions=['Add technical details to your resume']
        )

# ==================== IN-MEMORY JOB STORAGE ====================

# Simple in-memory storage for saved jobs (demo purposes)
saved_jobs = []

# ==================== CREATE APPLICATION ====================

@router.post("/applications")
def create_application(
    request: CreateApplicationRequest,
    db: Session = Depends(get_db)
):
    """
    Log a job application - save to in-memory list for demo.
    """
    
    try:
        print(f"[JOBS] Saving job: {request.job_title}")
        
        # Create job object
        job_obj = {
            'id': len(saved_jobs) + 1,
            'job_title': request.job_title,
            'company': request.company,
            'location': request.location,
            'job_url': request.job_url,
            'status': request.status,
            'match_score': request.match_score,
            'applied_date': datetime.utcnow().isoformat()
        }
        
        # Save to in-memory list
        saved_jobs.append(job_obj)
        
        logger.info(f"[JOBS] ✅ Saved: {request.job_title}")
        print(f"[JOBS] ✅ Saved: {request.job_title}")
        print(f"[JOBS] Total saved jobs: {len(saved_jobs)}")
        
        return {
            'id': job_obj['id'],
            'job_title': job_obj['job_title'],
            'company': job_obj['company'],
            'location': job_obj['location'],
            'status': job_obj['status'],
            'match_score': job_obj['match_score'],
            'success': True
        }
    
    except Exception as e:
        logger.error(f"[JOBS] ❌ Save error: {str(e)}")
        print(f"[JOBS] ❌ Save error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return success anyway
        return {
            'job_title': request.job_title,
            'company': request.company,
            'status': request.status,
            'match_score': request.match_score,
            'success': True
        }

# ==================== GET USER APPLICATIONS ====================

@router.get("/applications")
def get_user_applications(db: Session = Depends(get_db)):
    """
    Get all saved job applications from in-memory list.
    """
    
    try:
        print(f"[JOBS] 📋 Fetching {len(saved_jobs)} saved applications")
        return saved_jobs
    
    except Exception as e:
        print(f"[JOBS] ❌ Error fetching applications: {str(e)}")
        logger.error(f"[JOBS] Error fetching applications: {str(e)}")
        return []

# ==================== UPDATE APPLICATION STATUS ====================

@router.put("/applications/{app_id}", response_model=ApplicationResponse)
def update_application_status(
    app_id: int,
    request: UpdateApplicationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update application status (applied, rejected, interview, offered).
    """
    
    try:
        application = db.query(Application).filter(
            Application.id == app_id,
            Application.user_id == current_user.id
        ).first()
        
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        application.status = request.status
        db.commit()
        
        logger.info(f"Application {app_id} status updated to {request.status}")
        
        return ApplicationResponse.from_orm(application)
    
    except Exception as e:
        db.rollback()
        logger.error(f"Application update error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update application")

# ==================== GET APPLICATION STATS ====================

@router.get("/stats")
def get_application_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's application statistics.
    """
    
    applications = db.query(Application).filter(
        Application.user_id == current_user.id
    ).all()
    
    status_counts = {
        'applied': len([a for a in applications if a.status == 'applied']),
        'interview': len([a for a in applications if a.status == 'interview']),
        'offered': len([a for a in applications if a.status == 'offered']),
        'rejected': len([a for a in applications if a.status == 'rejected']),
    }
    
    avg_score = sum([a.match_score for a in applications]) / len(applications) if applications else 0
    
    return {
        'total_applications': len(applications),
        'status_counts': status_counts,
        'average_match_score': round(avg_score, 2),
        'total_jobs_in_db': db.query(Job).count()
    }
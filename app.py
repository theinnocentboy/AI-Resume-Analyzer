from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_session import Session
from functools import wraps
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import json
import pdfplumber
import re
from dotenv import load_dotenv
from models import db, User, Resume, AnalysisReport
import groq
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url


load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
# Fetch the database URL from the environment
db_url = os.environ.get('DATABASE_URL', 'sqlite:///resume_analyzer.db')

# Render provides URLs starting with 'postgres://', but SQLAlchemy requires 'postgresql://'
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
# Configure Cloudinary using environment variables
cloudinary.config( 
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'), 
    api_key = os.environ.get('CLOUDINARY_API_KEY'), 
    api_secret = os.environ.get('CLOUDINARY_API_SECRET') 
)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf'}

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize extensions
db.init_app(app)
Session(app)

with app.app_context():
    db.create_all()

# Initialize Groq client
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
groq_client = groq.Groq(api_key=GROQ_API_KEY)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def extract_text_from_pdf(file_path):
    """Extract text from PDF file using pdfplumber"""
    try:
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise Exception(f"Error extracting PDF text: {str(e)}")


def analyze_resume_with_ai(resume_text):
    """
    Analyze resume using Groq API with Llama model
    Returns structured analysis with scores and insights
    """
    
    # Refined prompt for better AI analysis
    analysis_prompt = f"""You are an expert resume analyzer and ATS (Applicant Tracking System) specialist with 20+ years of recruiting experience.

Analyze the following resume and provide a comprehensive evaluation:

RESUME CONTENT:
{resume_text}

IMPORTANT: Respond ONLY with valid JSON (no markdown, no code blocks, no extra text). Use exactly this structure:

{{
    "resume_score": <number 0-100>,
    "ats_score": <number 0-100>,
    "skills_identified": [<list of 10-15 technical and soft skills found>],
    "missing_skills": [<list of 5-10 in-demand skills that are missing>],
    "strengths": [<list of 3-5 key strengths>],
    "weaknesses": [<list of 3-5 areas for improvement>],
    "improvements": [<list of 5-7 specific actionable suggestions>],
    "summary_review": "<2-3 paragraph professional assessment>"
}}

Scoring Guidelines:
- Resume Score: Overall quality (0-100). Consider structure, clarity, achievement metrics, keyword relevance
- ATS Score: How well the resume will pass ATS systems (0-100). Consider formatting, keywords, standard sections

Be strict but fair. Provide honest feedback."""

    try:
        # CORRECTED: Use the updated model name
        chat_completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # <--- CHANGE THIS LINE
            max_tokens=2000,
            messages=[
                {
                    "role": "user",
                    "content": analysis_prompt
                }
            ]
        )
        
        # CORRECTED: Access the response text using the completions structure
        response_text = chat_completion.choices[0].message.content.strip()
        
        # Parse JSON response
        # Groq might occasionally wrap JSON in markdown blocks (```json ... ```)
        # This small cleanup ensures json.loads doesn't fail if that happens
        if response_text.startswith("```json"):
            response_text = response_text[7:-3].strip()
        elif response_text.startswith("```"):
            response_text = response_text[3:-3].strip()
            
        analysis_data = json.loads(response_text)
        return analysis_data
        
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse AI response as JSON: {str(e)}")
    except Exception as e:
        raise Exception(f"Error analyzing resume: {str(e)}")


def compare_with_job_description(resume_text, job_description):
    """
    Compare resume with job description and identify gaps
    """
    
    comparison_prompt = f"""You are an expert recruiter analyzing resume-job fit.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Analyze how well the resume matches the job description. Respond ONLY with valid JSON:

{{
    "match_score": <number 0-100>,
    "missing_keywords": [<list of important keywords/skills from JD not in resume>],
    "matched_keywords": [<list of keywords present in both>],
    "suggestions": [<list of 5-7 specific ways to improve resume for this role>],
    "analysis": "<2-3 paragraph analysis of fit>"
}}"""

    try:
        # CORRECTED: Use the updated model name
        chat_completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # <--- CHANGE THIS LINE
            max_tokens=1500,
            messages=[
                {
                    "role": "user",
                    "content": comparison_prompt
                }
            ]
        )
        
        # CORRECTED: Access the response text correctly
        response_text = chat_completion.choices[0].message.content.strip()
        
        # JSON cleanup just in case
        if response_text.startswith("```json"):
            response_text = response_text[7:-3].strip()
        elif response_text.startswith("```"):
            response_text = response_text[3:-3].strip()
            
        comparison_data = json.loads(response_text)
        return comparison_data
        
    except Exception as e:
        raise Exception(f"Error comparing with job description: {str(e)}")


# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.route('/')
def home():
    """Home page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not all([name, email, password, confirm_password]):
            flash('All fields are required', 'danger')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'danger')
            return redirect(url_for('register'))
        
        # Check if user exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))
        
        # Create new user
        try:
            user = User(name=name, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error during registration: {str(e)}', 'danger')
            return redirect(url_for('register'))
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Email and password are required', 'danger')
            return redirect(url_for('login'))
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_email'] = user.email
            session.permanent = True
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
            return redirect(url_for('login'))
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('home'))


@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    user = User.query.get(session['user_id'])
    total_resumes = Resume.query.filter_by(user_id=user.id).count()
    total_analyses = AnalysisReport.query.filter_by(user_id=user.id).count()
    
    avg_score = db.session.query(db.func.avg(AnalysisReport.resume_score)).filter(
        AnalysisReport.user_id == user.id
    ).scalar() or 0
    
    return render_template('profile.html', 
                         user=user,
                         total_resumes=total_resumes,
                         total_analyses=total_analyses,
                         avg_score=round(avg_score, 2))


# ============================================================================
# DASHBOARD ROUTES
# ============================================================================

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard with statistics"""
    user_id = session['user_id']
    
    # Get statistics
    total_resumes = Resume.query.filter_by(user_id=user_id).count()
    total_analyses = AnalysisReport.query.filter_by(user_id=user_id).count()
    
    avg_resume_score = db.session.query(db.func.avg(AnalysisReport.resume_score)).filter(
        AnalysisReport.user_id == user_id
    ).scalar() or 0
    
    avg_ats_score = db.session.query(db.func.avg(AnalysisReport.ats_score)).filter(
        AnalysisReport.user_id == user_id
    ).scalar() or 0
    
    # Get recent analyses
    recent_reports = AnalysisReport.query.filter_by(user_id=user_id).order_by(
        AnalysisReport.created_at.desc()
    ).limit(5).all()
    
    return render_template('dashboard.html',
                         total_resumes=total_resumes,
                         total_analyses=total_analyses,
                         avg_resume_score=round(avg_resume_score, 1),
                         avg_ats_score=round(avg_ats_score, 1),
                         recent_reports=recent_reports)


# ============================================================================
# RESUME UPLOAD & ANALYSIS ROUTES
# ============================================================================

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_resume():
    """Upload resume and extract text"""
    if request.method == 'POST':
        # Check if file is present
        if 'resume_file' not in request.files:
            flash('No file selected', 'danger')
            return redirect(url_for('upload_resume'))
        
        file = request.files['resume_file']
        
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(url_for('upload_resume'))
        
        if not allowed_file(file.filename):
            flash('Only PDF files are allowed', 'danger')
            return redirect(url_for('upload_resume'))
        
        
        try:
            # 1. Save file locally (temporarily for text extraction)
            filename = secure_filename(f"{datetime.utcnow().timestamp()}_{file.filename}")
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # 2. Extract text using your existing pdfplumber function
            extracted_text = extract_text_from_pdf(file_path)
            
            if not extracted_text.strip():
                if os.path.exists(file_path):
                    os.remove(file_path)
                flash('Could not extract text from PDF', 'danger')
                return redirect(url_for('upload_resume'))

            # 3. Upload the PDF to Cloudinary (resource_type="raw" preserves the PDF format)
            upload_result = cloudinary.uploader.upload(file_path, resource_type="raw")
            secure_cloud_url = upload_result.get("secure_url")
            
            # 4. Clean up the local ephemeral disk space immediately
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # 5. Save record to PostgreSQL using the Cloud URL instead of the local path
            resume = Resume(
                user_id=session['user_id'],
                filename=filename,
                original_filename=file.filename,
                file_path=secure_cloud_url,  # The permanent cloud link
                file_size=upload_result.get("bytes", 0),
                extracted_text=extracted_text
            )
            db.session.add(resume)
            db.session.commit()
            
            flash('Resume uploaded securely to the cloud!', 'success')
            return redirect(url_for('analyze_resume', resume_id=resume.id))
            
        except Exception as e:
            db.session.rollback()
            # Failsafe cleanup to avoid accumulating files if the upload fails mid-way
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)
            flash(f'Error uploading resume: {str(e)}', 'danger')
            return redirect(url_for('upload_resume'))
    
    return render_template('upload.html')


@app.route('/analyze/<int:resume_id>')
@login_required
def analyze_resume(resume_id):
    """Analyze resume using AI"""
    resume = Resume.query.get_or_404(resume_id)
    
    # Check if user owns this resume
    if resume.user_id != session['user_id']:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('dashboard'))
    
    try:
        # Analyze resume
        analysis_data = analyze_resume_with_ai(resume.extracted_text)
        
        # Save analysis to database
        report = AnalysisReport(
            user_id=session['user_id'],
            resume_id=resume_id,
            resume_score=analysis_data.get('resume_score', 0),
            ats_score=analysis_data.get('ats_score', 0),
            skills_identified=json.dumps(analysis_data.get('skills_identified', [])),
            missing_skills=json.dumps(analysis_data.get('missing_skills', [])),
            strengths=json.dumps(analysis_data.get('strengths', [])),
            weaknesses=json.dumps(analysis_data.get('weaknesses', [])),
            improvements=json.dumps(analysis_data.get('improvements', [])),
            summary_review=analysis_data.get('summary_review', ''),
            analysis_text=json.dumps(analysis_data)
        )
        db.session.add(report)
        db.session.commit()
        
        flash('Resume analyzed successfully!', 'success')
        return redirect(url_for('view_analysis', report_id=report.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error analyzing resume: {str(e)}', 'danger')
        return redirect(url_for('upload_resume'))


@app.route('/analysis/<int:report_id>')
@login_required
def view_analysis(report_id):
    """View analysis report"""
    report = AnalysisReport.query.get_or_404(report_id)
    
    # Check authorization
    if report.user_id != session['user_id']:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('dashboard'))
    # Parse JSON fields safely
    analysis_dict = json.loads(report.analysis_text) if report.analysis_text else {}
    
    data = {
        'report': report,
        'skills': json.loads(report.skills_identified) if report.skills_identified else [],
        'missing_skills': json.loads(report.missing_skills) if report.missing_skills else [],
        'strengths': json.loads(report.strengths) if report.strengths else [],
        'weaknesses': json.loads(report.weaknesses) if report.weaknesses else [],
        'improvements': json.loads(report.improvements) if report.improvements else [],
        'missing_keywords': json.loads(report.missing_keywords) if report.missing_keywords else [],
        'matched_keywords': analysis_dict.get('matched_keywords', []) # Safe extraction
    }
    
    return render_template('analysis.html', **data)


# ============================================================================
# JOB MATCHING ROUTES
# ============================================================================

@app.route('/job-match/<int:resume_id>', methods=['GET', 'POST'])
@login_required
def job_match(resume_id):
    """Compare resume with job description"""
    resume = Resume.query.get_or_404(resume_id)
    
    if resume.user_id != session['user_id']:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        job_description = request.form.get('job_description')
        
        if not job_description or len(job_description) < 50:
            flash('Please provide a valid job description (at least 50 characters)', 'danger')
            return redirect(url_for('job_match', resume_id=resume_id))
        
        try:
            # Compare with job description
            comparison = compare_with_job_description(resume.extracted_text, job_description)
            
            # Check if analysis already exists
            report = AnalysisReport.query.filter_by(
                resume_id=resume_id,
                job_description=job_description
            ).first()
            
            if not report:
                report = AnalysisReport(
                    user_id=session['user_id'],
                    resume_id=resume_id,
                    job_description=job_description
                )
            
            # Update comparison data
            report.match_score = comparison.get('match_score', 0)
            report.missing_keywords = json.dumps(comparison.get('missing_keywords', []))
            report.job_match_suggestions = json.dumps(comparison.get('suggestions', []))
            report.analysis_text = json.dumps(comparison)
            
            db.session.add(report)
            db.session.commit()
            
            flash('Job matching completed!', 'success')
            return redirect(url_for('view_job_match', report_id=report.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error matching with job description: {str(e)}', 'danger')
            return redirect(url_for('job_match', resume_id=resume_id))
    
    return render_template('job_match.html', resume=resume)


@app.route('/job-match-result/<int:report_id>')
@login_required
def view_job_match(report_id):
    """View job matching results"""
    report = AnalysisReport.query.get_or_404(report_id)
    
    if report.user_id != session['user_id']:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('dashboard'))
    
    data = {
        'report': report,
        'missing_keywords': json.loads(report.missing_keywords) if report.missing_keywords else [],
        'suggestions': json.loads(report.job_match_suggestions) if report.job_match_suggestions else [],
        'analysis': json.loads(report.analysis_text).get('analysis', '') if report.analysis_text else ''
    }
    
    return render_template('job_match_result.html', **data)


# ============================================================================
# REPORT HISTORY ROUTES
# ============================================================================

@app.route('/history')
@login_required
def history():
    """View all analysis reports"""
    page = request.args.get('page', 1, type=int)
    reports = AnalysisReport.query.filter_by(user_id=session['user_id']).order_by(
        AnalysisReport.created_at.desc()
    ).paginate(page=page, per_page=10)
    
    return render_template('history.html', reports=reports)


@app.route('/report/<int:report_id>/delete', methods=['POST'])
@login_required
def delete_report(report_id):
    """Delete a report"""
    report = AnalysisReport.query.get_or_404(report_id)
    
    if report.user_id != session['user_id']:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('dashboard'))
    
    try:
        db.session.delete(report)
        db.session.commit()
        flash('Report deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting report: {str(e)}', 'danger')
    
    return redirect(url_for('history'))


# ============================================================================
# API ROUTES (for AJAX requests)
# ============================================================================

@app.route('/api/resume-stats')
@login_required
def api_resume_stats():
    """API endpoint for resume statistics"""
    user_id = session['user_id']
    
    last_30_days = datetime.utcnow() - timedelta(days=30)
    
    stats = {
        'total_resumes': Resume.query.filter_by(user_id=user_id).count(),
        'total_analyses': AnalysisReport.query.filter_by(user_id=user_id).count(),
        'analyses_30_days': AnalysisReport.query.filter(
            AnalysisReport.user_id == user_id,
            AnalysisReport.created_at >= last_30_days
        ).count(),
        'avg_resume_score': round(
            db.session.query(db.func.avg(AnalysisReport.resume_score)).filter(
                AnalysisReport.user_id == user_id
            ).scalar() or 0, 2
        ),
        'avg_ats_score': round(
            db.session.query(db.func.avg(AnalysisReport.ats_score)).filter(
                AnalysisReport.user_id == user_id
            ).scalar() or 0, 2
        )
    }
    
    return jsonify(stats)


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    db.session.rollback()
    return render_template('500.html'), 500


# ============================================================================
# CONTEXT PROCESSORS
# ============================================================================

@app.context_processor
def inject_user():
    """Make user info available to all templates"""
    if 'user_id' in session:
        return dict(
            logged_in=True,
            user_name=session.get('user_name', 'User'),
            user_email=session.get('user_email', '')
        )
    return dict(logged_in=False)


# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def init_db():
    """Initialize database"""
    with app.app_context():
        db.create_all()
        print("Database initialized successfully!")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    init_db()
    
    # Check for required environment variables
    if GROQ_API_KEY == 'your-groq-api-key':
        print("WARNING: GROQ_API_KEY not set. Please set it as an environment variable.")
        print("Get your API key from: https://console.groq.com")
    
    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=os.environ.get('FLASK_ENV') == 'development'
    )

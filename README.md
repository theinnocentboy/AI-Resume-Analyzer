# ResumeAI - AI-Powered Resume Analyzer

A modern, professional web application for analyzing resumes using artificial intelligence (Groq API with Llama model). The application provides comprehensive feedback on resume quality, ATS compatibility, skill analysis, and job matching.

## 📋 Features

### Core Features
- **User Authentication**: Secure registration and login with password hashing
- **Resume Upload**: Upload PDF resumes for analysis
- **AI Analysis**: Advanced resume analysis using Groq API (Llama 3.1 70B)
- **Scoring System**:
  - Resume Quality Score (0-100)
  - ATS (Applicant Tracking System) Score (0-100)
  - Job Match Percentage
- **Detailed Insights**:
  - Skills Identified
  - Missing Skills
  - Strengths and Weaknesses
  - Actionable Improvement Suggestions
  - Professional Summary Review
- **Job Matching**: Compare resume with job descriptions
- **Report History**: Save and view past analyses
- **Dashboard**: Statistics and analytics
- **User Profile**: Account management and statistics

### Technical Features
- Modern Bootstrap 5 UI with glassmorphism design
- Responsive layout for all devices
- Secure file upload with validation
- SQLite database for data persistence
- Session management for user authentication
- CSRF protection
- Error handling and logging

## 🛠️ Tech Stack

- **Backend**: Flask 3.0.0
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: Bootstrap 5, HTML5, JavaScript
- **AI**: Groq API (Llama 3.1 70B model)
- **PDF Processing**: pdfplumber
- **Web Server**: Gunicorn

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Groq API key (free from https://console.groq.com)

### Local Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd resume_analyzer
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Create environment configuration**
```bash
cp .env.example .env
```

5. **Update .env file**
```
FLASK_ENV=development
SECRET_KEY=your-super-secret-key
GROQ_API_KEY=your-groq-api-key
```

6. **Create uploads directory**
```bash
mkdir uploads
```

7. **Run the application**
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 🚀 Deployment on Render

### Step-by-Step Deployment

1. **Push your code to GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-github-repo>
git push -u origin main
```

2. **Create a Render account** at https://render.com

3. **Create a new Web Service**
   - Connect your GitHub repository
   - Select the repository
   - Choose "Python" as the runtime

4. **Configure Environment**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn --workers 4 --threads 2 --worker-class gthread --bind 0.0.0.0:$PORT app:app`

5. **Add Environment Variables in Render Dashboard**
   - `FLASK_ENV`: `production`
   - `SECRET_KEY`: Generate a secure key
   - `GROQ_API_KEY`: Your Groq API key
   - `SQLALCHEMY_DATABASE_URI`: `sqlite:///resume_analyzer.db`

6. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete
   - Your app will be available at the provided URL

## 📁 Project Structure

```
resume_analyzer/
├── app.py                    # Main Flask application
├── models.py                 # SQLAlchemy models
├── requirements.txt          # Python dependencies
├── Procfile                  # Render/Heroku deployment config
├── render.yaml              # Render deployment configuration
├── .env.example             # Environment variables template
├── .gitignore              # Git ignore file
├── README.md               # This file
├── uploads/                # User-uploaded resumes (directory)
├── flask_session/          # Session files (auto-created)
│
└── templates/              # HTML Templates
    ├── base.html          # Base template with navigation
    ├── home.html          # Home page
    ├── login.html         # Login page
    ├── register.html      # Registration page
    ├── dashboard.html     # User dashboard
    ├── upload.html        # Resume upload page
    ├── analysis.html      # Analysis results page
    ├── job_match.html     # Job matching input
    ├── job_match_result.html  # Job matching results
    ├── history.html       # Report history page
    ├── profile.html       # User profile page
    ├── 404.html          # 404 error page
    └── 500.html          # 500 error page
```

## 🔐 Security Features

- **Password Hashing**: Using Werkzeug's secure password hashing
- **Session Management**: Secure Flask sessions
- **CSRF Protection**: Built-in Flask security
- **File Validation**: Only PDF files allowed, with size limits
- **SQL Injection Prevention**: Using SQLAlchemy ORM
- **Data Encryption**: Sensitive data handling

## 📊 Database Schema

### Users Table
```sql
- id (Primary Key)
- name (String)
- email (Unique)
- password_hash (String)
- created_at (DateTime)
- updated_at (DateTime)
```

### Resumes Table
```sql
- id (Primary Key)
- user_id (Foreign Key)
- filename (String)
- original_filename (String)
- file_path (String)
- file_size (Integer)
- upload_date (DateTime)
- extracted_text (Text)
```

### Analysis Reports Table
```sql
- id (Primary Key)
- user_id (Foreign Key)
- resume_id (Foreign Key)
- resume_score (Float)
- ats_score (Float)
- match_score (Float)
- skills_identified (JSON)
- missing_skills (JSON)
- strengths (JSON)
- weaknesses (JSON)
- improvements (JSON)
- summary_review (Text)
- job_description (Text)
- missing_keywords (JSON)
- analysis_text (JSON)
- created_at (DateTime)
```

## 🤖 AI Analysis Details

### Resume Analysis Prompt
The application uses this prompt structure for analyzing resumes:

```
You are an expert resume analyzer and ATS specialist with 20+ years of recruiting experience.

Analyze the following resume and provide:
1. Resume Score (0-100) - Overall quality
2. ATS Score (0-100) - ATS system compatibility
3. Skills Identified - List of 10-15 technical and soft skills
4. Missing Skills - List of 5-10 in-demand skills not present
5. Strengths - 3-5 key strengths
6. Weaknesses - 3-5 areas for improvement
7. Improvements - 5-7 actionable suggestions
8. Professional Summary - 2-3 paragraph assessment

Response Format: JSON only
```

### Job Matching Analysis
```
Compare resume with job description to:
1. Calculate match percentage (0-100)
2. Identify matched keywords
3. Identify missing keywords
4. Provide improvement suggestions
5. Give detailed analysis

Response Format: JSON only
```

## 🔑 API Endpoints

### Authentication
- `POST /register` - User registration
- `POST /login` - User login
- `GET /logout` - User logout

### Dashboard
- `GET /dashboard` - Main dashboard
- `GET /` - Home page (redirects to dashboard if logged in)

### Resume Management
- `GET /upload` - Upload page
- `POST /upload` - Upload resume
- `GET /analyze/<resume_id>` - Trigger analysis
- `GET /analysis/<report_id>` - View analysis results

### Job Matching
- `GET /job-match/<resume_id>` - Job matching input page
- `POST /job-match/<resume_id>` - Submit for analysis
- `GET /job-match-result/<report_id>` - View results

### Reports
- `GET /history` - View all reports
- `POST /report/<report_id>/delete` - Delete report

### API
- `GET /api/resume-stats` - Get statistics (JSON)

## 🧪 Testing

Create a test user:
```
Email: test@example.com
Password: test123456
```

### Test Resume Analysis
1. Register/Login
2. Upload a PDF resume
3. Click "Analyze"
4. View detailed results

### Test Job Matching
1. View analysis results
2. Click "Compare with Job Description"
3. Paste a job description
4. See match results

## 🐛 Troubleshooting

### Issue: GROQ_API_KEY not set
**Solution**: 
1. Get your key from https://console.groq.com
2. Set it in your .env file
3. Restart the application

### Issue: PDF extraction fails
**Solution**:
1. Ensure PDF contains selectable text (not scanned images)
2. Try with a different PDF
3. Check PDF file size (max 16MB)

### Issue: Database errors
**Solution**:
```bash
# Delete old database
rm resume_analyzer.db

# The app will create a new one automatically
python app.py
```

### Issue: Port already in use
**Solution**:
```bash
# Use a different port
python -c "from app import app; app.run(port=5001)"
```

## 📝 Configuration

### Application Settings (in app.py)
```python
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'pdf'}  # Only PDF files
SESSION_LIFETIME = timedelta(days=7)  # Session duration
```

### Groq API Settings
- Model: `llama-3.1-70b-versatile`
- Max Tokens: 2000 per request
- Free tier includes generous limits

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the MIT License.

## 📧 Support

For issues and questions:
1. Check the Troubleshooting section
2. Review error messages in the application
3. Check Flask logs for detailed error information

## 🔄 Workflow Guide

### For Users

**First Time:**
1. Visit https://your-domain.com
2. Click "Get Started"
3. Create an account
4. Upload your resume (PDF)
5. Review AI analysis
6. Get improvement suggestions

**Regular Use:**
1. Login to dashboard
2. Upload new resume version
3. Track score improvements
4. Use job matching for specific positions
5. View analysis history

### For Developers

**Local Development:**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with credentials
echo "GROQ_API_KEY=your_key" > .env

# Run development server
python app.py

# Access at http://localhost:5000
```

**Making Changes:**
1. Modify files in templates/ or app.py
2. Refresh browser (no restart needed for templates)
3. Restart app if modifying app.py or models.py
4. Test all features
5. Commit and push changes

## 🎯 Performance Tips

- **Large Resumes**: Keep resumes under 2 pages for faster analysis
- **Batch Processing**: Analyze one resume at a time
- **Caching**: API responses are cached per session
- **Database**: SQLite is sufficient for small-medium apps

## 🔗 Useful Links

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Groq API Documentation](https://console.groq.com/docs)
- [Bootstrap 5](https://getbootstrap.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Render Deployment](https://render.com/docs)

## 📊 Version History

- **v1.0.0** - Initial release
  - User authentication
  - Resume upload and analysis
  - AI-powered feedback
  - Job matching
  - Report history
  - Responsive UI

---

**Created for B.Tech students and job seekers** 🎓💼

Happy resume analyzing! 🚀

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    """User model for authentication and resume management"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    resumes = db.relationship('Resume', backref='user', lazy=True, cascade='all, delete-orphan')
    analysis_reports = db.relationship('AnalysisReport', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'


class Resume(db.Model):
    """Resume model for storing uploaded resumes"""
    __tablename__ = 'resumes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)  # in bytes
    upload_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    extracted_text = db.Column(db.Text)
    
    # Relationships
    analysis_reports = db.relationship('AnalysisReport', backref='resume', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Resume {self.original_filename}>'


class AnalysisReport(db.Model):
    """Analysis report model for storing AI analysis results"""
    __tablename__ = 'analysis_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False, index=True)
    
    # Scores
    resume_score = db.Column(db.Float, default=0.0)
    ats_score = db.Column(db.Float, default=0.0)
    match_score = db.Column(db.Float, default=0.0)
    
    # Analysis Results (JSON-like text storage)
    skills_identified = db.Column(db.Text)  # JSON format
    missing_skills = db.Column(db.Text)  # JSON format
    strengths = db.Column(db.Text)  # JSON format
    weaknesses = db.Column(db.Text)  # JSON format
    improvements = db.Column(db.Text)  # JSON format
    summary_review = db.Column(db.Text)
    
    # Job Matching
    job_description = db.Column(db.Text)
    missing_keywords = db.Column(db.Text)  # JSON format
    job_match_suggestions = db.Column(db.Text)
    
    # Metadata
    analysis_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<AnalysisReport {self.id}>'

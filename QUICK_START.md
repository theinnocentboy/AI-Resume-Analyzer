# 🚀 Quick Start Guide - ResumeAI

Get your Resume Analyzer running in 5 minutes!

## Prerequisites Check

Before starting, make sure you have:
- ✓ Python 3.8 or higher installed
- ✓ A Groq API key (free from https://console.groq.com)
- ✓ A PDF resume to test with

## Windows Users

### Step 1: Run the Start Script
Double-click `run.bat` in the project folder.

The script will:
1. Create virtual environment
2. Install dependencies
3. Create necessary folders
4. Prompt you to add your Groq API key

### Step 2: Configure Groq API
When prompted, edit the `.env` file:
1. Open `.env` in Notepad
2. Find the line: `GROQ_API_KEY=your-groq-api-key-here`
3. Replace with your actual Groq API key
4. Save the file
5. Return to the command prompt and press Enter

### Step 3: Open Browser
The application will start automatically. Open:
```
http://localhost:5000
```

---

## macOS/Linux Users

### Step 1: Open Terminal
Navigate to the project folder:
```bash
cd /path/to/resume_analyzer
```

### Step 2: Make Script Executable
```bash
chmod +x run.sh
```

### Step 3: Run the Script
```bash
./run.sh
```

The script will handle all setup automatically.

### Step 4: Configure Groq API
When prompted:
1. Edit `.env` file with your favorite editor:
```bash
nano .env
# or
vim .env
```
2. Update `GROQ_API_KEY` with your actual key
3. Save and return to terminal
4. Press Enter to continue

### Step 5: Open Browser
Once the server starts, visit:
```
http://localhost:5000
```

---

## Manual Setup (All Platforms)

If the scripts don't work, follow these steps:

### 1. Create Virtual Environment
```bash
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
# Copy example file
cp .env.example .env  # macOS/Linux
copy .env.example .env  # Windows

# Edit .env and add your Groq API key
```

### 5. Create Required Folders
```bash
mkdir uploads
mkdir flask_session
```

### 6. Run Application
```bash
python app.py
```

---

## 🔑 Getting Your Groq API Key

### Free API Key (Recommended)

1. Go to https://console.groq.com
2. Click "Sign Up" (or "Sign In" if you have an account)
3. Verify your email
4. Go to "API Keys" section
5. Click "Create New API Key"
6. Copy the key
7. Paste in `.env` file

**Free tier includes:**
- Unlimited API calls
- All models available
- No credit card required
- Perfect for development

---

## First Time Usage

### Create Account
1. Click "Register" on home page
2. Enter name, email, password
3. Click "Create Account"

### Upload Resume
1. Go to Dashboard (after login)
2. Click "Upload New Resume"
3. Drag & drop or browse for a PDF
4. Click "Upload & Analyze Resume"

### View Analysis
- See Resume Score (0-100)
- See ATS Score (0-100)
- Review Skills Identified
- Check Improvement Suggestions
- Read Professional Summary

### Try Job Matching
1. Click "Compare with Job Description"
2. Paste a job posting
3. See Match Percentage
4. Get specific recommendations

---

## Troubleshooting

### Error: "GROQ_API_KEY not set"

**Solution:**
1. Make sure `.env` file exists
2. Check if `GROQ_API_KEY=your-key` is there
3. Restart the application
4. Test the API key: https://console.groq.com/keys

### Error: "Port 5000 already in use"

**Solution:**
1. Edit `app.py` (line at bottom)
2. Change: `port=int(os.environ.get('PORT', 5000))`
3. To: `port=int(os.environ.get('PORT', 5001))`
4. Restart application

### Error: "PDF extraction failed"

**Solution:**
1. Ensure PDF has selectable text (not scanned)
2. Try with a different PDF
3. Check file size (max 16MB)
4. Use online PDF converter if needed

### Virtual Environment Not Working

**Solution:**
```bash
# Delete existing environment
rm -rf venv  # macOS/Linux
rmdir /s venv  # Windows

# Create fresh environment
python -m venv venv

# Activate and reinstall
# (follow steps above)
```

---

## Features to Try

### 📊 Dashboard
- See all your statistics
- View recent analyses
- Track improvement over time

### 📁 Upload Multiple Resumes
- Analyze different versions
- Compare scores
- Track progress

### 🔗 Job Matching
- Compare with real job postings
- Get keyword suggestions
- Improve match percentage

### 📜 Report History
- Access all past analyses
- Search by filename
- Download results

### 👤 Profile
- View account details
- See overall statistics
- Manage your account

---

## Tips for Best Results

### Resume Formatting
- Use clear section headings
- Include measurable achievements
- List relevant skills
- Use standard fonts
- Keep to 1-2 pages

### For Job Matching
- Use complete job description
- Include all sections (responsibilities, requirements)
- Copy directly from job boards
- Provide context about the role

---

## Next Steps

1. **Upload Your Resume** - Start analyzing
2. **Try Job Matching** - Compare with target roles
3. **Implement Feedback** - Improve your resume
4. **Re-analyze** - Track progress
5. **Use Report History** - Monitor improvements

---

## Need Help?

### Check Documentation
- See `README.md` for detailed info
- Review error messages carefully
- Check browser console (F12)

### Common Issues
- Verify internet connection (needed for Groq API)
- Check Groq API status: https://console.groq.com
- Ensure .env file is in correct location
- Try clearing browser cache

### Debug Mode
To see detailed logs:

Edit `app.py`, find the last line:
```python
app.run(debug=True)  # Change to True
```

Then restart. More verbose output will appear.

---

## Performance Notes

- First load may take 5-10 seconds (AI analysis)
- Subsequent loads are faster
- Job matching may take 10-15 seconds
- Works best with modern browsers

---

**You're all set! Happy resume analyzing! 🚀**

For more information, see `README.md`

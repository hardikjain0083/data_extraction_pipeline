# GitHub Setup Guide

This guide will help you push your project to GitHub properly.

## Step-by-Step Instructions

### 1. Initialize Git Repository (if not already done)

```bash
git init
```

### 2. Check What Will Be Committed

The `.gitignore` file has been configured to exclude:
- ✅ All installed packages (groq, pandas, numpy, etc.)
- ✅ Virtual environment folders (venv/, env/)
- ✅ Cache files (__pycache__/, *.pyc)
- ✅ Runtime folders (uploads/, outputs/, extracted_images/)
- ✅ Environment files (.env)
- ✅ OS files (.DS_Store, Thumbs.db)

To see what will be committed:
```bash
git status
```

### 3. Add Files to Git

```bash
git add .
```

This will add only the files NOT in `.gitignore`.

### 4. Create Initial Commit

```bash
git commit -m "Initial commit: Education Data Extraction Pipeline"
```

### 5. Create GitHub Repository

1. Go to [GitHub.com](https://github.com)
2. Click the "+" icon → "New repository"
3. Name it (e.g., "edu-extraction-pipeline")
4. **DO NOT** initialize with README, .gitignore, or license (we already have these)
5. Click "Create repository"

### 6. Connect Local Repository to GitHub

```bash
# Add remote (replace <username> and <repo-name> with your values)
git remote add origin https://github.com/<username>/<repo-name>.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

### 7. Verify Upload

Visit your GitHub repository URL to verify all files are uploaded correctly.

## Files That Should Be on GitHub

✅ **Should be committed:**
- `app.py` - Flask application
- `pipeline.py` - Main pipeline
- `ner_groq.py` - NER processor
- `main.py` - Legacy GUI (optional)
- `requirements.txt` - Dependencies
- `README.md` - Documentation
- `SETUP.md` - Setup guide
- `.gitignore` - Git ignore rules
- `run.bat` / `run.sh` - Run scripts
- `templates/` - HTML templates
- `static/` - CSS and JS files
- `install_poppler.py` - Utility script (if needed)
- `test_*.py` - Test files (optional)

❌ **Should NOT be committed:**
- `.env` - Contains API keys
- `venv/` or `env/` - Virtual environment
- `__pycache__/` - Python cache
- `uploads/` - User uploaded files
- `outputs/` - Generated outputs
- `extracted_images/` - Extracted images
- All package folders (groq/, pandas/, etc.)

## Future Updates

When making changes:

```bash
# Check status
git status

# Add changes
git add .

# Commit
git commit -m "Description of changes"

# Push
git push
```

## Security Reminder

⚠️ **IMPORTANT:** Never commit:
- API keys or secrets
- `.env` file
- Personal data
- Large binary files

The `.gitignore` is configured to prevent this, but always double-check before committing!


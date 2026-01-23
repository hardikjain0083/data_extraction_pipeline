# Setup Guide - Education Data Extraction Pipeline

This guide will help you set up the project from scratch and run it with the frontend.

## Quick Start

### 1. Prerequisites Check

Make sure you have:
- ✅ Python 3.8+ installed
- ✅ pip installed
- ✅ Git installed (for version control)
- ✅ Groq API key ([Get one here](https://console.groq.com))

### 2. Project Setup

#### Step 1: Navigate to Project Directory
```bash
cd edu
```

#### Step 2: Create Virtual Environment

**Windows:**
```powershell
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt when activated.

#### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install:
- Flask (web framework)
- Groq (AI API client)
- PyMuPDF (PDF processing)
- Pandas (data processing)
- ReportLab (PDF generation)
- And other required packages

#### Step 4: Create Environment File

Create a `.env` file in the root directory:

**Windows (PowerShell):**
```powershell
New-Item -Path .env -ItemType File
```

**Linux/Mac:**
```bash
touch .env
```

Add your Groq API key to the `.env` file:
```
GROQ_API_KEY=your_actual_api_key_here
```

**⚠️ Important:** Replace `your_actual_api_key_here` with your actual Groq API key from [console.groq.com](https://console.groq.com)

### 3. Running the Application

#### Option A: Using Python Directly

```bash
python app.py
```

#### Option B: Using Run Scripts

**Windows:**
```bash
run.bat
```

**Linux/Mac:**
```bash
chmod +x run.sh
./run.sh
```

### 4. Access the Frontend

1. Open your web browser
2. Navigate to: `http://localhost:5000`
3. You should see the Education Data Extraction interface

### 5. Using the Application

1. **Upload PDF**: Click "Select File" or drag and drop a PDF file
2. **Process**: Click "Process Document" button
3. **Wait**: Processing may take 1-2 minutes depending on document size
4. **View Results**: Browse through tabs (Summary, Entities, Statistics, etc.)
5. **Download**: Click "Download CSV" or "Download PDF" to save results

## Troubleshooting

### Issue: "Module not found" errors

**Solution:** Make sure your virtual environment is activated and dependencies are installed:
```bash
# Activate venv first
pip install -r requirements.txt
```

### Issue: "GROQ_API_KEY not found"

**Solution:** 
1. Check that `.env` file exists in the root directory
2. Verify the API key is correctly formatted: `GROQ_API_KEY=your_key_here`
3. Make sure there are no extra spaces or quotes

### Issue: Port 5000 already in use

**Solution:** Change the port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Change 5000 to 5001
```

### Issue: PDF processing fails

**Solution:**
- Ensure PDF is not corrupted
- Try with a smaller PDF file first
- Check that PyMuPDF is installed: `pip install PyMuPDF`

### Issue: Frontend not loading

**Solution:**
- Check that Flask server is running
- Verify you're accessing `http://localhost:5000` (or the correct port)
- Check browser console for errors (F12)
- Ensure `templates/` and `static/` folders exist

## Project Structure

```
edu/
├── app.py              # Flask application (main entry point)
├── pipeline.py         # Data extraction pipeline
├── ner_groq.py         # Named Entity Recognition
├── main.py            # Legacy Tkinter GUI (optional)
├── requirements.txt   # Python dependencies
├── .env              # Environment variables (create this)
├── .gitignore        # Git ignore rules
├── run.bat           # Windows run script
├── run.sh            # Linux/Mac run script
├── templates/
│   └── index.html    # Frontend HTML
└── static/
    ├── css/
    │   └── style.css # Frontend styles
    └── js/
        └── main.js   # Frontend JavaScript
```

## Development Tips

1. **Always use virtual environment** - Keeps dependencies isolated
2. **Never commit `.env`** - Contains sensitive API keys
3. **Check logs** - Flask will show errors in the terminal
4. **Test with small PDFs first** - Faster iteration during development

## Next Steps

- Read the main [README.md](README.md) for detailed feature documentation
- Check API endpoints in README for integration options
- Customize extraction schema in `pipeline.py` if needed

---

**Need Help?** Check the main README.md or open an issue on GitHub.


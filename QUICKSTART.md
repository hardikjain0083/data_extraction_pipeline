# Quick Start Guide

## Setup (5 minutes)

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up API key**:
   - Create a `.env` file in the project root
   - Add: `GROQ_API_KEY=your_api_key_here`
   - Get your key from: https://console.groq.com

3. **Test API connection** (optional):
   ```bash
   python test_groq.py
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```
   Or use:
   - Windows: `run.bat`
   - Linux/Mac: `chmod +x run.sh && ./run.sh`

5. **Open browser**: Navigate to `http://localhost:5000`

## Usage

1. Upload a PDF document (drag & drop or click to browse)
2. Click "Process Document"
3. Wait for processing (1-2 minutes)
4. Browse results in different tabs
5. Download as CSV or PDF

## Features Checklist

✅ Modern web interface (replaced Tkinter)
✅ Named Entity Recognition integrated
✅ Optimized for Indian education data
✅ PDF download functionality
✅ CSV export
✅ Beautiful, responsive UI
✅ Groq API integration verified

## Troubleshooting

**API Key Error**: Make sure `.env` file exists with `GROQ_API_KEY=...`

**Port in use**: Change port in `app.py` line 313: `port=5001`

**PDF processing slow**: This is normal for large documents. The AI processing takes time.

**No results**: Check that your PDF contains text (not just images). OCR is not implemented yet.

---

**Ready for your hackathon!** 🚀



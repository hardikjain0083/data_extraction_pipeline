# Education Data Extraction Pipeline - India

An AI-powered data extraction pipeline specifically designed for processing Indian education documents. This application uses Groq AI and Named Entity Recognition (NER) to extract, structure, and analyze education-related data from PDF documents.

## Features

- 📄 **PDF Document Processing**: Upload and process PDF documents with advanced text extraction
- 🤖 **AI-Powered Extraction**: Uses Groq's Llama models for intelligent data extraction
- 🏷️ **Named Entity Recognition**: Automatically identifies organizations, locations, persons, dates, and education-specific entities
- 📊 **Structured Data Output**: Extracts summaries, statistics, tables, policies, and schemes
- 📥 **Multiple Export Formats**: Download results as CSV or PDF reports
- 🎨 **Modern Web Interface**: Beautiful, responsive UI built with Flask and modern CSS
- 🇮🇳 **India-Specific**: Optimized for Indian education system, states, policies, and statistics

## Technology Stack

- **Backend**: Flask (Python)
- **AI/ML**: Groq API (Llama 3.3 70B & Llama 3.2 Vision)
- **PDF Processing**: PyMuPDF, pymupdf4llm
- **Data Processing**: Pandas
- **PDF Generation**: ReportLab
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Groq API key ([Get one here](https://console.groq.com))

## Installation

### Step 1: Clone the Repository

```bash
git clone <your-repository-url>
cd edu
```

### Step 2: Create Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables

1. Create a `.env` file in the root directory (copy from `.env.example` if available)
2. Add your Groq API key:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```
3. **Important**: Never commit the `.env` file to Git (it's already in `.gitignore`)

### Step 5: Verify Installation

The application will automatically create `uploads/` and `outputs/` directories when you run it.

## Running the Application

### Option 1: Using Python Directly

```bash
python app.py
```

### Option 2: Using the Batch Script (Windows)

```bash
run.bat
```

### Option 3: Using the Shell Script (Linux/Mac)

```bash
chmod +x run.sh
./run.sh
```

### Access the Web Interface

1. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

2. **Upload a PDF document**:
   - Click "Select File" or drag and drop a PDF file
   - The application accepts PDF files up to 50MB

3. **Process the document**:
   - Click "Process Document" to start extraction
   - Wait for the processing to complete (this may take a minute or two)

4. **View and download results**:
   - Browse through different tabs (Summary, Entities, Statistics, Tables, Policies)
   - Download results as CSV or PDF report

## Pushing to GitHub

### Initial Setup

1. **Initialize Git repository** (if not already done):
   ```bash
   git init
   ```

2. **Add all files** (`.gitignore` will automatically exclude unnecessary files):
   ```bash
   git add .
   ```

3. **Create initial commit**:
   ```bash
   git commit -m "Initial commit: Education Data Extraction Pipeline"
   ```

4. **Add remote repository**:
   ```bash
   git remote add origin <your-github-repo-url>
   ```

5. **Push to GitHub**:
   ```bash
   git branch -M main
   git push -u origin main
   ```

### Important Notes for GitHub

- ✅ The `.gitignore` file will automatically exclude:
  - Installed packages (groq, pandas, numpy, etc.)
  - Virtual environment folders
  - Cache files (`__pycache__`, `.pyc` files)
  - Runtime folders (`uploads/`, `outputs/`, `extracted_images/`)
  - Environment files (`.env`)
  - OS-specific files

- ⚠️ **Never commit**:
  - Your `.env` file (contains API keys)
  - Virtual environment folder
  - Uploaded files or extracted images

- 📝 **Files that will be committed**:
  - Source code (`.py` files)
  - Templates and static files
  - `requirements.txt`
  - `README.md`
  - `.gitignore`
  - Configuration files

## Project Structure

```
edu/
├── app.py                 # Flask application
├── pipeline.py            # Main data extraction pipeline
├── ner_groq.py            # Named Entity Recognition processor
├── main.py               # Legacy Tkinter GUI (deprecated)
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variables template
├── templates/
│   └── index.html        # Main web interface
├── static/
│   ├── css/
│   │   └── style.css     # Styling
│   └── js/
│       └── main.js       # Frontend logic
├── uploads/              # Uploaded PDF files (auto-created)
└── outputs/              # Processed results (auto-created)
```

## Features in Detail

### Named Entity Recognition (NER)
- Extracts organizations (schools, universities, government bodies)
- Identifies locations (Indian states, cities, districts)
- Finds persons (officials, educators)
- Detects dates and education-related terms
- Categorizes policies and schemes

### Data Extraction
- **Summary**: Comprehensive document summary
- **Document Type**: Classification of document type
- **Education Levels**: Primary, Secondary, Higher Education, etc.
- **States Mentioned**: Indian states and union territories
- **Key Statistics**: Enrollment rates, literacy rates, dropout rates, etc.
- **Policies & Schemes**: Government policies and educational schemes
- **Tables**: Structured table data extraction
- **Budget Information**: Financial data if available

### Export Options
- **CSV Export**: Structured data in CSV format with multiple sections
- **PDF Report**: Professional PDF report with formatted tables and statistics

## API Endpoints

- `GET /` - Main application page
- `POST /upload` - Upload PDF file
- `POST /process` - Process uploaded file
- `GET /download/csv?session_id=<id>` - Download CSV
- `GET /download/pdf?session_id=<id>` - Download PDF report

## Configuration

The application can be configured in `app.py`:
- `UPLOAD_FOLDER`: Directory for uploaded files
- `OUTPUT_FOLDER`: Directory for processed results
- `MAX_CONTENT_LENGTH`: Maximum file size (default: 50MB)

## Troubleshooting

### Groq API Errors
- Ensure your API key is correctly set in the `.env` file
- Check your Groq API quota and rate limits
- Verify internet connectivity

### PDF Processing Issues
- Ensure PDF files are not corrupted
- Try with smaller PDF files first
- Check that PyMuPDF is properly installed

### Port Already in Use
- Change the port in `app.py`: `app.run(debug=True, host='0.0.0.0', port=5001)`

## Contributing

This is a hackathon project. Feel free to fork and improve!

## License

MIT License - feel free to use this project for your hackathon or educational purposes.

## Acknowledgments

- Groq for providing fast AI inference
- PyMuPDF for excellent PDF processing
- Flask community for the web framework

---

**Built for Hackathon** 🚀

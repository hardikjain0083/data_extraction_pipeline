import os
import sys
import argparse
import io
import shutil

# --- Python 3.14 Compatibility Fix ---
# pkgutil.find_loader was removed in Python 3.14.
# pytesseract relies on it, so we monkeypatch it with importlib.util.find_spec.
import pkgutil
import importlib.util

if not hasattr(pkgutil, 'find_loader'):
    def find_loader(fullname):
        spec = importlib.util.find_spec(fullname)
        return spec.loader if spec else None
    pkgutil.find_loader = find_loader

# Now we can safely import pytesseract and other libs
import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path, pdfinfo_from_path
from PIL import Image, ImageTk
from docx import Document

# --- Configuration ---
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# os.environ["PATH"] += os.pathsep + r'C:\poppler-xx\bin'

# Auto-detect Poppler in common installation directory (created by install_poppler.py)
poppler_install_dir = os.path.expanduser(r"~\AppData\Local\Programs\poppler")
if os.path.exists(poppler_install_dir):
    for root, dirs, files in os.walk(poppler_install_dir):
        if "pdftoppm.exe" in files:
            print(f"Adding local Poppler to PATH: {root}")
            os.environ["PATH"] += os.pathsep + root
            break



def check_dependencies():
    """Checks if Tesseract and Poppler are available."""
    missing = []
    
    # Check Tesseract
    try:
        pytesseract.get_tesseract_version()
        tesseract_status = "OK"
    except Exception:
        tesseract_status = "Missing (Install Tesseract-OCR)"
        missing.append("Tesseract-OCR")

    # Check Poppler
    try:
        # pdf2image uses 'pdftoppm' or 'pdftocairo' from poppler
        if not shutil.which("pdftoppm") and not shutil.which("pdftocairo"):
             poppler_status = "Missing (Install Poppler)"
             missing.append("Poppler")
        else:
             poppler_status = "OK"
    except Exception:
         poppler_status = "Error checking"

    return tesseract_status, poppler_status, missing


def extract_from_docx(file_path):
    """Extracts text from a .docx file."""
    try:
        doc = Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return '\n'.join(full_text)
    except Exception as e:
        return f"Error extracting from DOCX: {e}"


def extract_from_image(file_path):
    """Extracts text from an image using OCR."""
    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        return f"Error extracting from Image: {e}"


def is_digital_pdf(doc):
    """
    Heuristic to determine if a PDF is digital (selectable text) or scanned.
    """
    text_length = 0
    # Check up to first 3 pages
    for i in range(min(3, len(doc))):
        text_length += len(doc[i].get_text())
    
    if text_length > 50: 
        return True
    return False


def extract_from_pdf(file_path):
    """
    Extracts text from PDF. Determine if it's digital or scanned.
    """
    try:
        doc = fitz.open(file_path)
        
        if is_digital_pdf(doc):
            print("Detected Digital PDF. Using PyMuPDF...")
            text_content = []
            for page in doc:
                text_content.append(page.get_text())
            doc.close()
            return "\n".join(text_content)
        else:
            print("Detected Scanned PDF. Using OCR (pdf2image + pytesseract)...")
            doc.close()
            
            # Check poppler again here to be safe or catch error
            try:
                images = convert_from_path(file_path)
            except Exception as e:
                return f"Error converting PDF to image (Check Poppler): {e}"
            
            text_content = []
            for i, image in enumerate(images):
                print(f"Processing page {i+1}...")
                page_text = pytesseract.image_to_string(image)
                text_content.append(page_text)
            
            return "\n".join(text_content)
            
    except Exception as e:
        return f"Error extracting from PDF: {e}"


def save_output(text, output_path):
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Successfully saved output to {output_path}")
    except Exception as e:
        print(f"Error saving output: {e}")

# --- GUI ---
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox

class TextExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Universal Text Extractor")
        self.root.geometry("600x500")

        # Dependency Status
        t_status, p_status, missing = check_dependencies()
        
        status_frame = tk.LabelFrame(root, text="System Dependencies", padx=10, pady=10)
        status_frame.pack(fill="x", padx=10, pady=5)
        
        t_color = "green" if t_status == "OK" else "red"
        p_color = "green" if p_status == "OK" else "red"
        
        tk.Label(status_frame, text=f"Tesseract OCR: {t_status}", fg=t_color).pack(anchor="w")
        tk.Label(status_frame, text=f"Poppler: {p_status}", fg=p_color).pack(anchor="w")

        if missing:
             tk.Label(status_frame, text="Note: Install missing dependencies for OCR to work.", fg="orange").pack(anchor="w")

        # File Selection
        control_frame = tk.Frame(root, padx=10, pady=10)
        control_frame.pack(fill="x")

        self.btn_select = tk.Button(control_frame, text="Select File & Extract", command=self.process_file, height=2, bg="#ddd")
        self.btn_select.pack(fill="x")
        
        self.lbl_file = tk.Label(control_frame, text="No file selected", wraplength=500)
        self.lbl_file.pack(pady=5)

        # Output Area
        self.txt_output = scrolledtext.ScrolledText(root, wrap=tk.WORD)
        self.txt_output.pack(fill="both", expand=True, padx=10, pady=10)

    def process_file(self):
        file_path = filedialog.askopenfilename(filetypes=[
            ("All Supported", "*.pdf *.docx *.png *.jpg *.jpeg *.tiff *.bmp"),
            ("PDF Files", "*.pdf"),
            ("Word Documents", "*.docx"),
            ("Images", "*.png *.jpg *.jpeg *.tiff *.bmp")
        ])
        
        if not file_path:
            return

        self.lbl_file.config(text=f"Selected: {file_path}")
        self.txt_output.delete(1.0, tk.END)
        self.txt_output.insert(tk.END, "Processing...\n")
        self.root.update()

        ext = os.path.splitext(file_path)[1].lower()
        extracted_text = ""

        if ext == '.docx':
            extracted_text = extract_from_docx(file_path)
        elif ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
            extracted_text = extract_from_image(file_path)
        elif ext == '.pdf':
            extracted_text = extract_from_pdf(file_path)
        else:
            extracted_text = f"Unsupported file format: {ext}"

        self.txt_output.delete(1.0, tk.END)
        self.txt_output.insert(tk.END, extracted_text)

def main():
    # If command line args are present, run CLI mode
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description="Universal Text Extractor")
        parser.add_argument("input_file", help="Path to the input file")
        parser.add_argument("--output", "-o", help="Path to save output")
        args = parser.parse_args()
        
        file_path = args.input_file
        if not os.path.exists(file_path):
            print(f"Error: Not found {file_path}")
            sys.exit(1)
            
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.docx':
            txt = extract_from_docx(file_path)
        elif ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
            txt = extract_from_image(file_path)
        elif ext == '.pdf':
            txt = extract_from_pdf(file_path)
        else:
            print("Unsupported format")
            sys.exit(1)
            
        if args.output:
            save_output(txt, args.output)
        else:
            print(txt)
    else:
        # GUI Mode
        root = tk.Tk()
        app = TextExtractorApp(root)
        root.mainloop()

if __name__ == "__main__":
    main()

import os
import requests
import json
import time
import csv
from dotenv import load_dotenv
from PyPDF2 import PdfReader

# Load API key from .env
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env file!")

BASE_URL = "https://api.groq.com/v1/predict"  # Groq API endpoint

# ----------- Utilities -----------

def download_file(url, local_path="downloaded_file"):
    response = requests.get(url)
    response.raise_for_status()
    with open(local_path, "wb") as f:
        f.write(response.content)
    return local_path

def extract_text(file_path):
    if file_path.lower().endswith(".pdf"):
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    elif file_path.lower().endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        raise ValueError("Unsupported file type! Use PDF or TXT.")

def chunk_text(text, max_chars=1000):
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        chunks.append(text[start:end])
        start = end
    return chunks

def extract_entities_chunk(chunk):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    prompt = f"""
Extract named entities from the following text.
Output JSON with objects having "text" and "label".

Text:
{chunk}
"""
    body = {"model": "openai/gpt-oss-20b", "input": prompt}
    
    while True:
        response = requests.post(BASE_URL, headers=headers, json=body)
        if response.status_code == 429:  # Rate limit hit
            wait_time = 5
            try:
                msg = response.json().get("error", {}).get("message", "")
                if "in" in msg:
                    wait_time = float(msg.split("in ")[-1].split("s")[0]) + 1
            except:
                pass
            print(f"Rate limit hit, sleeping {wait_time:.1f}s...")
            time.sleep(wait_time)
            continue
        elif response.status_code != 200:
            raise RuntimeError(f"NER call failed {response.status_code}: {response.text}")
        break

    output_text = response.json().get("output_text", "")
    try:
        return json.loads(output_text)
    except Exception:
        return []

def extract_entities(text):
    all_entities = []
    chunks = chunk_text(text)
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1}/{len(chunks)}...")
        chunk_entities = extract_entities_chunk(chunk)
        all_entities.extend(chunk_entities)
    return all_entities

def save_to_csv(entities, output_file):
    if not entities:
        print(f"No entities found for {output_file}")
        return
    keys = entities[0].keys()
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(entities)
    print(f"✅ Entities saved to {output_file}")

# ----------- Main -----------

def process_file(file_input):
    # Download if URL
    if file_input.startswith("http://") or file_input.startswith("https://"):
        print(f"Downloading {file_input} ...")
        file_path = download_file(file_input, "downloaded_file")
        if not os.path.splitext(file_path)[1]:
            file_path += ".pdf"  # default
    else:
        file_path = file_input
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return

    print(f"Extracting text from {file_path}...")
    text = extract_text(file_path)
    print("Extracting named entities...")
    entities = extract_entities(text)
    
    output_csv = os.path.splitext(os.path.basename(file_path))[0] + "_ner.csv"
    save_to_csv(entities, output_csv)

def main():
    input_files = input("Enter PDF/TXT file paths or folder path (comma separated for multiple files): ").strip()
    
    # Check if folder
    if os.path.isdir(input_files):
        files = [os.path.join(input_files, f) for f in os.listdir(input_files) 
                 if f.lower().endswith((".pdf", ".txt"))]
    else:
        # Split comma separated files
        files = [f.strip() for f in input_files.split(",")]
    
    for file_path in files:
        try:
            process_file(file_path)
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")

if __name__ == "__main__":
    main()
=======
from groq import GroqClient

# 1️⃣ Set your Groq API key
api_key = "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"
os.environ["GROQ_API_KEY"] = api_key

# 2️⃣ Initialize Groq client
client = GroqClient(api_key=api_key)

# 3️⃣ Text to analyze
text = "Apple is planning to open a new office in Bangalore next year."

# 4️⃣ Run NER
response = client.analyze(text, task="ner")

# 5️⃣ Print detected entities
print("Detected entities:")
for entity in response["entities"]:
    print(f"- {entity['text']} ({entity['label']})")
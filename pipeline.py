import json
import base64
import sys
import os

from typing import List, Dict, Optional
try:
    import pymupdf4llm
    HAS_PYMUPDF4LLM = True
except ImportError:
    HAS_PYMUPDF4LLM = False
    print("Warning: pymupdf4llm not found. Using simple text extraction.")

from groq import Groq
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import pandas as pd
import fitz  # PyMuPDF
from ner_groq import NERProcessor

# Load environment variables
load_dotenv()

class DocumentIngestor:
    """Handles loading and converting documents."""
    
    @staticmethod
    def to_markdown(file_path: str) -> str:
        """Converts PDF to Markdown, preserving layout and tables."""
        print(f"Converting {file_path} to Markdown...")
        try:
            if HAS_PYMUPDF4LLM:
                # pymupdf4llm is excellent at preserving table structure in markdown
                md_text = pymupdf4llm.to_markdown(file_path)
                return md_text
            else:
                # Fallback to standard text extraction
                doc = fitz.open(file_path)
                text = ""
                for page in doc:
                    text += page.get_text() + "\n\n"
                return text
        except Exception as e:
            print(f"Error converting to Markdown: {e}")
            return ""

    @staticmethod
    def extract_images(file_path: str, output_dir: str = "extracted_images") -> List[str]:
        """Extracts images from PDF for vision processing."""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        image_paths = []
        doc = fitz.open(file_path)
        
        for i, page in enumerate(doc):
            image_list = page.get_images(full=True)
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                image_filename = f"{output_dir}/page_{i+1}_img_{img_index}.{image_ext}"
                
                with open(image_filename, "wb") as f:
                    f.write(image_bytes)
                
                image_paths.append(image_filename)
                
        return image_paths

class GroqProcessor:
    """Handles interaction with Groq API for Text and Vision."""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment!")
        self.client = Groq(api_key=self.api_key)
        self.text_model = "llama-3.3-70b-versatile"
        self.vision_model = "llama-3.2-11b-vision-preview"

    def analyze_image(self, image_path: str) -> str:
        """Uses Llama 3.2 Vision to describe a chart or image."""
        print(f"Analyzing image: {image_path}")
        
        # Encode image
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Describe this image in detail. If it is a chart or table, output the data in textual format."},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{encoded_string}",
                                },
                            },
                        ],
                    }
                ],
                model=self.vision_model,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(f"Vision API Error: {e}")
            return ""

    def structurize_text(self, text: str, schema_description: str) -> dict:
        """Extracts structured data from text using JSON mode."""
        
        prompt = f"""
        Extract the following information from the text provided below.
        Return the result as a strictly valid JSON object.
        
        Schema Description:
        {schema_description}

        Text:
        {text[:15000]} # Truncate to be safe with context limits
        """
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.text_model,
                response_format={"type": "json_object"},
            )
            return json.loads(chat_completion.choices[0].message.content)
        except Exception as e:
            print(f"Structure API Error: {e}")
            return {}

class Pipeline:
    def __init__(self):
        self.ingestor = DocumentIngestor()
        self.processor = GroqProcessor()
        self.ner_processor = NERProcessor()

    def run(self, input_file: str, save_json: bool = True) -> dict:
        print(f"--- Starting Pipeline for {input_file} ---")
        
        # 1. Convert to Markdown (Layout preservation)
        md_content = self.ingestor.to_markdown(input_file)
        
        # 2. Extract and Analyze Images (Vision)
        image_paths = self.ingestor.extract_images(input_file)
        image_summaries = []
        for img_path in image_paths:
            summary = self.processor.analyze_image(img_path)
            image_summaries.append(f"Image ({img_path}): {summary}")
        
        # 3. Combine Context
        full_context = md_content + "\n\n" + "\n".join(image_summaries)
        
        # 4. Perform Named Entity Recognition
        print("Extracting named entities...")
        ner_entities = self.ner_processor.extract_entities(full_context)
        
        # 5. Structure Data - Optimized for Indian Education Data
        schema = """
        {
            "summary": "Comprehensive summary of the education document focusing on Indian education system, policies, statistics, or reports",
            "document_type": "Type of document (e.g., Policy Document, Statistical Report, Research Paper, Government Circular)",
            "education_levels": ["List of education levels mentioned (e.g., Primary, Secondary, Higher Education, Vocational)"],
            "states_mentioned": ["List of Indian states/UTs mentioned in the document"],
            "organizations": ["List of educational institutions, government bodies, NGOs mentioned"],
            "key_statistics": [
                {
                    "metric": "Name of the statistic (e.g., Enrollment Rate, Literacy Rate, Dropout Rate)",
                    "value": "Numerical value or percentage",
                    "context": "Additional context about the statistic"
                }
            ],
            "policies_schemes": [
                {
                    "name": "Name of policy or scheme",
                    "description": "Brief description",
                    "target_audience": "Who it targets"
                }
            ],
            "tables": [
                {
                    "title": "Title of the table or chart",
                    "data": [
                        { "column_1": "value", "column_2": "value" }
                    ]
                }
            ],
            "key_dates": ["Important dates mentioned in the document"],
            "budget_financials": {
                "total_budget": "Total budget amount if mentioned",
                "currency": "Currency (usually INR)",
                "breakdown": "Breakdown of budget allocation if available"
            }
        }
        """
        
        print("Structuring data for Indian education context...")
        result = self.processor.structurize_text(full_context, schema)
        
        # 6. Integrate NER results
        if ner_entities:
            result["named_entities"] = ner_entities
            # Categorize entities
            result["entities_by_type"] = self._categorize_entities(ner_entities)
        
        # 7. Save Output (Optional)
        if save_json:
            output_file = os.path.splitext(input_file)[0] + "_output.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=4, ensure_ascii=False)
            print(f"Pipeline complete. Output saved to {output_file}")
            
        return result
    
    def _categorize_entities(self, entities: List[Dict]) -> Dict[str, List[str]]:
        """Categorize entities by type for better organization."""
        categorized = {
            "organizations": [],
            "locations": [],
            "persons": [],
            "dates": [],
            "other": []
        }
        
        for entity in entities:
            label = entity.get("label", "").lower()
            text = entity.get("text", "")
            
            if any(keyword in label for keyword in ["org", "organization", "institution", "company"]):
                categorized["organizations"].append(text)
            elif any(keyword in label for keyword in ["loc", "location", "place", "state", "city", "country"]):
                categorized["locations"].append(text)
            elif any(keyword in label for keyword in ["person", "per", "name"]):
                categorized["persons"].append(text)
            elif any(keyword in label for keyword in ["date", "time"]):
                categorized["dates"].append(text)
            else:
                categorized["other"].append(text)
        
        return categorized

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AI Data Extraction Pipeline")
    parser.add_argument("input_file", help="Path to PDF file")
    args = parser.parse_args()
    
    if os.path.exists(args.input_file):
        pipeline = Pipeline()
        pipeline.run(args.input_file)
    else:
        print("File not found.")

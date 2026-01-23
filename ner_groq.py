import os
import json
import csv
from dotenv import load_dotenv
from groq import Groq

# Load API key
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    print("WARNING: GROQ_API_KEY not found in .env file. Please set it.")

class NERProcessor:
    def __init__(self, api_key=None):
        self.client = Groq(api_key=api_key or API_KEY)
        self.model = "llama-3.1-70b-versatile" # Good balance of speed and smarts

    def extract_entities(self, text):
        prompt = f"""
        Extract named entities from the following text, focusing on Indian education context.
        Identify: Organizations (schools, universities, government bodies), Locations (states, cities, districts),
        Persons (officials, educators), Dates, Policies/Schemes, and Education-related terms.
        
        Return a JSON object with an "entities" key containing an array of objects.
        Each object should have "text" (the entity text) and "label" (the entity type).
        
        Entity types should be: ORGANIZATION, LOCATION, PERSON, DATE, POLICY_SCHEME, EDUCATION_TERM, or OTHER.
        
        Text:
        {text[:8000]} 
        """

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.model,
                response_format={"type": "json_object"}, 
            )
            
            content = chat_completion.choices[0].message.content
            # Ensure it's parsed as JSON
            data = json.loads(content)
            # Handle cases where the model wraps it in a key like "entities"
            if isinstance(data, dict):
               if "entities" in data:
                   return data["entities"]
               # If it's just a dict, maybe the model misunderstood, or it's a single object
               return [data] if data else []
            return data if isinstance(data, list) else []

        except Exception as e:
            print(f"Error calling Groq API: {e}")
            return []

    def save_to_csv(self, entities, output_file):
        if not entities:
            print("No entities to save.")
            return

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["text", "label"])
            writer.writeheader()
            for entity in entities:
                # Ensure we only write the known keys
                row = {k: entity.get(k, "") for k in ["text", "label"]}
                writer.writerow(row)
        print(f"Saved to {output_file}")

if __name__ == "__main__":
    # Example Usage
    text_input = "Apple is planning to open a new office in Bangalore next year. Tim Cook announced this yesterday."
    processor = NERProcessor()
    entities = processor.extract_entities(text_input)
    print("Extracted Entities:", entities)
    processor.save_to_csv(entities, "test_ner.csv")
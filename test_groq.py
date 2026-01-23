"""
Test script to verify Groq API integration
"""
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

def test_groq_api():
    """Test if Groq API is working correctly"""
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        print("❌ ERROR: GROQ_API_KEY not found in environment variables!")
        print("Please create a .env file with: GROQ_API_KEY=your_key_here")
        return False
    
    try:
        client = Groq(api_key=api_key)
        
        # Test text model
        print("Testing Groq API connection...")
        print("Model: llama-3.3-70b-versatile")
        
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Say 'API is working' if you can read this."
                }
            ],
            model="llama-3.3-70b-versatile",
        )
        
        result = response.choices[0].message.content
        print(f"✅ API Response: {result}")
        print("✅ Groq API is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("Please check your API key and internet connection.")
        return False

if __name__ == "__main__":
    test_groq_api()



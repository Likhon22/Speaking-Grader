
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

def test_connection():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ API Key not found!")
        return

    client = genai.Client(api_key=api_key)
    model_name = "gemini-2.5-flash"
    
    print(f"Testing model: {model_name}...")
    
    try:
        response = client.models.generate_content(
            model=model_name,
            contents="Say 'Hello, I am working!' if you can hear me."
        )
        print("\n✅ SUCCESS!")
        print(f"Response: {response.text}")
    except Exception as e:
        print("\n❌ FAILED")
        print(f"Error: {e}")

if __name__ == "__main__":
    test_connection()

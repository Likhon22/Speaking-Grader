
import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

def burst_test():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ API Key not found!")
        return

    client = genai.Client(api_key=api_key)
    model_name = "gemini-2.5-flash" # Using your requested premium model
    
    print(f"🚀 Starting Burst Test for: {model_name}")
    print("Sending 20 rapid requests to check rate limits...")
    print("(Free tier limit is usually 15 RPM for Flash models)")
    
    success_count = 0
    fail_count = 0
    
    for i in range(25):
        try:
            client.models.generate_content(
                model=model_name,
                contents="ping"
            )
            success_count += 1
            print(f"Request {i+1}: ✅ OK", end="\r")
        except Exception as e:
            fail_count += 1
            print(f"Request {i+1}: ❌ ERROR: {e}")
            if "429" in str(e) or "Resource has been exhausted" in str(e):
                print("\n⚠️  THROTTLED! This looks like a FREE TIER key (15 requests/min limit reached).")
                return
        time.sleep(0.1) # Very fast

    print(f"\n\n💎 TOTAL SUCCESS: {success_count}/25")
    if success_count > 15:
        print("🏆 VERIFIED: This is likely a PAID/PREMIUM key because it passed the 15 RPM limit!")
    else:
        print("❓ Result is inconclusive. Try again if you are sure it's paid.")

if __name__ == "__main__":
    burst_test()

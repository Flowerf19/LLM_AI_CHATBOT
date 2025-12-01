import os
import sys
import google.generativeai as genai
from dotenv import load_dotenv

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("❌ Error: GEMINI_API_KEY not found in .env")
    sys.exit(1)

genai.configure(api_key=api_key)

print("🔍 Checking available Gemini models for your API Key...")
try:
    print(f"{'Model Name':<30} | {'Supported Methods'}")
    print("-" * 60)
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"{m.name:<30} | {m.supported_generation_methods}")
except Exception as e:
    print(f"❌ Error listing models: {e}")

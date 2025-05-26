#!/usr/bin/env python3
# LLM Provider PoC for Metadata Code Extractor - OpenRouter
import os
from dotenv import load_dotenv
import requests
import json
import sys

# Load environment variables
load_dotenv()

# Configuration for OpenRouter
API_KEY = os.getenv("OPENROUTER_API_KEY")
API_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4")  # Default to GPT-4 via OpenRouter
SITE_URL = os.getenv("OPENROUTER_SITE_URL", "https://github.com/metadata-code-extractor")
APP_NAME = os.getenv("OPENROUTER_APP_NAME", "metadata-code-extractor")

# Simple Python code to analyze
sample_code = """
class User:
    \"\"\"Represents a user in the system.\"\"\"
    
    def __init__(self, user_id: str, name: str, email: str = None):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.is_active = True
    
    def deactivate(self):
        \"\"\"Deactivate this user account.\"\"\"
        self.is_active = False
        return self.is_active
"""

# Basic extraction prompt
prompt = f"""
You are a code analyzer. Extract metadata from this Python code:

{sample_code}

Return a JSON object with:
1. Class name
2. Class description
3. Fields with types and descriptions
4. Methods with descriptions

Format as valid JSON only.
"""

def run_poc():
    # Check for API key
    if not API_KEY:
        print("Error: OPENROUTER_API_KEY environment variable not set.")
        print("Please set it in .env file or environment.")
        return False
        
    # API request headers for OpenRouter
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
        "HTTP-Referer": SITE_URL,  # Required by OpenRouter
        "X-Title": APP_NAME  # Required by OpenRouter
    }

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "response_format": {"type": "json_object"}
    }

    # Make request
    try:
        print(f"Connecting to OpenRouter API using {MODEL}...")
        response = requests.post(API_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()
        
        # Parse response
        result = response.json()
        extracted_data = json.loads(result["choices"][0]["message"]["content"])
        
        print("\n✅ API Connection Successful!")
        print(f"✅ Model used: {MODEL}")
        print("✅ Extracted Metadata:")
        print(json.dumps(extracted_data, indent=2))
        
        # Validate basic structure
        assert "class_name" in extracted_data, "Missing class name"
        assert "fields" in extracted_data, "Missing fields"
        
        print("\n✅ Validation successful - required fields present")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = run_poc()
    sys.exit(0 if success else 1) 
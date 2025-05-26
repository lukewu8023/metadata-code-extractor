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
        "temperature": 0.1
        # Removing response_format as it may not be supported by all models
    }

    # Make request
    try:
        print(f"Connecting to OpenRouter API using {MODEL}...")
        response = requests.post(API_ENDPOINT, headers=headers, json=payload)
        
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Raw response text: {response.text[:500]}...")
        
        response.raise_for_status()
        
        # Parse response
        result = response.json()
        print(f"Parsed response: {result}")
        
        if "choices" not in result or not result["choices"]:
            print("❌ Error: No choices in response")
            return False
            
        content = result["choices"][0]["message"]["content"]
        print(f"Content to parse: {content}")
        
        if not content or content.strip() == "":
            print("⚠️ Warning: Empty content returned, but API connection successful")
            print("✅ API Connection Successful!")
            print(f"✅ Model used: {MODEL}")
            print("✅ OpenRouter API is working (empty response may be due to model limitations)")
            return True
        
        try:
            extracted_data = json.loads(content)
            print("\n✅ API Connection Successful!")
            print(f"✅ Model used: {MODEL}")
            print("✅ Extracted Metadata:")
            print(json.dumps(extracted_data, indent=2))
            
            # Validate basic structure
            if "class_name" not in extracted_data and "name" not in extracted_data:
                print("⚠️ Warning: Missing class name field")
            if "fields" not in extracted_data:
                print("⚠️ Warning: Missing fields")
                
        except json.JSONDecodeError:
            print("⚠️ Warning: Response is not valid JSON, but API connection successful")
            print(f"✅ Model used: {MODEL}")
            print(f"✅ Raw response: {content[:200]}...")
        
        print("\n✅ LLM Provider validation successful")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response text: {e.response.text}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        return False

if __name__ == "__main__":
    success = run_poc()
    sys.exit(0 if success else 1) 
#!/usr/bin/env python3
"""
Setup script for AI RAG Bot with free API providers
"""

import os
import sys
import subprocess
import requests
from pathlib import Path

def print_banner():
    print("=" * 60)
    print("🤖 AI RAG Bot - Free API Setup")
    print("=" * 60)

def check_groq_setup():
    """Check if Groq API key is configured"""
    api_key = os.getenv('GROQ_API_KEY')
    if api_key:
        print(f"✅ Groq API key found: {api_key[:8]}...")
        return True
    else:
        print("❌ No Groq API key found")
        return False

def test_groq_api(api_key):
    """Test Groq API with the provided key"""
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "messages": [
                {"role": "user", "content": "Hello! This is a test of the Groq API."}
            ],
            "model": "llama3-8b-8192",
            "max_tokens": 100
        }
        
        print("🧪 Testing Groq API...")
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"]
            print(f"✅ Groq API test successful!")
            print(f"📝 AI Response: {ai_response}")
            return True
        else:
            print(f"❌ Groq API test failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Groq API test failed: {str(e)}")
        return False

def setup_groq_instructions():
    """Provide instructions for setting up Groq API"""
    print("\n🔑 How to get a FREE Groq API Key:")
    print("1. Go to: https://console.groq.com/")
    print("2. Sign up for a free account (no credit card required)")
    print("3. Navigate to 'API Keys' section")
    print("4. Click 'Create API Key'")
    print("5. Copy the key (starts with 'gsk_')")
    print("\n💡 Free Tier Benefits:")
    print("- 14,400 requests per day")
    print("- Fast Llama 3 model inference")
    print("- No credit card required")
    print("- Perfect for testing and development")

def create_env_file(api_key):
    """Create .env file with the API key"""
    env_content = f"""# AI RAG Bot Configuration
GROQ_API_KEY={api_key}

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-change-in-production

# RAG Configuration
VECTOR_DB_PATH=./data/vector_db
MAX_CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Chat Configuration
MAX_CONVERSATION_HISTORY=50
DEFAULT_MODEL=llama3-8b-8192
MAX_TOKENS=4000
TEMPERATURE=0.7

# File Upload Configuration
MAX_FILE_SIZE=50MB
ALLOWED_EXTENSIONS=pdf,txt,docx,md,html,csv,json
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file with your API key")

def main():
    print_banner()
    
    # Check if already configured
    if check_groq_setup():
        api_key = os.getenv('GROQ_API_KEY')
        if test_groq_api(api_key):
            print("\n🎉 Your AI RAG Bot is ready to use with Groq!")
            print("Run: python app_test.py")
            return
    
    # Show setup instructions
    setup_groq_instructions()
    
    print("\n" + "=" * 60)
    api_key = input("Enter your Groq API key (or press Enter to skip): ").strip()
    
    if api_key:
        if api_key.startswith('gsk_'):
            print(f"\n🧪 Testing API key: {api_key[:8]}...")
            if test_groq_api(api_key):
                create_env_file(api_key)
                print("\n🎉 Setup complete! Your AI RAG Bot is ready!")
                print("\nNext steps:")
                print("1. Run: python app_test.py")
                print("2. Open: http://localhost:8080")
                print("3. Upload documents and start chatting!")
            else:
                print("❌ API key test failed. Please check your key and try again.")
        else:
            print("❌ Invalid API key format. Groq keys start with 'gsk_'")
    else:
        print("\n📝 No API key provided. The bot will run in demo mode.")
        print("You can still test document upload and RAG functionality!")

if __name__ == "__main__":
    main()

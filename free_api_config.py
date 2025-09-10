import os
from typing import Optional, Dict, Any
import requests
import json

class FreeAPIProvider:
    """Manages free API providers for testing"""
    
    def __init__(self):
        self.providers = {
            "groq": {
                "base_url": "https://api.groq.com/openai/v1",
                "model": "llama3-8b-8192",
                "free_tier": True,
                "api_key_required": True
            },
            "ollama": {
                "base_url": "http://localhost:11434/api",
                "model": "llama2",
                "free_tier": True,
                "api_key_required": False
            },
            "huggingface": {
                "base_url": "https://api-inference.huggingface.co/models",
                "model": "microsoft/DialoGPT-medium",
                "free_tier": True,
                "api_key_required": True
            }
        }
    
    def test_groq_api(self, api_key: str) -> Dict[str, Any]:
        """Test Groq API with free tier"""
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "messages": [
                    {"role": "user", "content": "Hello, this is a test message."}
                ],
                "model": "llama3-8b-8192",
                "max_tokens": 100
            }
            
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "provider": "groq",
                    "response": result["choices"][0]["message"]["content"],
                    "model": "llama3-8b-8192"
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "provider": "groq"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "provider": "groq"
            }
    
    def test_ollama_local(self) -> Dict[str, Any]:
        """Test local Ollama installation"""
        try:
            # Check if Ollama is running
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            
            if response.status_code == 200:
                models = response.json().get("models", [])
                if models:
                    # Test with first available model
                    model_name = models[0]["name"]
                    
                    test_data = {
                        "model": model_name,
                        "prompt": "Hello, this is a test message.",
                        "stream": False
                    }
                    
                    test_response = requests.post(
                        "http://localhost:11434/api/generate",
                        json=test_data,
                        timeout=30
                    )
                    
                    if test_response.status_code == 200:
                        result = test_response.json()
                        return {
                            "success": True,
                            "provider": "ollama",
                            "response": result.get("response", ""),
                            "model": model_name,
                            "available_models": [m["name"] for m in models]
                        }
                
                return {
                    "success": False,
                    "error": "No models available in Ollama",
                    "provider": "ollama"
                }
            else:
                return {
                    "success": False,
                    "error": "Ollama not responding",
                    "provider": "ollama"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Ollama not available: {str(e)}",
                "provider": "ollama"
            }
    
    def get_free_groq_key_instructions(self) -> str:
        """Instructions for getting free Groq API key"""
        return """
🔑 Get Free Groq API Key:

1. Go to https://console.groq.com/
2. Sign up for a free account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (starts with 'gsk_')

Free Tier Limits:
- 14,400 requests per day
- Fast inference with Llama models
- No credit card required
"""
    
    def get_ollama_setup_instructions(self) -> str:
        """Instructions for setting up Ollama locally"""
        return """
🦙 Setup Ollama (100% Free Local AI):

1. Download Ollama from https://ollama.ai/
2. Install and start Ollama
3. Pull a model: `ollama pull llama2`
4. Verify: `ollama list`

Available Free Models:
- llama2 (7B) - Good general purpose
- codellama (7B) - Code generation
- mistral (7B) - Fast and efficient
- phi (2.7B) - Lightweight option

No API key needed - runs completely offline!
"""

def test_all_free_providers() -> Dict[str, Any]:
    """Test all available free providers"""
    provider = FreeAPIProvider()
    results = {}
    
    # Test Ollama (local)
    print("Testing Ollama (local)...")
    results["ollama"] = provider.test_ollama_local()
    
    # Test Groq (if API key available)
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        print("Testing Groq API...")
        results["groq"] = provider.test_groq_api(groq_key)
    else:
        results["groq"] = {
            "success": False,
            "error": "No GROQ_API_KEY found in environment",
            "provider": "groq",
            "instructions": provider.get_free_groq_key_instructions()
        }
    
    return results

if __name__ == "__main__":
    print("🧪 Testing Free AI Providers...")
    print("=" * 50)
    
    results = test_all_free_providers()
    
    for provider, result in results.items():
        print(f"\n{provider.upper()}:")
        if result["success"]:
            print(f"✅ Success! Model: {result.get('model', 'N/A')}")
            print(f"Response: {result.get('response', '')[:100]}...")
        else:
            print(f"❌ Failed: {result['error']}")
            if "instructions" in result:
                print(result["instructions"])
    
    print("\n" + "=" * 50)
    print("🎯 Recommendation:")
    
    if results["ollama"]["success"]:
        print("✅ Use Ollama - it's working and completely free!")
    elif results["groq"]["success"]:
        print("✅ Use Groq - fast and has generous free tier!")
    else:
        print("📝 Set up Ollama or get a free Groq API key to test the bot.")

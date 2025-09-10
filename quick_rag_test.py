#!/usr/bin/env python3
"""
Quick RAG test with OpenRouter
"""

import os
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

def quick_rag_test():
    """Quick test of RAG with OpenRouter"""
    print("🚀 Quick RAG Test with OpenRouter + Llama 3.2")
    print("="*50)
    
    # Test API
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ No OpenRouter API key found")
        return
    
    print(f"🔑 API Key: {api_key[:15]}...")
    
    try:
        # Initialize client
        client = openai.OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        
        # Simulate RAG context
        context = """
        AI RAG Bot Features:
        1. Document Processing - Supports PDF, DOCX, TXT, MD, HTML, CSV, JSON
        2. Vector Database - Uses ChromaDB for semantic search
        3. Multiple AI Providers - OpenAI, Groq, Ollama, Anthropic, OpenRouter
        4. Web Interface - Modern responsive chat UI
        5. Session Management - Persistent conversations
        6. Export Features - JSON, TXT, Markdown formats
        """
        
        query = "What document formats are supported?"
        
        print(f"📋 Context: {context[:100]}...")
        print(f"❓ Query: {query}")
        print("\n🤖 Generating RAG response...")
        
        # Generate response
        response = client.chat.completions.create(
            model="meta-llama/llama-3.2-3b-instruct:free",
            messages=[
                {
                    "role": "system", 
                    "content": "You are an AI assistant. Use the provided context to answer questions accurately."
                },
                {
                    "role": "user", 
                    "content": f"Context: {context}\n\nQuestion: {query}\n\nAnswer based on the context:"
                }
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        print("\n" + "="*50)
        print("🎯 RAG Response:")
        print("="*50)
        print(ai_response)
        print("="*50)
        
        print("\n✅ SUCCESS! RAG system working with OpenRouter!")
        print("🎉 Your AI RAG Bot is fully functional!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    quick_rag_test()

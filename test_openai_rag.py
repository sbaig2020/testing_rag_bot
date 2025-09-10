#!/usr/bin/env python3
"""
Direct test of OpenAI API with RAG system
"""

import os
import sys
import json
from dotenv import load_dotenv
import openai
from vector_store import VectorStore
from document_processor import DocumentProcessor

# Load environment variables
load_dotenv()

def test_openai_api():
    """Test OpenAI API connection"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ No OpenAI API key found in .env file")
        return False
    
    print(f"🔑 Testing OpenAI API key: {api_key[:8]}...")
    
    try:
        # Initialize OpenAI client
        client = openai.OpenAI(api_key=api_key)
        
        # Test API call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Hello! This is a test of the OpenAI API."}
            ],
            max_tokens=100
        )
        
        ai_response = response.choices[0].message.content
        print(f"✅ OpenAI API test successful!")
        print(f"📝 AI Response: {ai_response}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API test failed: {str(e)}")
        return False

def test_rag_with_openai():
    """Test RAG system with OpenAI"""
    print("\n" + "="*60)
    print("🧠 Testing RAG System with OpenAI")
    print("="*60)
    
    # Initialize components
    vector_store = VectorStore()
    doc_processor = DocumentProcessor()
    
    # Create test document
    test_content = """
    AI RAG Bot Features:
    1. Document Processing - Supports PDF, DOCX, TXT, MD, HTML, CSV, JSON
    2. Vector Database - Uses ChromaDB for semantic search
    3. Multiple AI Providers - OpenAI, Groq, Ollama, Anthropic
    4. Web Interface - Modern responsive chat UI
    5. Session Management - Persistent conversations
    6. Export Features - JSON, TXT, Markdown formats
    7. Real-time Chat - WebSocket support
    8. File Upload - Drag and drop interface
    """
    
    # Process document
    print("📄 Processing test document...")
    chunks = doc_processor.process_text(test_content, "test_rag_features.txt")
    vector_store.add_documents(chunks, ["test_rag_features.txt"] * len(chunks))
    print(f"✅ Created {len(chunks)} chunks")
    
    # Test query
    query = "What are the main features of this AI RAG system?"
    print(f"\n❓ Query: {query}")
    
    # Retrieve context
    print("🔍 Retrieving relevant context...")
    results = vector_store.search(query, k=3)
    
    if not results:
        print("❌ No context retrieved")
        return False
    
    context = "\n".join([doc["content"] for doc in results])
    print(f"📋 Retrieved {len(results)} relevant chunks")
    
    # Generate AI response with context
    print("🤖 Generating AI response with RAG context...")
    
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        client = openai.OpenAI(api_key=api_key)
        
        system_prompt = """You are an AI assistant with access to a knowledge base. 
        Use the provided context to answer questions accurately and comprehensively.
        If the context doesn't contain relevant information, say so clearly."""
        
        user_prompt = f"""Context from knowledge base:
{context}

Question: {query}

Please provide a detailed answer based on the context above."""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        print("\n" + "="*60)
        print("🎉 RAG + OpenAI Response:")
        print("="*60)
        print(ai_response)
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"❌ RAG + OpenAI test failed: {str(e)}")
        return False

def main():
    print("🤖 AI RAG Bot - OpenAI Integration Test")
    print("="*60)
    
    # Test OpenAI API
    if not test_openai_api():
        print("\n❌ OpenAI API test failed. Please check your API key.")
        return
    
    # Test RAG with OpenAI
    if test_rag_with_openai():
        print("\n🎉 All tests passed! Your AI RAG Bot is working with OpenAI!")
        print("\nNext steps:")
        print("1. The RAG system is fully functional")
        print("2. OpenAI integration is working")
        print("3. You can now use the web interface or API")
    else:
        print("\n❌ RAG test failed. Please check the logs above.")

if __name__ == "__main__":
    main()

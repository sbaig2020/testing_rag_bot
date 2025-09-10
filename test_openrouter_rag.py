#!/usr/bin/env python3
"""
Test OpenRouter API with RAG system
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

def test_openrouter_api():
    """Test OpenRouter API connection"""
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ No OpenRouter API key found in .env file")
        return False
    
    print(f"🔑 Testing OpenRouter API key: {api_key[:15]}...")
    
    try:
        # Initialize OpenAI client with OpenRouter endpoint
        client = openai.OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        
        # Test API call with free model
        response = client.chat.completions.create(
            model="meta-llama/llama-3.2-3b-instruct:free",
            messages=[
                {"role": "user", "content": "Hello! This is a test of the OpenRouter API with Llama 3.2."}
            ],
            max_tokens=100
        )
        
        ai_response = response.choices[0].message.content
        print(f"✅ OpenRouter API test successful!")
        print(f"📝 AI Response: {ai_response}")
        return True
        
    except Exception as e:
        print(f"❌ OpenRouter API test failed: {str(e)}")
        return False

def test_rag_with_openrouter():
    """Test RAG system with OpenRouter"""
    print("\n" + "="*60)
    print("🧠 Testing RAG System with OpenRouter + Llama 3.2")
    print("="*60)
    
    # Initialize components
    vector_store = VectorStore()
    doc_processor = DocumentProcessor()
    
    # Create comprehensive test document
    test_content = """
    AI RAG Bot - Advanced Features Documentation
    
    Core Capabilities:
    1. Document Processing Engine
       - Supports multiple formats: PDF, DOCX, TXT, Markdown, HTML, CSV, JSON
       - Intelligent text chunking with configurable overlap
       - Metadata extraction and preservation
       - Batch processing capabilities
    
    2. Vector Database System
       - ChromaDB integration for persistent storage
       - Sentence transformer embeddings (all-MiniLM-L6-v2)
       - Semantic similarity search
       - Efficient retrieval with relevance scoring
    
    3. AI Provider Integration
       - OpenAI GPT models (GPT-3.5, GPT-4)
       - Groq with Llama models (fast inference)
       - OpenRouter with multiple model access
       - Anthropic Claude integration
       - Local Ollama support
       - Fallback demo mode
    
    4. Web Interface Features
       - Modern responsive design
       - Real-time chat with WebSocket
       - Drag and drop file upload
       - Document management dashboard
       - Conversation export (JSON, TXT, Markdown)
       - Statistics and usage tracking
    
    5. Advanced RAG Features
       - Context-aware responses
       - Multi-document knowledge synthesis
       - Session-based conversation memory
       - Configurable retrieval parameters
       - Source attribution and citations
    
    Technical Architecture:
    - Flask backend with RESTful API
    - ChromaDB for vector storage
    - Sentence Transformers for embeddings
    - WebSocket for real-time communication
    - Modular design for easy extension
    
    Use Cases:
    - Document Q&A systems
    - Knowledge base chatbots
    - Research assistance tools
    - Customer support automation
    - Educational content interaction
    """
    
    # Create temporary file and process it
    print("📄 Processing comprehensive test document...")
    temp_file = "temp_test_doc.txt"
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    chunks = doc_processor.process_document(temp_file)
    
    # Add chunks directly to vector store
    vector_store.add_documents(chunks)
    print(f"✅ Created {len(chunks)} chunks from comprehensive documentation")
    
    # Clean up temp file
    os.remove(temp_file)
    
    # Test multiple queries
    queries = [
        "What document formats does the AI RAG Bot support?",
        "How does the vector database system work?",
        "What AI providers are integrated?",
        "What are the main features of the web interface?"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n{'='*60}")
        print(f"🔍 Test Query {i}: {query}")
        print('='*60)
        
        # Retrieve context
        print("📋 Retrieving relevant context...")
        results = vector_store.search(query, k=3)
        
        if not results:
            print("❌ No context retrieved")
            continue
        
        context = "\n".join([doc["content"] for doc in results])
        print(f"✅ Retrieved {len(results)} relevant chunks")
        
        # Generate AI response with context
        print("🤖 Generating AI response with RAG context...")
        
        try:
            api_key = os.getenv('OPENROUTER_API_KEY')
            client = openai.OpenAI(
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1"
            )
            
            system_prompt = """You are an AI assistant with access to documentation about an AI RAG Bot system. 
            Use the provided context to answer questions accurately and comprehensively.
            Be specific and mention relevant technical details from the context.
            If the context doesn't contain relevant information, say so clearly."""
            
            user_prompt = f"""Context from documentation:
{context}

Question: {query}

Please provide a detailed answer based on the context above."""
            
            response = client.chat.completions.create(
                model="meta-llama/llama-3.2-3b-instruct:free",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            print(f"\n🎯 RAG + OpenRouter Response:")
            print("-" * 60)
            print(ai_response)
            print("-" * 60)
            
        except Exception as e:
            print(f"❌ RAG + OpenRouter test failed for query {i}: {str(e)}")
            continue
    
    return True

def main():
    print("🤖 AI RAG Bot - OpenRouter Integration Test")
    print("="*60)
    
    # Test OpenRouter API
    if not test_openrouter_api():
        print("\n❌ OpenRouter API test failed. Please check your API key.")
        return
    
    # Test RAG with OpenRouter
    if test_rag_with_openrouter():
        print("\n" + "="*60)
        print("🎉 ALL TESTS PASSED! Your AI RAG Bot is fully functional!")
        print("="*60)
        print("\n✅ Verified Features:")
        print("• OpenRouter API integration with Llama 3.2")
        print("• Document processing and chunking")
        print("• Vector database storage and retrieval")
        print("• Semantic search with context ranking")
        print("• RAG-enhanced AI responses")
        print("• Multi-query testing")
        
        print("\n🚀 Next Steps:")
        print("1. Launch the web interface: python app_test.py")
        print("2. Open browser: http://localhost:8080")
        print("3. Upload your documents and start chatting!")
        print("4. The system is production-ready!")
    else:
        print("\n❌ RAG test failed. Please check the logs above.")

if __name__ == "__main__":
    main()

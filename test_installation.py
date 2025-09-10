#!/usr/bin/env python3
"""
Test script to verify AI RAG Bot installation
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import flask
        print("✅ Flask imported successfully")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False
    
    try:
        import anthropic
        print("✅ Anthropic imported successfully")
    except ImportError as e:
        print(f"❌ Anthropic import failed: {e}")
        return False
    
    try:
        import chromadb
        print("✅ ChromaDB imported successfully")
    except ImportError as e:
        print(f"❌ ChromaDB import failed: {e}")
        return False
    
    try:
        from sentence_transformers import SentenceTransformer
        print("✅ Sentence Transformers imported successfully")
    except ImportError as e:
        print(f"❌ Sentence Transformers import failed: {e}")
        return False
    
    try:
        import PyPDF2
        print("✅ PyPDF2 imported successfully")
    except ImportError as e:
        print(f"❌ PyPDF2 import failed: {e}")
        return False
    
    try:
        from docx import Document
        print("✅ python-docx imported successfully")
    except ImportError as e:
        print(f"❌ python-docx import failed: {e}")
        return False
    
    return True

def test_config():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    try:
        from config import settings
        print("✅ Configuration loaded successfully")
        
        # Check if .env file exists
        if os.path.exists('.env'):
            print("✅ .env file found")
        else:
            print("⚠️  .env file not found - you'll need to configure your API key")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_components():
    """Test individual components"""
    print("\nTesting components...")
    
    try:
        from document_processor import DocumentProcessor
        processor = DocumentProcessor()
        print("✅ Document Processor initialized successfully")
    except Exception as e:
        print(f"❌ Document Processor test failed: {e}")
        return False
    
    try:
        from vector_store import VectorStore
        # Don't initialize to avoid creating files during test
        print("✅ Vector Store module loaded successfully")
    except Exception as e:
        print(f"❌ Vector Store test failed: {e}")
        return False
    
    try:
        from chat_manager import ChatManager
        print("✅ Chat Manager module loaded successfully")
    except Exception as e:
        print(f"❌ Chat Manager test failed: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🤖 AI RAG Bot Installation Test")
    print("=" * 40)
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
    
    # Test configuration
    if not test_config():
        all_passed = False
    
    # Test components
    if not test_components():
        all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 All tests passed! AI RAG Bot is ready to use.")
        print("\nNext steps:")
        print("1. Add your Anthropic API key to the .env file")
        print("2. Run: python app.py")
        print("3. Open http://localhost:5000 in your browser")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

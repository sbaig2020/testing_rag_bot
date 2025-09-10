import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import json

from flask import Flask, request, jsonify, render_template, send_from_directory, session
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.utils import secure_filename
import uuid

from config_simple import settings, get_max_file_size_bytes, is_allowed_file
from document_processor import DocumentProcessor
from vector_store import VectorStore
from chat_manager_free import FreeChatManager

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = settings.secret_key
app.config['MAX_CONTENT_LENGTH'] = get_max_file_size_bytes()

# Initialize extensions
CORS(app, origins=settings.cors_origins)
socketio = SocketIO(app, cors_allowed_origins=settings.cors_origins)

# Initialize components
document_processor = DocumentProcessor()
vector_store = VectorStore()
chat_manager = FreeChatManager(vector_store)

# Global state
active_sessions = {}

@app.route('/')
def index():
    """Main chat interface"""
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    try:
        vector_health = vector_store.health_check()
        
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "ai_provider": chat_manager.provider,
            "components": {
                "vector_store": vector_health,
                "document_processor": {"status": "healthy"},
                "chat_manager": {"status": "healthy", "provider": chat_manager.provider}
            },
            "version": "1.0.0-test"
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/session', methods=['POST'])
def create_session():
    """Create a new chat session"""
    try:
        data = request.get_json() or {}
        system_prompt = data.get('system_prompt')
        session_settings = data.get('settings', {})
        
        session_id = chat_manager.create_session(system_prompt, session_settings)
        
        return jsonify({
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "status": "created",
            "ai_provider": chat_manager.provider
        })
        
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/session/<session_id>/chat', methods=['POST'])
def chat(session_id):
    """Send a message and get AI response"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "Message is required"}), 400
        
        user_message = data['message']
        use_rag = data.get('use_rag', True)
        rag_query = data.get('rag_query')
        
        # Generate response
        response_data = chat_manager.generate_response(
            session_id, user_message, use_rag, rag_query
        )
        
        if "error" in response_data:
            return jsonify(response_data), 500
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload and process documents"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not is_allowed_file(file.filename):
            return jsonify({
                "error": f"File type not allowed. Supported: {', '.join(settings.allowed_extensions)}"
            }), 400
        
        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{filename}"
        file_path = os.path.join(settings.upload_folder, filename)
        
        file.save(file_path)
        logger.info(f"File uploaded: {file_path}")
        
        # Process document
        try:
            chunks = document_processor.process_document(file_path)
            
            # Add to vector store
            success = vector_store.add_documents(chunks)
            
            if success:
                return jsonify({
                    "filename": filename,
                    "original_filename": file.filename,
                    "chunks_created": len(chunks),
                    "file_size": os.path.getsize(file_path),
                    "processed_at": datetime.now().isoformat(),
                    "status": "processed"
                })
            else:
                return jsonify({"error": "Failed to add documents to vector store"}), 500
                
        except Exception as e:
            # Clean up file if processing failed
            if os.path.exists(file_path):
                os.remove(file_path)
            raise e
        
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/documents')
def list_documents():
    """List all documents in the vector store"""
    try:
        limit = request.args.get('limit', 100, type=int)
        documents = vector_store.get_all_documents(limit)
        
        # Group by source file
        files = {}
        for doc in documents:
            source = doc["metadata"].get("source_file", "unknown")
            if source not in files:
                files[source] = {
                    "source_file": source,
                    "chunks": 0,
                    "file_type": doc["metadata"].get("file_type", "unknown"),
                    "created_at": doc["metadata"].get("created_at")
                }
            files[source]["chunks"] += 1
        
        return jsonify({
            "documents": list(files.values()),
            "total_chunks": len(documents),
            "total_files": len(files)
        })
        
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/statistics')
def get_statistics():
    """Get system statistics"""
    try:
        vector_stats = vector_store.get_statistics()
        sessions = chat_manager.get_all_sessions()
        
        return jsonify({
            "vector_store": vector_stats,
            "chat_sessions": {
                "total_sessions": len(sessions),
                "active_sessions": len(active_sessions),
                "sessions": sessions
            },
            "system": {
                "ai_provider": chat_manager.provider,
                "upload_folder": settings.upload_folder,
                "max_file_size": settings.max_file_size,
                "allowed_extensions": settings.allowed_extensions,
                "default_model": settings.default_model
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/test-upload')
def test_upload():
    """Create a test document for demonstration"""
    try:
        # Create a sample document
        test_content = """
# AI RAG Bot Test Document

This is a test document to demonstrate the RAG capabilities of the AI bot.

## Features
- Document processing and chunking
- Vector embeddings for semantic search
- Context retrieval for AI responses
- Multi-format support (PDF, DOCX, TXT, MD, etc.)

## How it works
1. Documents are uploaded and processed
2. Text is extracted and split into chunks
3. Embeddings are generated using sentence transformers
4. Chunks are stored in ChromaDB vector database
5. When users ask questions, relevant chunks are retrieved
6. AI uses the retrieved context to generate informed responses

## Example Questions
- What are the main features of this system?
- How does the RAG process work?
- What file formats are supported?

This document can be used to test the search and retrieval functionality.
        """
        
        # Save test document
        test_filename = f"test_document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        test_path = os.path.join(settings.upload_folder, test_filename)
        
        with open(test_path, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # Process the test document
        chunks = document_processor.process_document(test_path)
        success = vector_store.add_documents(chunks)
        
        if success:
            return jsonify({
                "message": "Test document created and processed successfully",
                "filename": test_filename,
                "chunks_created": len(chunks),
                "status": "success"
            })
        else:
            return jsonify({"error": "Failed to process test document"}), 500
            
    except Exception as e:
        logger.error(f"Error creating test document: {str(e)}")
        return jsonify({"error": str(e)}), 500

# WebSocket events for real-time chat
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('connected', {
        'status': 'Connected to AI RAG Bot (Test Mode)',
        'provider': chat_manager.provider
    })

@socketio.on('join_session')
def handle_join_session(data):
    """Join a chat session room"""
    session_id = data.get('session_id')
    if session_id:
        join_room(session_id)
        active_sessions[request.sid] = session_id
        emit('joined_session', {'session_id': session_id})
        logger.info(f"Client {request.sid} joined session {session_id}")

@socketio.on('send_message')
def handle_message(data):
    """Handle real-time message sending"""
    try:
        session_id = data.get('session_id')
        message = data.get('message')
        use_rag = data.get('use_rag', True)
        
        if not session_id or not message:
            emit('error', {'error': 'Session ID and message are required'})
            return
        
        # Emit user message to room
        socketio.emit('user_message', {
            'message': message,
            'timestamp': datetime.now().isoformat()
        }, room=session_id)
        
        # Generate AI response
        response_data = chat_manager.generate_response(session_id, message, use_rag)
        
        if "error" in response_data:
            emit('error', response_data)
        else:
            # Emit AI response to room
            socketio.emit('ai_response', response_data, room=session_id)
        
    except Exception as e:
        logger.error(f"Error handling message: {str(e)}")
        emit('error', {'error': str(e)})

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs(settings.upload_folder, exist_ok=True)
    os.makedirs(os.path.dirname(settings.log_file), exist_ok=True)
    
    print("\n" + "="*60)
    print("🤖 AI RAG Bot - Test Mode")
    print("="*60)
    print(f"🔧 AI Provider: {chat_manager.provider}")
    print(f"📁 Upload folder: {settings.upload_folder}")
    print(f"🗄️ Vector store: {settings.vector_db_path}")
    print(f"📄 Supported files: {', '.join(settings.allowed_extensions)}")
    print("="*60)
    
    if chat_manager.provider == "demo":
        print("⚠️  DEMO MODE: No AI provider detected")
        print("   For real AI responses:")
        print("   • Get free Groq API key: https://console.groq.com/")
        print("   • Set GROQ_API_KEY environment variable")
        print("   • Or install Ollama for local AI")
        print("="*60)
    
    logger.info("Starting AI RAG Bot test server...")
    
    # Run the app
    socketio.run(
        app,
        host='0.0.0.0',
        port=8080,
        debug=settings.flask_debug,
        allow_unsafe_werkzeug=True
    )

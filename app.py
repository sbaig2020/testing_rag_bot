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

from config import settings, get_max_file_size_bytes, is_allowed_file
from document_processor import DocumentProcessor
from vector_store import VectorStore
from chat_manager import ChatManager

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
chat_manager = ChatManager(vector_store)

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
            "components": {
                "vector_store": vector_health,
                "document_processor": {"status": "healthy"},
                "chat_manager": {"status": "healthy"}
            },
            "version": "1.0.0"
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
            "status": "created"
        })
        
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/session/<session_id>')
def get_session(session_id):
    """Get session information"""
    try:
        session_data = chat_manager.get_session(session_id)
        if not session_data:
            return jsonify({"error": "Session not found"}), 404
        
        return jsonify({
            "session_id": session_id,
            "created_at": session_data.created_at,
            "updated_at": session_data.updated_at,
            "message_count": len(session_data.messages),
            "system_prompt": session_data.system_prompt,
            "settings": session_data.settings
        })
        
    except Exception as e:
        logger.error(f"Error getting session: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/session/<session_id>/messages')
def get_messages(session_id):
    """Get conversation history"""
    try:
        limit = request.args.get('limit', type=int)
        messages = chat_manager.get_conversation_history(session_id, limit)
        
        return jsonify({
            "session_id": session_id,
            "messages": messages,
            "count": len(messages)
        })
        
    except Exception as e:
        logger.error(f"Error getting messages: {str(e)}")
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

@app.route('/api/documents/search', methods=['POST'])
def search_documents():
    """Search documents in the vector store"""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({"error": "Query is required"}), 400
        
        query = data['query']
        n_results = data.get('n_results', 5)
        filter_metadata = data.get('filter')
        
        results = vector_store.search(query, n_results, filter_metadata)
        
        return jsonify({
            "query": query,
            "results": results,
            "count": len(results)
        })
        
    except Exception as e:
        logger.error(f"Error searching documents: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/documents/<path:source_file>', methods=['DELETE'])
def delete_document(source_file):
    """Delete documents by source file"""
    try:
        success = vector_store.delete_documents_by_source(source_file)
        
        if success:
            # Also try to delete the physical file
            try:
                file_path = os.path.join(settings.upload_folder, os.path.basename(source_file))
                if os.path.exists(file_path):
                    os.remove(file_path)
            except:
                pass  # File might not exist or be accessible
            
            return jsonify({"status": "deleted", "source_file": source_file})
        else:
            return jsonify({"error": "Document not found"}), 404
            
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
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
                "upload_folder": settings.upload_folder,
                "max_file_size": settings.max_file_size,
                "allowed_extensions": settings.allowed_extensions,
                "default_model": settings.default_model
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/session/<session_id>/export')
def export_conversation(session_id):
    """Export conversation in various formats"""
    try:
        format_type = request.args.get('format', 'json').lower()
        
        exported_data = chat_manager.export_conversation(session_id, format_type)
        
        if exported_data is None:
            return jsonify({"error": "Session not found or invalid format"}), 404
        
        # Set appropriate content type
        if format_type == 'json':
            content_type = 'application/json'
            filename = f"conversation_{session_id}.json"
        elif format_type == 'txt':
            content_type = 'text/plain'
            filename = f"conversation_{session_id}.txt"
        elif format_type == 'md':
            content_type = 'text/markdown'
            filename = f"conversation_{session_id}.md"
        else:
            return jsonify({"error": "Invalid format"}), 400
        
        return app.response_class(
            exported_data,
            mimetype=content_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error exporting conversation: {str(e)}")
        return jsonify({"error": str(e)}), 500

# WebSocket events for real-time chat
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('connected', {'status': 'Connected to AI RAG Bot'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {request.sid}")
    
    # Clean up session if needed
    if request.sid in active_sessions:
        del active_sessions[request.sid]

@socketio.on('join_session')
def handle_join_session(data):
    """Join a chat session room"""
    session_id = data.get('session_id')
    if session_id:
        join_room(session_id)
        active_sessions[request.sid] = session_id
        emit('joined_session', {'session_id': session_id})
        logger.info(f"Client {request.sid} joined session {session_id}")

@socketio.on('leave_session')
def handle_leave_session(data):
    """Leave a chat session room"""
    session_id = data.get('session_id')
    if session_id:
        leave_room(session_id)
        if request.sid in active_sessions:
            del active_sessions[request.sid]
        emit('left_session', {'session_id': session_id})
        logger.info(f"Client {request.sid} left session {session_id}")

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

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(413)
def file_too_large(error):
    return jsonify({"error": f"File too large. Maximum size: {settings.max_file_size}"}), 413

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs(settings.upload_folder, exist_ok=True)
    os.makedirs(os.path.dirname(settings.log_file), exist_ok=True)
    
    logger.info("Starting AI RAG Bot server...")
    logger.info(f"Vector store path: {settings.vector_db_path}")
    logger.info(f"Upload folder: {settings.upload_folder}")
    logger.info(f"Supported file types: {', '.join(settings.allowed_extensions)}")
    
    # Run the app
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=settings.flask_debug,
        allow_unsafe_werkzeug=True
    )

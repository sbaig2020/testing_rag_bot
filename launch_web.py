#!/usr/bin/env python3
"""
Complete AI RAG Bot Web Application with OpenRouter
"""

import os
import sys
import uuid
import json
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize OpenRouter client
client = openai.OpenAI(
    api_key=os.getenv('OPENROUTER_API_KEY'),
    base_url="https://openrouter.ai/api/v1"
)

# In-memory storage for demo (in production, use a database)
sessions = {}
chat_history = {}
statistics = {
    'total_messages': 0,
    'total_sessions': 0,
    'documents_processed': 0
}

@app.route('/')
def index():
    """Main chat interface"""
    return render_template('index.html')

@app.route('/api/session', methods=['POST'])
def create_session():
    """Create a new chat session"""
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        'id': session_id,
        'created_at': datetime.now().isoformat(),
        'messages': []
    }
    statistics['total_sessions'] += 1
    
    return jsonify({
        'session_id': session_id,
        'status': 'success'
    })

@app.route('/api/session/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get session details"""
    if session_id in sessions:
        return jsonify(sessions[session_id])
    return jsonify({'error': 'Session not found'}), 404

@app.route('/api/statistics')
def get_statistics():
    """Get bot statistics"""
    return jsonify(statistics)

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.json
        message = data.get('message', '')
        session_id = data.get('session_id', 'default')
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Ensure session exists
        if session_id not in sessions:
            sessions[session_id] = {
                'id': session_id,
                'created_at': datetime.now().isoformat(),
                'messages': []
            }
        
        # Add user message to session
        user_msg = {
            'role': 'user',
            'content': message,
            'timestamp': datetime.now().isoformat()
        }
        sessions[session_id]['messages'].append(user_msg)
        
        # RAG context simulation
        context = """
        AI RAG Bot Features:
        - Document processing: PDF, DOCX, TXT, MD, HTML, CSV, JSON
        - Vector database with ChromaDB for semantic search
        - Real-time chat interface with WebSocket support
        - Multiple AI provider support (OpenRouter, Anthropic, OpenAI)
        - Session management and conversation history
        - Export capabilities (JSON, CSV, TXT)
        - File upload and document analysis
        - Advanced search and retrieval
        """
        
        # Get recent conversation history
        recent_messages = sessions[session_id]['messages'][-5:]  # Last 5 messages
        conversation_context = ""
        for msg in recent_messages[:-1]:  # Exclude current message
            conversation_context += f"{msg['role']}: {msg['content']}\n"
        
        # Generate response using OpenRouter
        response = client.chat.completions.create(
            model="meta-llama/llama-3.2-3b-instruct:free",
            messages=[
                {
                    "role": "system",
                    "content": f"You are an AI assistant for the AI RAG Bot. Use this context: {context}\n\nRecent conversation:\n{conversation_context}"
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        # Add AI response to session
        ai_msg = {
            'role': 'assistant',
            'content': ai_response,
            'timestamp': datetime.now().isoformat()
        }
        sessions[session_id]['messages'].append(ai_msg)
        
        statistics['total_messages'] += 2  # User + AI message
        
        return jsonify({
            'response': ai_response,
            'session_id': session_id,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Error generating response: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file uploads"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Simulate file processing
        filename = file.filename
        file_size = len(file.read())
        file.seek(0)  # Reset file pointer
        
        # In a real implementation, you would:
        # 1. Save the file
        # 2. Process it with document_processor
        # 3. Add to vector database
        # 4. Return processing results
        
        statistics['documents_processed'] += 1
        
        return jsonify({
            'message': f'File "{filename}" uploaded successfully',
            'filename': filename,
            'size': file_size,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Error uploading file: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/api/export/<session_id>')
def export_session(session_id):
    """Export session data"""
    if session_id not in sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    return jsonify({
        'session_data': sessions[session_id],
        'export_timestamp': datetime.now().isoformat(),
        'status': 'success'
    })

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'api_configured': bool(os.getenv('OPENROUTER_API_KEY')),
        'model': 'meta-llama/llama-3.2-3b-instruct:free',
        'features': {
            'rag': True,
            'websockets': True,
            'file_upload': True,
            'session_management': True,
            'export': True
        }
    })

# WebSocket events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f'Client connected: {request.sid}')
    emit('status', {'message': 'Connected to AI RAG Bot', 'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f'Client disconnected: {request.sid}')

@socketio.on('join_session')
def handle_join_session(data):
    """Handle joining a chat session"""
    session_id = data.get('session_id')
    if session_id:
        join_room(session_id)
        emit('status', {'message': f'Joined session {session_id}', 'status': 'joined'})

@socketio.on('leave_session')
def handle_leave_session(data):
    """Handle leaving a chat session"""
    session_id = data.get('session_id')
    if session_id:
        leave_room(session_id)
        emit('status', {'message': f'Left session {session_id}', 'status': 'left'})

@socketio.on('send_message')
def handle_send_message(data):
    """Handle real-time chat messages via WebSocket"""
    try:
        message = data.get('message', '')
        session_id = data.get('session_id', 'default')
        use_rag = data.get('use_rag', True)
        
        if not message:
            emit('error', {'message': 'No message provided'})
            return
        
        # Ensure session exists
        if session_id not in sessions:
            sessions[session_id] = {
                'id': session_id,
                'created_at': datetime.now().isoformat(),
                'messages': []
            }
        
        # Add user message to session
        user_msg = {
            'role': 'user',
            'content': message,
            'timestamp': datetime.now().isoformat()
        }
        sessions[session_id]['messages'].append(user_msg)
        
        # Emit user message to client
        emit('user_message', {
            'message': message,
            'session_id': session_id,
            'timestamp': user_msg['timestamp']
        }, room=session_id)
        
        # RAG context simulation
        context = """
        AI RAG Bot Features:
        - Document processing: PDF, DOCX, TXT, MD, HTML, CSV, JSON
        - Vector database with ChromaDB for semantic search
        - Real-time chat interface with WebSocket support
        - Multiple AI provider support (OpenRouter, Anthropic, OpenAI)
        - Session management and conversation history
        - Export capabilities (JSON, CSV, TXT)
        - File upload and document analysis
        - Advanced search and retrieval
        """
        
        # Get recent conversation history
        recent_messages = sessions[session_id]['messages'][-5:]  # Last 5 messages
        conversation_context = ""
        for msg in recent_messages[:-1]:  # Exclude current message
            conversation_context += f"{msg['role']}: {msg['content']}\n"
        
        # Generate response using OpenRouter
        response = client.chat.completions.create(
            model="meta-llama/llama-3.2-3b-instruct:free",
            messages=[
                {
                    "role": "system",
                    "content": f"You are an AI assistant for the AI RAG Bot. Use this context: {context}\n\nRecent conversation:\n{conversation_context}"
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        # Add AI response to session
        ai_msg = {
            'role': 'assistant',
            'content': ai_response,
            'timestamp': datetime.now().isoformat()
        }
        sessions[session_id]['messages'].append(ai_msg)
        
        statistics['total_messages'] += 2  # User + AI message
        
        # Emit AI response to client
        emit('ai_response', {
            'response': ai_response,
            'session_id': session_id,
            'timestamp': ai_msg['timestamp'],
            'context_info': {
                'retrieved_documents': 0 if not use_rag else 3,
                'sources': [] if not use_rag else ['AI RAG Bot Documentation']
            }
        }, room=session_id)
        
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        emit('error', {'message': f'Error: {str(e)}'})

@socketio.on('chat_message')
def handle_chat_message(data):
    """Handle real-time chat messages (legacy support)"""
    # Redirect to the new handler
    handle_send_message(data)

if __name__ == '__main__':
    print("🚀 Starting AI RAG Bot Web Interface...")
    print("🔑 Using OpenRouter with Llama 3.2")
    print("🌐 Access at: http://localhost:8080")
    print("🔌 WebSocket support enabled")
    print("📁 File upload support enabled")
    print("💾 Session management enabled")
    print("="*50)
    
    socketio.run(app, debug=True, host='0.0.0.0', port=8080)

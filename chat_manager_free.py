import logging
import json
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import uuid
import os
import time

from config_simple import settings
from vector_store import VectorStore

# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)

@dataclass
class ChatMessage:
    """Represents a chat message"""
    id: str
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ChatSession:
    """Represents a chat session"""
    session_id: str
    messages: List[ChatMessage]
    created_at: str
    updated_at: str
    system_prompt: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None

class FreeChatManager:
    """Manages chat conversations with free AI providers"""
    
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.sessions: Dict[str, ChatSession] = {}
        self.default_system_prompt = self._get_default_system_prompt()
        
        # Determine which provider to use
        self.provider = self._detect_provider()
        logger.info(f"Using AI provider: {self.provider}")
    
    def _detect_provider(self) -> str:
        """Detect which AI provider to use"""
        # Check for Groq API key
        if os.getenv('GROQ_API_KEY'):
            return "groq"
        
        # Check for OpenAI API key
        if os.getenv('OPENAI_API_KEY'):
            return "openai"
        
        # Check if Ollama is running
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                return "ollama"
        except:
            pass
        
        # Fallback to demo mode
        return "demo"
    
    def _get_default_system_prompt(self) -> str:
        """Get the default system prompt for the AI assistant"""
        return """You are an advanced AI assistant with access to a knowledge base through RAG (Retrieval-Augmented Generation). 

Key capabilities:
- Answer questions using both your training data and the provided context from documents
- Analyze and summarize uploaded documents
- Provide detailed explanations with citations when using retrieved information
- Handle multi-turn conversations with context awareness
- Support various document types (PDF, DOCX, TXT, MD, HTML, CSV, JSON)

Guidelines:
- Always cite sources when using information from retrieved documents
- If retrieved context is relevant, incorporate it naturally into your response
- If no relevant context is found, rely on your training data but mention this
- Be helpful, accurate, and conversational
- Ask clarifying questions when needed
- Provide structured responses for complex queries

Current session context will include relevant document excerpts when available."""

    def create_session(self, system_prompt: Optional[str] = None, session_settings: Optional[Dict[str, Any]] = None) -> str:
        """Create a new chat session"""
        session_id = str(uuid.uuid4())
        
        session = ChatSession(
            session_id=session_id,
            messages=[],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            system_prompt=system_prompt or self.default_system_prompt,
            settings=session_settings or {}
        )
        
        self.sessions[session_id] = session
        logger.info(f"Created new chat session: {session_id}")
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get a chat session by ID"""
        return self.sessions.get(session_id)
    
    def add_message(self, session_id: str, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[ChatMessage]:
        """Add a message to a chat session"""
        session = self.sessions.get(session_id)
        if not session:
            logger.error(f"Session not found: {session_id}")
            return None
        
        message = ChatMessage(
            id=str(uuid.uuid4()),
            role=role,
            content=content,
            timestamp=datetime.now().isoformat(),
            metadata=metadata or {}
        )
        
        session.messages.append(message)
        session.updated_at = datetime.now().isoformat()
        
        # Limit conversation history
        if len(session.messages) > settings.max_conversation_history:
            # Keep system messages and recent messages
            system_messages = [msg for msg in session.messages if msg.role == 'system']
            recent_messages = session.messages[-(settings.max_conversation_history - len(system_messages)):]
            session.messages = system_messages + recent_messages
        
        return message
    
    def generate_response(self, session_id: str, user_message: str, use_rag: bool = True, rag_query: Optional[str] = None) -> Dict[str, Any]:
        """Generate AI response for a user message"""
        try:
            session = self.sessions.get(session_id)
            if not session:
                return {"error": "Session not found"}
            
            # Add user message to session
            user_msg = self.add_message(session_id, "user", user_message)
            
            # Retrieve relevant context if RAG is enabled
            context_info = {}
            context_text = ""
            if use_rag:
                search_query = rag_query or user_message
                retrieved_docs = self.vector_store.search(search_query, n_results=3)
                
                if retrieved_docs:
                    context_info = {
                        "retrieved_documents": len(retrieved_docs),
                        "sources": list(set(doc["metadata"].get("source_file", "unknown") for doc in retrieved_docs))
                    }
                    
                    # Format context for the AI
                    context_text = self._format_context(retrieved_docs)
                else:
                    context_info["retrieved_documents"] = 0
            else:
                context_info["rag_disabled"] = True
            
            # Generate response based on provider
            if self.provider == "groq":
                response_content = self._generate_groq_response(session, user_message, context_text)
            elif self.provider == "openai":
                response_content = self._generate_openai_response(session, user_message, context_text)
            elif self.provider == "ollama":
                response_content = self._generate_ollama_response(session, user_message, context_text)
            else:
                response_content = self._generate_demo_response(session, user_message, context_text)
            
            # Add assistant response to session
            assistant_msg = self.add_message(
                session_id, 
                "assistant", 
                response_content,
                metadata={
                    "provider": self.provider,
                    **context_info
                }
            )
            
            return {
                "response": response_content,
                "message_id": assistant_msg.id,
                "provider": self.provider,
                "context_info": context_info,
                "timestamp": assistant_msg.timestamp
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return {"error": str(e)}
    
    def _generate_groq_response(self, session: ChatSession, user_message: str, context: str) -> str:
        """Generate response using Groq API"""
        try:
            api_key = os.getenv('GROQ_API_KEY')
            if not api_key:
                return "Error: GROQ_API_KEY not found in environment variables."
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Prepare messages
            messages = [{"role": "system", "content": session.system_prompt}]
            
            # Add recent conversation history
            for msg in session.messages[-10:]:  # Last 10 messages
                if msg.role in ['user', 'assistant']:
                    messages.append({"role": msg.role, "content": msg.content})
            
            # Add context if available
            if context:
                messages.append({
                    "role": "system", 
                    "content": f"Relevant context from documents:\n{context}\n\nUse this context to inform your response when relevant."
                })
            
            data = {
                "messages": messages,
                "model": "llama3-8b-8192",
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                return f"Error from Groq API: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"Error calling Groq API: {str(e)}"
    
    def _generate_openai_response(self, session: ChatSession, user_message: str, context: str) -> str:
        """Generate response using OpenAI API"""
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                return "Error: OPENAI_API_KEY not found in environment variables."
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Prepare messages
            messages = [{"role": "system", "content": session.system_prompt}]
            
            # Add recent conversation history
            for msg in session.messages[-10:]:
                if msg.role in ['user', 'assistant']:
                    messages.append({"role": msg.role, "content": msg.content})
            
            # Add context if available
            if context:
                messages.append({
                    "role": "system", 
                    "content": f"Relevant context from documents:\n{context}\n\nUse this context to inform your response when relevant."
                })
            
            data = {
                "messages": messages,
                "model": "gpt-3.5-turbo",
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                return f"Error from OpenAI API: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"Error calling OpenAI API: {str(e)}"
    
    def _generate_ollama_response(self, session: ChatSession, user_message: str, context: str) -> str:
        """Generate response using local Ollama"""
        try:
            # Get available models
            models_response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if models_response.status_code != 200:
                return "Error: Ollama is not running. Please start Ollama and pull a model."
            
            models = models_response.json().get("models", [])
            if not models:
                return "Error: No models available in Ollama. Please pull a model (e.g., 'ollama pull llama2')."
            
            model_name = models[0]["name"]
            
            # Prepare prompt with context
            prompt = session.system_prompt + "\n\n"
            
            if context:
                prompt += f"Relevant context from documents:\n{context}\n\n"
            
            # Add recent conversation
            for msg in session.messages[-5:]:
                if msg.role == 'user':
                    prompt += f"User: {msg.content}\n"
                elif msg.role == 'assistant':
                    prompt += f"Assistant: {msg.content}\n"
            
            prompt += f"User: {user_message}\nAssistant: "
            
            data = {
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 500
                }
            }
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "No response generated.")
            else:
                return f"Error from Ollama: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"Error calling Ollama: {str(e)}"
    
    def _generate_demo_response(self, session: ChatSession, user_message: str, context: str) -> str:
        """Generate a demo response when no AI provider is available"""
        responses = [
            f"🤖 **Demo Mode Response**\n\nI received your message: \"{user_message}\"\n\n",
            f"This is a demonstration of the AI RAG Bot. In demo mode, I can show you how the system works:\n\n",
            f"✅ **RAG System**: {'Context found and would be used' if context else 'No relevant context found'}\n",
            f"✅ **Session Management**: Your message has been stored in session {session.session_id[:8]}...\n",
            f"✅ **Document Processing**: {len(self.vector_store.get_all_documents(10))} documents in knowledge base\n\n",
            f"**To get real AI responses, please:**\n",
            f"1. Get a free Groq API key from https://console.groq.com/\n",
            f"2. Set GROQ_API_KEY environment variable\n",
            f"3. Or install Ollama locally for offline AI\n\n",
            f"**Your message analysis:**\n",
            f"- Length: {len(user_message)} characters\n",
            f"- Word count: {len(user_message.split())} words\n",
            f"- Contains question: {'Yes' if '?' in user_message else 'No'}\n"
        ]
        
        if context:
            responses.append(f"\n**Retrieved Context Preview:**\n{context[:200]}...")
        
        return "".join(responses)
    
    def _format_context(self, retrieved_docs: List[Dict[str, Any]]) -> str:
        """Format retrieved documents as context"""
        if not retrieved_docs:
            return ""
        
        context_parts = []
        for i, doc in enumerate(retrieved_docs, 1):
            source = doc["metadata"].get("source_file", "Unknown source")
            content = doc["content"][:300] + "..." if len(doc["content"]) > 300 else doc["content"]
            
            context_parts.append(f"[Source {i}: {source}]\n{content}")
        
        return "\n\n".join(context_parts)
    
    def get_conversation_history(self, session_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get conversation history for a session"""
        session = self.sessions.get(session_id)
        if not session:
            return []
        
        messages = session.messages
        if limit:
            messages = messages[-limit:]
        
        return [asdict(msg) for msg in messages]
    
    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """Get all chat sessions (metadata only)"""
        sessions_info = []
        
        for session_id, session in self.sessions.items():
            sessions_info.append({
                "session_id": session_id,
                "created_at": session.created_at,
                "updated_at": session.updated_at,
                "message_count": len(session.messages),
                "last_message": session.messages[-1].content[:100] + "..." if session.messages else None
            })
        
        return sessions_info
    
    def export_conversation(self, session_id: str, format: str = "json") -> Optional[str]:
        """Export conversation in specified format"""
        session = self.sessions.get(session_id)
        if not session:
            return None
        
        if format.lower() == "json":
            return json.dumps(asdict(session), indent=2, ensure_ascii=False)
        
        elif format.lower() == "txt":
            lines = [f"Chat Session: {session_id}"]
            lines.append(f"Provider: {self.provider}")
            lines.append(f"Created: {session.created_at}")
            lines.append(f"Updated: {session.updated_at}")
            lines.append("-" * 50)
            
            for msg in session.messages:
                timestamp = datetime.fromisoformat(msg.timestamp).strftime("%Y-%m-%d %H:%M:%S")
                lines.append(f"\n[{timestamp}] {msg.role.upper()}:")
                lines.append(msg.content)
            
            return "\n".join(lines)
        
        return None

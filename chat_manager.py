import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import uuid

import anthropic

from config import settings
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

class ChatManager:
    """Manages chat conversations and AI interactions"""
    
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.anthropic_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.sessions: Dict[str, ChatSession] = {}
        self.default_system_prompt = self._get_default_system_prompt()
    
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
            if use_rag:
                search_query = rag_query or user_message
                retrieved_docs = self.vector_store.search(search_query, n_results=5)
                
                if retrieved_docs:
                    context_info = {
                        "retrieved_documents": len(retrieved_docs),
                        "sources": list(set(doc["metadata"].get("source_file", "unknown") for doc in retrieved_docs))
                    }
                    
                    # Format context for the AI
                    context_text = self._format_context(retrieved_docs)
                    
                    # Add context as a system message (temporary, not stored in history)
                    context_message = f"\n\nRelevant context from knowledge base:\n{context_text}\n\nPlease use this context to inform your response when relevant, and cite sources when appropriate."
                else:
                    context_message = "\n\nNo relevant context found in the knowledge base. Please respond based on your training data."
                    context_info["retrieved_documents"] = 0
            else:
                context_message = ""
                context_info["rag_disabled"] = True
            
            # Prepare messages for Anthropic API
            api_messages = self._prepare_api_messages(session, context_message)
            
            # Generate response using Anthropic API
            response = self.anthropic_client.messages.create(
                model=session.settings.get("model", settings.default_model),
                max_tokens=session.settings.get("max_tokens", settings.max_tokens),
                temperature=session.settings.get("temperature", settings.temperature),
                system=session.system_prompt,
                messages=api_messages
            )
            
            # Extract response content
            assistant_content = ""
            if response.content:
                for content_block in response.content:
                    if hasattr(content_block, 'text'):
                        assistant_content += content_block.text
            
            # Add assistant response to session
            assistant_msg = self.add_message(
                session_id, 
                "assistant", 
                assistant_content,
                metadata={
                    "model": response.model,
                    "usage": {
                        "input_tokens": response.usage.input_tokens,
                        "output_tokens": response.usage.output_tokens
                    },
                    **context_info
                }
            )
            
            return {
                "response": assistant_content,
                "message_id": assistant_msg.id,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                },
                "context_info": context_info,
                "timestamp": assistant_msg.timestamp
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return {"error": str(e)}
    
    def _prepare_api_messages(self, session: ChatSession, context_message: str = "") -> List[Dict[str, str]]:
        """Prepare messages for Anthropic API"""
        api_messages = []
        
        # Convert session messages to API format
        for msg in session.messages:
            if msg.role in ['user', 'assistant']:
                content = msg.content
                
                # Add context to the last user message if provided
                if msg.role == 'user' and msg == session.messages[-1] and context_message:
                    content += context_message
                
                api_messages.append({
                    "role": msg.role,
                    "content": content
                })
        
        return api_messages
    
    def _format_context(self, retrieved_docs: List[Dict[str, Any]]) -> str:
        """Format retrieved documents as context"""
        if not retrieved_docs:
            return ""
        
        context_parts = []
        for i, doc in enumerate(retrieved_docs, 1):
            source = doc["metadata"].get("source_file", "Unknown source")
            content = doc["content"][:500] + "..." if len(doc["content"]) > 500 else doc["content"]
            
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
    
    def update_system_prompt(self, session_id: str, system_prompt: str) -> bool:
        """Update system prompt for a session"""
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        session.system_prompt = system_prompt
        session.updated_at = datetime.now().isoformat()
        
        # Add system message to history
        self.add_message(session_id, "system", f"System prompt updated: {system_prompt}")
        
        return True
    
    def update_session_settings(self, session_id: str, new_settings: Dict[str, Any]) -> bool:
        """Update settings for a session"""
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        session.settings.update(new_settings)
        session.updated_at = datetime.now().isoformat()
        
        return True
    
    def clear_conversation(self, session_id: str) -> bool:
        """Clear conversation history for a session"""
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        # Keep only system messages
        system_messages = [msg for msg in session.messages if msg.role == 'system']
        session.messages = system_messages
        session.updated_at = datetime.now().isoformat()
        
        return True
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a chat session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Deleted chat session: {session_id}")
            return True
        return False
    
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
            lines.append(f"Created: {session.created_at}")
            lines.append(f"Updated: {session.updated_at}")
            lines.append("-" * 50)
            
            for msg in session.messages:
                timestamp = datetime.fromisoformat(msg.timestamp).strftime("%Y-%m-%d %H:%M:%S")
                lines.append(f"\n[{timestamp}] {msg.role.upper()}:")
                lines.append(msg.content)
            
            return "\n".join(lines)
        
        elif format.lower() == "md":
            lines = [f"# Chat Session: {session_id}"]
            lines.append(f"**Created:** {session.created_at}")
            lines.append(f"**Updated:** {session.updated_at}")
            lines.append("")
            
            for msg in session.messages:
                timestamp = datetime.fromisoformat(msg.timestamp).strftime("%Y-%m-%d %H:%M:%S")
                role_emoji = "🧑" if msg.role == "user" else "🤖" if msg.role == "assistant" else "⚙️"
                lines.append(f"## {role_emoji} {msg.role.title()} - {timestamp}")
                lines.append("")
                lines.append(msg.content)
                lines.append("")
            
            return "\n".join(lines)
        
        return None
    
    def get_session_statistics(self, session_id: str) -> Dict[str, Any]:
        """Get statistics for a session"""
        session = self.sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}
        
        user_messages = [msg for msg in session.messages if msg.role == "user"]
        assistant_messages = [msg for msg in session.messages if msg.role == "assistant"]
        
        total_tokens = 0
        for msg in assistant_messages:
            if msg.metadata and "usage" in msg.metadata:
                total_tokens += msg.metadata["usage"].get("input_tokens", 0)
                total_tokens += msg.metadata["usage"].get("output_tokens", 0)
        
        return {
            "session_id": session_id,
            "total_messages": len(session.messages),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "total_tokens_used": total_tokens,
            "session_duration": session.updated_at,
            "created_at": session.created_at,
            "updated_at": session.updated_at
        }

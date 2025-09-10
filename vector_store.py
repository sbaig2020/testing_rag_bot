import os
import logging
import uuid
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json

import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
import numpy as np

from config_simple import settings
from document_processor import DocumentChunk

# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)

class VectorStore:
    """Manages vector storage and retrieval using ChromaDB"""
    
    def __init__(self):
        self.embedding_model = SentenceTransformer(settings.embedding_model)
        self.client = None
        self.collection = None
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize ChromaDB client and collection"""
        try:
            # Create ChromaDB client
            self.client = chromadb.PersistentClient(
                path=settings.vector_db_path,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            collection_name = "ai_rag_documents"
            try:
                self.collection = self.client.get_collection(collection_name)
                logger.info(f"Loaded existing collection: {collection_name}")
            except:
                self.collection = self.client.create_collection(
                    name=collection_name,
                    metadata={"description": "AI RAG Bot document embeddings"}
                )
                logger.info(f"Created new collection: {collection_name}")
                
        except Exception as e:
            logger.error(f"Error initializing vector database: {str(e)}")
            raise
    
    def add_documents(self, chunks: List[DocumentChunk]) -> bool:
        """Add document chunks to the vector store"""
        try:
            if not chunks:
                logger.warning("No chunks provided to add")
                return False
            
            # Prepare data for ChromaDB
            documents = []
            metadatas = []
            ids = []
            
            for chunk in chunks:
                documents.append(chunk.content)
                
                # Prepare metadata (ChromaDB requires string values)
                metadata = {
                    "source_file": chunk.source_file,
                    "chunk_index": str(chunk.chunk_index),
                    "chunk_id": chunk.chunk_id,
                    "created_at": datetime.now().isoformat(),
                    "file_type": chunk.metadata.get("file_type", "unknown"),
                    "chunk_size": str(len(chunk.content)),
                    "word_count": str(len(chunk.content.split()))
                }
                
                # Add additional metadata as JSON string if needed
                if chunk.metadata:
                    metadata["additional_metadata"] = json.dumps(chunk.metadata)
                
                metadatas.append(metadata)
                ids.append(str(uuid.uuid4()))
            
            # Generate embeddings
            logger.info(f"Generating embeddings for {len(documents)} chunks...")
            embeddings = self.embedding_model.encode(documents).tolist()
            
            # Add to ChromaDB
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings,
                ids=ids
            )
            
            logger.info(f"Successfully added {len(chunks)} chunks to vector store")
            return True
            
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {str(e)}")
            return False
    
    def search(self, query: str, n_results: int = 5, filter_metadata: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        try:
            if not query.strip():
                return []
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query]).tolist()[0]
            
            # Prepare search parameters
            search_params = {
                "query_embeddings": [query_embedding],
                "n_results": min(n_results, 50),  # Limit results
            }
            
            # Add metadata filter if provided
            if filter_metadata:
                search_params["where"] = filter_metadata
            
            # Search in ChromaDB
            results = self.collection.query(**search_params)
            
            # Format results
            formatted_results = []
            if results["documents"] and results["documents"][0]:
                for i in range(len(results["documents"][0])):
                    result = {
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i] if results["distances"] else None,
                        "id": results["ids"][0][i]
                    }
                    
                    # Parse additional metadata if present
                    if "additional_metadata" in result["metadata"]:
                        try:
                            additional = json.loads(result["metadata"]["additional_metadata"])
                            result["metadata"].update(additional)
                            del result["metadata"]["additional_metadata"]
                        except:
                            pass
                    
                    formatted_results.append(result)
            
            logger.info(f"Found {len(formatted_results)} results for query: {query[:50]}...")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching vector store: {str(e)}")
            return []
    
    def get_document_count(self) -> int:
        """Get total number of documents in the store"""
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"Error getting document count: {str(e)}")
            return 0
    
    def get_all_documents(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all documents with metadata"""
        try:
            results = self.collection.get(limit=limit)
            
            formatted_results = []
            if results["documents"]:
                for i in range(len(results["documents"])):
                    result = {
                        "content": results["documents"][i],
                        "metadata": results["metadatas"][i] if results["metadatas"] else {},
                        "id": results["ids"][i]
                    }
                    
                    # Parse additional metadata if present
                    if "additional_metadata" in result["metadata"]:
                        try:
                            additional = json.loads(result["metadata"]["additional_metadata"])
                            result["metadata"].update(additional)
                            del result["metadata"]["additional_metadata"]
                        except:
                            pass
                    
                    formatted_results.append(result)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error getting all documents: {str(e)}")
            return []
    
    def delete_documents_by_source(self, source_file: str) -> bool:
        """Delete all documents from a specific source file"""
        try:
            # Get documents with the specified source file
            results = self.collection.get(
                where={"source_file": source_file}
            )
            
            if results["ids"]:
                self.collection.delete(ids=results["ids"])
                logger.info(f"Deleted {len(results['ids'])} documents from {source_file}")
                return True
            else:
                logger.info(f"No documents found for source file: {source_file}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting documents by source: {str(e)}")
            return False
    
    def delete_document_by_id(self, doc_id: str) -> bool:
        """Delete a specific document by ID"""
        try:
            self.collection.delete(ids=[doc_id])
            logger.info(f"Deleted document with ID: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document by ID: {str(e)}")
            return False
    
    def clear_all_documents(self) -> bool:
        """Clear all documents from the vector store"""
        try:
            # Delete the collection and recreate it
            collection_name = self.collection.name
            self.client.delete_collection(collection_name)
            
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "AI RAG Bot document embeddings"}
            )
            
            logger.info("Cleared all documents from vector store")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing all documents: {str(e)}")
            return False
    
    def get_similar_documents(self, doc_id: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Find documents similar to a given document"""
        try:
            # Get the document by ID
            doc_result = self.collection.get(ids=[doc_id])
            
            if not doc_result["documents"]:
                logger.warning(f"Document with ID {doc_id} not found")
                return []
            
            # Use the document content as query
            query = doc_result["documents"][0]
            
            # Search for similar documents (excluding the original)
            results = self.search(query, n_results + 1)
            
            # Filter out the original document
            similar_docs = [r for r in results if r["id"] != doc_id][:n_results]
            
            return similar_docs
            
        except Exception as e:
            logger.error(f"Error finding similar documents: {str(e)}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        try:
            total_docs = self.get_document_count()
            
            # Get sample of documents to analyze
            sample_docs = self.get_all_documents(limit=100)
            
            # Analyze file types
            file_types = {}
            total_size = 0
            
            for doc in sample_docs:
                file_type = doc["metadata"].get("file_type", "unknown")
                file_types[file_type] = file_types.get(file_type, 0) + 1
                
                chunk_size = doc["metadata"].get("chunk_size")
                if chunk_size and chunk_size.isdigit():
                    total_size += int(chunk_size)
            
            avg_chunk_size = total_size / len(sample_docs) if sample_docs else 0
            
            return {
                "total_documents": total_docs,
                "file_types": file_types,
                "average_chunk_size": round(avg_chunk_size, 2),
                "embedding_model": settings.embedding_model,
                "vector_db_path": settings.vector_db_path,
                "collection_name": self.collection.name if self.collection else None
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            return {"error": str(e)}
    
    def health_check(self) -> Dict[str, Any]:
        """Check the health of the vector store"""
        try:
            # Test basic operations
            test_query = "test query"
            test_results = self.search(test_query, n_results=1)
            
            doc_count = self.get_document_count()
            
            return {
                "status": "healthy",
                "document_count": doc_count,
                "search_functional": True,
                "embedding_model_loaded": self.embedding_model is not None,
                "collection_exists": self.collection is not None
            }
            
        except Exception as e:
            logger.error(f"Vector store health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "document_count": 0,
                "search_functional": False,
                "embedding_model_loaded": False,
                "collection_exists": False
            }

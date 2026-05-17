"""
NVIDIA-powered RAG service using PostgreSQL as a Vector Database.
Handles document embedding, storage, and similarity search for fraud patterns.
"""
import logging
from typing import List, Dict, Any, Optional
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings, ChatNVIDIA
from langchain_postgres.vectorstores import PGVector
from backend.config import NVIDIA_API_KEY, DATABASE_URL_SYNC, NVIDIA_MODEL

logger = logging.getLogger("fraud_detection")

class FraudRAGService:
    """
    Service to handle Retrieval-Augmented Generation (RAG) for fraud detection.
    Uses NVIDIA embeddings and Postgres pgvector.
    """

    def __init__(self):
        # 1. Initialize NVIDIA Embeddings (using a high-quality model)
        self.embeddings = NVIDIAEmbeddings(
            nvidia_api_key=NVIDIA_API_KEY,
            model="nvidia/nv-embedqa-e5-v5" 
        )
        
        # 2. Connect to Postgres Vector Store
        # We use DATABASE_URL_SYNC because pgvector works best with sync connection
        try:
            self.vector_store = PGVector(
                embeddings=self.embeddings,
                collection_name="fraud_knowledge_base",
                connection=DATABASE_URL_SYNC,
                use_jsonb=True,
            )
            logger.info("Successfully connected to Postgres Vector Store.")
        except Exception as e:
            logger.error(f"Failed to connect to Postgres Vector Store: {e}")
            self.vector_store = None

        # 3. Initialize NVIDIA LLM for generation
        self.llm = ChatNVIDIA(
            nvidia_api_key=NVIDIA_API_KEY,
            model=NVIDIA_MODEL,
            temperature=0.2
        )

    def add_knowledge(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None):
        """Add new fraud patterns or case studies to the knowledge base."""
        if not self.vector_store:
            logger.error("Vector store not initialized.")
            return
        
        try:
            self.vector_store.add_texts(texts=texts, metadatas=metadatas)
            logger.info(f"Added {len(texts)} items to knowledge base.")
        except Exception as e:
            logger.error(f"Error adding to knowledge base: {e}")

    def query_similar_patterns(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Retrieve the most relevant fraud patterns for a given transaction query."""
        if not self.vector_store:
            return []
        
        try:
            docs = self.vector_store.similarity_search(query, k=k)
            return [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata
                } for doc in docs
            ]
        except Exception as e:
            logger.error(f"Error querying knowledge base: {e}")
            return []

    async def generate_fraud_analysis(self, transaction_data: Dict[str, Any]) -> str:
        """
        Perform a full RAG analysis: Retrieve similar cases -> Generate explanation.
        """
        # 1. Convert transaction to a searchable string
        query = f"Transaction for {transaction_data.get('amount')} at {transaction_data.get('merchant')}"
        
        # 2. Retrieve similar cases
        similar_cases = self.query_similar_patterns(query)
        context = "\n\n".join([f"Case: {c['content']}" for c in similar_cases])
        
        # 3. Build prompt
        prompt = f"""
        You are an expert fraud investigator. Analyze the following transaction based on our historical fraud knowledge base.
        
        TRANSACTION TO ANALYZE:
        {transaction_data}
        
        HISTORICAL FRAUD CONTEXT:
        {context if context else 'No specific historical matches found.'}
        
        TASK:
        Explain if this transaction matches any known fraud patterns. 
        Provide a risk assessment and recommended action.
        """
        
        # 4. Generate response using NVIDIA LLM
        response = await self.llm.ainvoke(prompt)
        return response.content

# Singleton instance
rag_service = FraudRAGService()

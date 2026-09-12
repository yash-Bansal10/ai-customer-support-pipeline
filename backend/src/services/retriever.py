import json
import os
import faiss
import numpy as np
from pathlib import Path
from typing import List, Dict
from sentence_transformers import SentenceTransformer

from src.models.api_models import HistoricalEvidence

class Retriever:
    """I built this to handle vector search for historical support cases using FAISS."""
    
    def __init__(self, data_path: Path = Path("data/twitter_customer_support/train_conversations.json")):
        self.data_path = data_path
        self.model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        self.top_k = int(os.getenv("RETRIEVAL_TOP_K", "5"))
        
        self.documents = []
        self.index = None
        self.embedder = None
        
    def load_data(self):
        """I load historical conversations and build the FAISS index."""
        print(f"Loading embedding model: {self.model_name}")
        self.embedder = SentenceTransformer(self.model_name)
        
        if not self.data_path.exists():
            print(f"Warning: Data file not found at {self.data_path}. Retriever is empty.")
            return
            
        with open(self.data_path, 'r', encoding='utf-8') as f:
            self.documents = json.load(f)
            
        if not self.documents:
            return
            
        print(f"Embedding {len(self.documents)} historical cases...")
        texts = [doc['customer_message'] for doc in self.documents]
        embeddings = self.embedder.encode(texts, show_progress_bar=True)
        
        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(embeddings)
        print("FAISS index built successfully.")
        
    def retrieve(self, query: str) -> List[HistoricalEvidence]:
        """I embed the user's query and do a nearest-neighbor search to find the most relevant past cases."""
        if not self.index or not self.documents:
            return []
            
        query_emb = self.embedder.encode([query], convert_to_numpy=True)
        distances, indices = self.index.search(query_emb, self.top_k)
        
        results = []
        # distances[0] and indices[0] because we only sent one query
        for dist, idx in zip(distances[0], indices[0]):
            if dist > 1.2:
                continue # Hard relevance threshold to prevent hallucinating on bad evidence
                
            if idx < len(self.documents):
                doc = self.documents[idx]
                results.append(HistoricalEvidence(
                    conversation_id=str(doc.get('conversation_id', idx)),
                    customer_message=doc.get('customer_message', ''),
                    brand_response=doc.get('brand_response', ''),
                    similarity_score=float(dist) # Raw L2 Distance instead of misleading percentage
                ))
        return results

# Singleton instance to avoid reloading models on every request
_retriever_instance = None

def get_retriever() -> Retriever:
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = Retriever()
        _retriever_instance.load_data()
    return _retriever_instance

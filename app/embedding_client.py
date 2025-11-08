# app/embedding_client.py
from sentence_transformers import SentenceTransformer

class EmbeddingClient:
    """
    Local embedding client using SentenceTransformers (fully local, no API required)
    """
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_query(self, query):
        """Embed a single query string"""
        return self.model.encode([query])[0]

    def embed_documents(self, documents):
        """Embed a list of documents (strings)"""
        return self.model.encode(documents)

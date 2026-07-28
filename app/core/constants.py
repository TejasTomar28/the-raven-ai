"""Shared application constants."""

DEFAULT_CHUNK_SIZE = 1000
"""Default maximum number of characters in a RAG chunk."""

DEFAULT_CHUNK_OVERLAP = 200
"""Default number of shared characters between adjacent RAG chunks."""

UPLOAD_CHUNK_SIZE = 1024 * 1024
"""Number of bytes read from an upload per write operation."""

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
"""Sentence-transformers model used to generate document embeddings."""

CHROMA_COLLECTION_NAME = "documents"
"""Name of the ChromaDB collection containing document chunks."""

OLLAMA_REQUEST_TIMEOUT_SECONDS = 60.0
"""Maximum time to wait for a local Ollama generation response."""

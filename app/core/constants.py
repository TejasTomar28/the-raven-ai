"""Shared application constants."""

DEFAULT_CHUNK_SIZE = 1000
"""Default maximum number of characters in a RAG chunk."""

DEFAULT_CHUNK_OVERLAP = 200
"""Default number of shared characters between adjacent RAG chunks."""

UPLOAD_CHUNK_SIZE = 1024 * 1024
"""Number of bytes read from an upload per write operation."""

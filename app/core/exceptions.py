"""Domain exceptions raised by the document service layer."""


class InvalidDocumentError(ValueError):
    """Raised when an uploaded document does not meet validation rules."""


class DuplicateDocumentError(FileExistsError):
    """Raised when an upload would overwrite an existing document."""


class InvalidChunkConfigurationError(ValueError):
    """Raised when chunk size and overlap cannot produce valid chunks."""


class EmbeddingGenerationError(RuntimeError):
    """Raised when document embeddings cannot be generated."""


class VectorStoreError(RuntimeError):
    """Raised when document vectors cannot be persisted."""


class InvalidSearchQueryError(ValueError):
    """Raised when a semantic search query is empty or invalid."""


class NoIndexedDocumentsError(LookupError):
    """Raised when semantic search is requested before documents are indexed."""

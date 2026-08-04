"""Domain exceptions raised by the document service layer."""


class InvalidDocumentError(ValueError):
    """Raised when an uploaded document does not meet validation rules."""


class DuplicateDocumentError(FileExistsError):
    """Raised when an upload would overwrite an existing document."""


class DocumentNotFoundError(FileNotFoundError):
    """Raised when an uploaded document cannot be found."""


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


class OllamaUnavailableError(ConnectionError):
    """Raised when the local Ollama server cannot be reached."""


class LLMGenerationError(RuntimeError):
    """Raised when Ollama returns an invalid or unsuccessful generation response."""


class DocumentMetadataError(RuntimeError):
    """Raised when uploaded-document metadata cannot be persisted."""


class DocumentClassificationError(RuntimeError):
    """Raised when the local ML document classifier cannot classify text."""

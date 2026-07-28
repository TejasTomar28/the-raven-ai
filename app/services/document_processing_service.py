"""Service for indexing uploaded documents in the RAG pipeline."""

from app.core.logging import logger
from app.rag.chunker import chunk_text
from app.rag.embedding import EmbeddingService
from app.rag.parser import extract_text_from_pdf
from app.rag.vector_store import ChromaVectorStore


class DocumentProcessingService:
    """Coordinate parsing, chunking, embedding, and vector persistence."""

    def __init__(
        self,
        embedding_service: EmbeddingService,
    ) -> None:
        """Create a document processing service with its RAG dependencies."""
        self._embedding_service = embedding_service
        self._vector_store: ChromaVectorStore | None = None

    @property
    def vector_store(self) -> ChromaVectorStore:
        """Initialize the persistent vector store only when indexing is requested."""
        if self._vector_store is None:
            self._vector_store = ChromaVectorStore()
        return self._vector_store

    def process_document(self, filename: str) -> int:
        """Index an uploaded document and return the number of stored chunks."""
        logger.info("Extracting text for %s", filename)
        text = extract_text_from_pdf(filename)

        logger.info("Creating chunks for %s", filename)
        chunks = chunk_text(text, source_document=filename)

        embeddings = self._embedding_service.embed_chunks(chunks)
        self.vector_store.store_chunks(filename, chunks, embeddings)

        logger.info("Processing completed for %s: %d chunks", filename, len(chunks))
        return len(chunks)


document_processing_service = DocumentProcessingService(
    embedding_service=EmbeddingService(),
)

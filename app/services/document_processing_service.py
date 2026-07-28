"""Service for indexing uploaded documents in the RAG pipeline."""

from app.core.logging import logger
from app.langchain.vector_store import LangChainVectorStore, get_vector_store
from app.rag.chunker import chunk_text
from app.rag.parser import extract_text_from_pdf


class DocumentProcessingService:
    """Coordinate parsing, chunking, embedding, and vector persistence."""

    def __init__(self) -> None:
        """Create a document processing service with the shared LangChain store."""
        self._vector_store: LangChainVectorStore | None = None

    @property
    def vector_store(self) -> LangChainVectorStore:
        """Return the shared LangChain wrapper for persistent vector storage."""
        if self._vector_store is None:
            self._vector_store = get_vector_store()
        return self._vector_store

    def process_document(self, filename: str) -> int:
        """Index an uploaded document and return the number of stored chunks."""
        logger.info("Extracting text for %s", filename)
        text = extract_text_from_pdf(filename)

        logger.info("Creating chunks for %s", filename)
        chunks = chunk_text(text, source_document=filename)

        self.vector_store.store_chunks(filename, chunks)

        logger.info("Processing completed for %s: %d chunks", filename, len(chunks))
        return len(chunks)


document_processing_service = DocumentProcessingService()

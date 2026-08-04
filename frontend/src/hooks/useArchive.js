import { useCallback, useEffect, useState } from 'react'
import { deleteDocument, fetchDocuments, uploadDocument } from '../services/documents'

/** Manages the uploaded documents visible in the knowledge archive. */
export function useArchive() {
  const [documents, setDocuments] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [isUploading, setIsUploading] = useState(false)
  const [deletingFilename, setDeletingFilename] = useState(null)
  const [error, setError] = useState('')

  const loadDocuments = useCallback(async () => {
    setIsLoading(true)
    setError('')

    try {
      const response = await fetchDocuments()
      setDocuments(response.documents)
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    loadDocuments()
  }, [loadDocuments])

  const archiveDocument = useCallback(async (file) => {
    setIsUploading(true)
    setError('')

    try {
      const response = await uploadDocument(file)
      setDocuments((currentDocuments) => [
        {
          filename: response.filename,
          size_bytes: file.size,
          updated_at: new Date().toISOString(),
          chunks: response.chunks,
          chunk_count: response.chunks,
          category: response.category ?? 'general',
          classifier: response.category ? 'Linear SVM' : 'fallback',
          model_version: 'v1',
          classification_confidence: null,
        },
        ...currentDocuments.filter((document) => document.filename !== response.filename),
      ])
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setIsUploading(false)
    }
  }, [])

  const removeDocument = useCallback(async (filename) => {
    setDeletingFilename(filename)
    setError('')

    try {
      await deleteDocument(filename)
      await loadDocuments()
      return true
    } catch (requestError) {
      setError(requestError.message)
      return false
    } finally {
      setDeletingFilename(null)
    }
  }, [loadDocuments])

  return {
    archiveDocument,
    deletingFilename,
    documents,
    error,
    isLoading,
    isUploading,
    removeDocument,
  }
}

import { apiClient } from './apiClient'

/** Retrieves PDFs currently available in the knowledge archive. */
export function fetchDocuments() {
  return apiClient('/documents')
}

/** Uploads and indexes a PDF through the document processing pipeline. */
export function uploadDocument(file) {
  const formData = new FormData()
  formData.append('file', file)

  return apiClient('/documents/upload', {
    method: 'POST',
    body: formData,
  })
}

/** Permanently removes an uploaded document and its indexed vectors. */
export function deleteDocument(filename) {
  return apiClient(`/documents/${encodeURIComponent(filename)}`, {
    method: 'DELETE',
  })
}

/** Retrieves ranked passages to use as answer citations. */
export function searchDocuments(query) {
  return apiClient('/documents/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  })
}

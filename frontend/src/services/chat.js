import { apiClient } from './apiClient'

/** Requests a grounded answer from the RAVEN AI chat endpoint. */
export function askArchiveQuestion(question) {
  return apiClient('/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  })
}

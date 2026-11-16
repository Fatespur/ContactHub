import request from './request'
import * as mock from './mock'

/**
 * When VITE_USE_MOCK=false is explicitly set, requests are sent to the real backend.
 * When unset, development mode defaults to Mock data, while production builds
 * (vite build) default to the real backend to prevent accidental mock usage in production.
 */
export const isMockMode = import.meta.env.VITE_USE_MOCK
  ? import.meta.env.VITE_USE_MOCK !== 'false'
  : !import.meta.env.PROD

export function listContacts(params = {}) {
  return isMockMode ? mock.listContacts(params) : request.get('/contacts', { params })
}

export function getContact(id) {
  return isMockMode ? mock.getContact(id) : request.get(`/contacts/${id}`)
}

export function createContact(payload) {
  return isMockMode ? mock.createContact(payload) : request.post('/contacts', payload)
}

export function updateContact(id, payload) {
  return isMockMode ? mock.updateContact(id, payload) : request.put(`/contacts/${id}`, payload)
}

export function deleteContact(id) {
  return isMockMode ? mock.deleteContact(id) : request.delete(`/contacts/${id}`)
}

export function updateFavorite(id, isFavorite) {
  return isMockMode
    ? mock.updateFavorite(id, isFavorite)
    : request.patch(`/contacts/${id}/favorite`, { is_favorite: isFavorite })
}

export function importContacts(file, { onUploadProgress, signal } = {}) {
  if (isMockMode) {
    return mock.importContacts(file, { onProgress: onUploadProgress, signal })
  }
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/contacts/import', formData, {
    timeout: 60000,
    signal,
    onUploadProgress: (event) => {
      if (!onUploadProgress) return
      const total = event.total || file.size || 1
      onUploadProgress(Math.min(100, Math.round((event.loaded / total) * 100)))
    }
  })
}

export function exportContacts(params = {}) {
  return request.get('/contacts/export', { params, responseType: 'blob' })
}

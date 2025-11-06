/**
 * Utility functions
 */
import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

/**
 * Merge Tailwind CSS classes
 */
export function cn(...inputs) {
  return twMerge(clsx(inputs))
}

/**
 * Format file size
 */
export function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

/**
 * Format duration
 */
export function formatDuration(seconds) {
  if (seconds < 60) {
    return `${seconds.toFixed(1)}s`
  } else if (seconds < 3600) {
    const minutes = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${minutes}m ${secs}s`
  } else {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return `${hours}h ${minutes}m`
  }
}

/**
 * Format date
 */
export function formatDate(date) {
  if (!date) return 'N/A'
  
  const d = new Date(date)
  return d.toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

/**
 * Format number with commas
 */
export function formatNumber(num) {
  return num.toLocaleString('es-ES')
}

/**
 * Truncate text
 */
export function truncate(str, length = 50) {
  if (!str) return ''
  if (str.length <= length) return str
  return str.substring(0, length) + '...'
}

/**
 * Get status color
 */
export function getStatusColor(status) {
  const colors = {
    pending: 'bg-yellow-100 text-yellow-800',
    running: 'bg-blue-100 text-blue-800',
    completed: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800',
    cancelled: 'bg-gray-100 text-gray-800',
  }
  return colors[status] || colors.pending
}

/**
 * Download file from blob
 */
export function downloadBlob(blob, filename) {
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  window.URL.revokeObjectURL(url)
  document.body.removeChild(a)
}

/**
 * Parse error message
 */
export function parseError(error) {
  if (error.response?.data?.detail) {
    return error.response.data.detail
  }
  if (error.response?.data?.message) {
    return error.response.data.message
  }
  if (error.message) {
    return error.message
  }
  return 'An unknown error occurred'
}

/**
 * Validate image file
 */
export function isValidImageFile(file) {
  const validTypes = ['image/jpeg', 'image/png', 'image/jpg', 'image/bmp', 'image/webp']
  return validTypes.includes(file.type)
}

/**
 * Get confidence color
 */
export function getConfidenceColor(confidence) {
  if (confidence >= 0.8) return 'text-green-600'
  if (confidence >= 0.6) return 'text-yellow-600'
  return 'text-orange-600'
}

/**
 * Calculate progress percentage
 */
export function calculateProgress(current, total) {
  if (total === 0) return 0
  return Math.round((current / total) * 100)
}

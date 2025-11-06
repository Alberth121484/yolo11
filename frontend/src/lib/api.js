/**
 * API client for YOLO11 backend
 */
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Health endpoints
export const healthAPI = {
  check: () => api.get('/health'),
  info: () => api.get('/info'),
}

// Inference endpoints
export const inferenceAPI = {
  predictSingle: (formData) => 
    api.post('/predict', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),
  
  predictBatch: (formData) =>
    api.post('/predict/batch', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),
  
  predictFromUrl: (data) => api.post('/predict/url', data),
  
  getResult: (filename) => api.get(`/result/${filename}`, {
    responseType: 'blob'
  }),
}

// Training endpoints
export const trainingAPI = {
  startTraining: (config) => api.post('/train', config),
  getJob: (jobId) => api.get(`/train/${jobId}`),
  listJobs: (params) => api.get('/train', { params }),
  cancelJob: (jobId) => api.delete(`/train/${jobId}`),
  getMetrics: (jobId) => api.get(`/train/${jobId}/metrics`),
  resumeJob: (jobId) => api.post(`/train/${jobId}/resume`),
}

// Dataset endpoints
export const datasetAPI = {
  create: (data) => api.post('/datasets', data),
  list: () => api.get('/datasets'),
  get: (name) => api.get(`/datasets/${name}`),
  delete: (name) => api.delete(`/datasets/${name}`),
  
  addImages: (name, formData) =>
    api.post(`/datasets/${name}/images`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),
  
  addAnnotatedImage: (name, formData) =>
    api.post(`/datasets/${name}/images/annotated`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),
  
  split: (name, data) => api.post(`/datasets/${name}/split`, data),
  validate: (name) => api.get(`/datasets/${name}/validate`),
  export: (name, format) => api.get(`/datasets/${name}/export`, {
    params: { format },
    responseType: 'blob'
  }),
}

// Model endpoints
export const modelAPI = {
  list: () => api.get('/models'),
  get: (name) => api.get(`/models/${name}`),
  download: (name) => api.get(`/models/${name}/download`, {
    responseType: 'blob'
  }),
  upload: (formData) =>
    api.post('/models/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),
  delete: (name) => api.delete(`/models/${name}`),
  export: (name, format) => api.post(`/models/${name}/export`, { format }),
  validate: (name, datasetName) =>
    api.post(`/models/${name}/validate`, { dataset_name: datasetName }),
}

export default api

import axios from 'axios'
import type {
  User,
  Invoice,
  CreateUserRequest,
  CreateInvoiceRequest,
  UpdateUserRequest,
  UpdateInvoiceRequest,
  PaginatedResponse,
  InvoiceFilters,
  ExportResponse
} from '../types'

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Users API
export const usersApi = {
  getAll: async (skip = 0, limit = 100): Promise<User[]> => {
    const response = await api.get('/users/', { params: { skip, limit } })
    return response.data
  },

  getById: async (id: number): Promise<User> => {
    const response = await api.get(`/users/${id}`)
    return response.data
  },

  create: async (user: CreateUserRequest): Promise<User> => {
    const response = await api.post('/users/', user)
    return response.data
  },

  update: async (id: number, user: UpdateUserRequest): Promise<User> => {
    const response = await api.put(`/users/${id}`, user)
    return response.data
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/users/${id}`)
  },
}

// Invoices API
export const invoicesApi = {
  getAll: async (filters: InvoiceFilters = {}): Promise<PaginatedResponse<Invoice>> => {
    const response = await api.get('/invoices/', { params: filters })
    return response.data
  },

  getById: async (id: number): Promise<Invoice> => {
    const response = await api.get(`/invoices/${id}`)
    return response.data
  },

  create: async (invoice: CreateInvoiceRequest, file?: File): Promise<Invoice> => {
    const formData = new FormData()
    
    // Agregar campos del formulario
    Object.entries(invoice).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        // Convertir fecha a formato ISO datetime
        if (key === 'date' && typeof value === 'string') {
          formData.append(key, `${value}T00:00:00`)
        } else {
          formData.append(key, value.toString())
        }
      }
    })
    
    // Agregar archivo si existe
    if (file) {
      formData.append('file', file)
    }

    const response = await api.post('/invoices/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  update: async (id: number, invoice: UpdateInvoiceRequest): Promise<Invoice> => {
    const response = await api.put(`/invoices/${id}`, invoice)
    return response.data
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/invoices/${id}`)
  },

  export: async (filters: Partial<InvoiceFilters> = {}): Promise<ExportResponse> => {
    const response = await api.get('/invoices/export/excel', { params: filters })
    return response.data
  },

  validate: async (id: number, status: string, notes?: string): Promise<Invoice> => {
    const formData = new FormData()
    formData.append('new_status', status)
    if (notes) {
      formData.append('validation_notes', notes)
    }
    
    const response = await api.patch(`/invoices/${id}/validate`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

}

export default api

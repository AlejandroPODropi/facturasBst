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

// Dashboard API
const dashboardApiBase = {
  getStats: async (): Promise<any> => {
    const response = await api.get('/dashboard/stats')
    return response.data
  },

  getBasicStats: async (): Promise<any> => {
    const response = await api.get('/dashboard/basic-stats')
    return response.data
  },

  getTrends: async (months: number = 6): Promise<any> => {
    const response = await api.get(`/dashboard/trends?months=${months}`)
    return response.data
  },

  getUserStats: async (limit: number = 10): Promise<any> => {
    const response = await api.get(`/dashboard/user-stats?limit=${limit}`)
    return response.data
  },

  getCategoryDistribution: async (): Promise<any> => {
    const response = await api.get('/dashboard/category-distribution')
    return response.data
  },

  getPaymentMethodDistribution: async (): Promise<any> => {
    const response = await api.get('/dashboard/payment-method-distribution')
    return response.data
  },

  getValidationPerformance: async (): Promise<any> => {
    const response = await api.get('/dashboard/validation-performance')
    return response.data
  },

  getRecentActivity: async (limit: number = 10): Promise<any> => {
    const response = await api.get(`/dashboard/recent-activity?limit=${limit}`)
    return response.data
  },
}

// Gmail API
export const gmailApi = {
  getAuthStatus: async (): Promise<any> => {
    const response = await api.get('/gmail/auth/status')
    return response.data
  },

  authenticate: async (code?: string): Promise<any> => {
    if (code) {
      const response = await api.post(`/gmail/auth/callback?code=${encodeURIComponent(code)}`)
      return response.data
    } else {
      const response = await api.post('/gmail/auth/authenticate')
      return response.data
    }
  },

  getAuthUrl: async (): Promise<any> => {
    const response = await api.get('/gmail/auth/url')
    return response.data
  },

  getSimpleAuthUrl: async (): Promise<any> => {
    const response = await api.get('/gmail/auth/simple')
    return response.data
  },

  getManualAuthInstructions: async (): Promise<any> => {
    const response = await api.get('/gmail/auth/manual')
    return response.data
  },

  searchEmails: async (query: string = "has:attachment newer_than:7d", maxResults: number = 10): Promise<any> => {
    const response = await api.get(`/gmail/emails/search?query=${encodeURIComponent(query)}&max_results=${maxResults}`)
    return response.data
  },

  getEmailDetails: async (messageId: string): Promise<any> => {
    const response = await api.get(`/gmail/emails/${messageId}`)
    return response.data
  },

  processInvoices: async (limit: number = 10): Promise<any> => {
    const response = await api.post(`/gmail/process-invoices/sync?limit=${limit}`)
    return response.data
  },

  downloadAttachment: async (messageId: string, attachmentId: string): Promise<any> => {
    const response = await api.get(`/gmail/attachments/${messageId}/${attachmentId}`)
    return response.data
  },

  markAsRead: async (messageId: string): Promise<any> => {
    const response = await api.post(`/gmail/emails/${messageId}/mark-read`)
    return response.data
  },

  getStats: async (): Promise<any> => {
    const response = await api.get('/gmail/stats')
    return response.data
  },
}

// OCR API
export const ocrApi = {
  processInvoice: async (file: File, userId: number): Promise<any> => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('user_id', userId.toString())
    const response = await api.post('/ocr/process', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  processAndCreateInvoice: async (
    file: File, 
    userId: number, 
    paymentMethod: string, 
    category: string, 
    description?: string
  ): Promise<any> => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('user_id', userId.toString())
    formData.append('payment_method', paymentMethod)
    formData.append('category', category)
    if (description) {
      formData.append('description', description)
    }
    const response = await api.post('/ocr/process-and-create', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  getSupportedFormats: async (): Promise<any> => {
    const response = await api.get('/ocr/supported-formats')
    return response.data
  },

  getInvoiceOCRData: async (invoiceId: number): Promise<any> => {
    const response = await api.get(`/ocr/invoice/${invoiceId}/ocr-data`)
    return response.data
  },

  validateExtraction: async (ocrData: any): Promise<any> => {
    const response = await api.post('/ocr/validate-extraction', ocrData)
    return response.data
  },
}

// Dashboard API extendido con funciones de Gmail
export const dashboardApi = {
  ...dashboardApiBase,
  getGmailStats: gmailApi.getStats,
  getGmailAuthStatus: gmailApi.getAuthStatus,
  authenticateGmail: gmailApi.authenticate,
  getGmailAuthUrl: gmailApi.getAuthUrl,
  getGmailSimpleAuthUrl: gmailApi.getSimpleAuthUrl,
  getGmailManualAuthInstructions: gmailApi.getManualAuthInstructions,
  processGmailInvoices: gmailApi.processInvoices,
}

export default api

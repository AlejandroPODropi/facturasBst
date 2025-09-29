import { useQuery, useMutation, useQueryClient } from 'react-query'
import { usersApi, invoicesApi } from '../services/api'
import type { 
  CreateUserRequest, 
  CreateInvoiceRequest,
  UpdateUserRequest,
  UpdateInvoiceRequest,
  InvoiceFilters
} from '../types'

// Hooks para usuarios
export const useUsers = () => {
  return useQuery('users', () => usersApi.getAll())
}

export const useUser = (id: number) => {
  return useQuery(['user', id], () => usersApi.getById(id), {
    enabled: !!id
  })
}

export const useCreateUser = () => {
  const queryClient = useQueryClient()
  
  return useMutation((user: CreateUserRequest) => usersApi.create(user), {
    onSuccess: () => {
      queryClient.invalidateQueries('users')
    }
  })
}

export const useUpdateUser = () => {
  const queryClient = useQueryClient()
  
  return useMutation(
    ({ id, user }: { id: number; user: UpdateUserRequest }) => 
      usersApi.update(id, user),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('users')
      }
    }
  )
}

export const useDeleteUser = () => {
  const queryClient = useQueryClient()
  
  return useMutation((id: number) => usersApi.delete(id), {
    onSuccess: () => {
      queryClient.invalidateQueries('users')
    }
  })
}

// Hooks para facturas
export const useInvoices = (filters?: InvoiceFilters) => {
  return useQuery(['invoices', filters], () => invoicesApi.getAll(filters))
}

export const useInvoice = (id: number) => {
  return useQuery(['invoice', id], () => invoicesApi.getById(id), {
    enabled: !!id
  })
}

export const useCreateInvoice = () => {
  const queryClient = useQueryClient()
  
  return useMutation(
    ({ invoice, file }: { invoice: CreateInvoiceRequest; file?: File }) => 
      invoicesApi.create(invoice, file),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('invoices')
      }
    }
  )
}

export const useUpdateInvoice = () => {
  const queryClient = useQueryClient()
  
  return useMutation(
    ({ id, invoice }: { id: number; invoice: UpdateInvoiceRequest }) => 
      invoicesApi.update(id, invoice),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('invoices')
      }
    }
  )
}

export const useDeleteInvoice = () => {
  const queryClient = useQueryClient()
  
  return useMutation((id: number) => invoicesApi.delete(id), {
    onSuccess: () => {
      queryClient.invalidateQueries('invoices')
    }
  })
}

export const useExportInvoices = () => {
  return useMutation((filters?: Partial<InvoiceFilters>) => 
    invoicesApi.export(filters)
  )
}

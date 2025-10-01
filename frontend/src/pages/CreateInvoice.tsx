import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { useNavigate } from 'react-router-dom'
import { invoicesApi, usersApi } from '../services/api'
import { 
  PaymentMethod, 
  ExpenseCategory, 
  PAYMENT_METHOD_LABELS, 
  EXPENSE_CATEGORY_LABELS 
} from '../types'
import { Save, Upload } from 'lucide-react'

export function CreateInvoice() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  
  const [formData, setFormData] = useState({
    date: '',
    provider: '',
    amount: '',
    payment_method: PaymentMethod.CASH,
    category: ExpenseCategory.OTHER,
    user_id: '',
    description: '',
    nit: '',
  })
  const [file, setFile] = useState<File | null>(null)

  const { data: users = [] } = useQuery('users', () => usersApi.getAll())

  const createInvoiceMutation = useMutation(
    (data: any) => invoicesApi.create(data, file || undefined),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('invoices')
        navigate('/invoices')
      },
      onError: (error) => {
        console.error('Error al crear factura:', error)
        alert('Error al crear la factura')
      },
    }
  )

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.user_id) {
      alert('Por favor selecciona un usuario')
      return
    }

    createInvoiceMutation.mutate({
      ...formData,
      user_id: parseInt(formData.user_id),
      amount: parseFloat(formData.amount),
    })
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
    }
  }

  return (
    <div className="space-y-4 lg:space-y-6">
      <div>
        <h1 className="text-xl lg:text-2xl font-bold text-gray-900">Nueva Factura</h1>
        <p className="mt-1 text-sm text-gray-500">
          Registra una nueva factura en el sistema
        </p>
      </div>

      <div className="card">
        <div className="card-header">
          <h3 className="text-base lg:text-lg font-medium text-gray-900">Información de la Factura</h3>
        </div>
        <div className="card-content">
          <form onSubmit={handleSubmit} className="space-y-4 lg:space-y-6">
            <div className="grid grid-cols-1 gap-4 lg:gap-6 lg:grid-cols-2">
              <div>
                <label htmlFor="date" className="block text-sm font-medium text-gray-700">
                  Fecha de la Factura *
                </label>
                <input
                  type="date"
                  id="date"
                  name="date"
                  value={formData.date}
                  onChange={handleInputChange}
                  required
                  className="input mt-1"
                />
              </div>

              <div>
                <label htmlFor="user_id" className="block text-sm font-medium text-gray-700">
                  Usuario *
                </label>
                <select
                  id="user_id"
                  name="user_id"
                  value={formData.user_id}
                  onChange={handleInputChange}
                  required
                  className="input mt-1"
                >
                  <option value="">Selecciona un usuario</option>
                  {users.map((user) => (
                    <option key={user.id} value={user.id}>
                      {user.name} ({user.email})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label htmlFor="provider" className="block text-sm font-medium text-gray-700">
                  Proveedor *
                </label>
                <input
                  type="text"
                  id="provider"
                  name="provider"
                  value={formData.provider}
                  onChange={handleInputChange}
                  required
                  className="input mt-1"
                  placeholder="Nombre del proveedor"
                />
              </div>

              <div>
                <label htmlFor="nit" className="block text-sm font-medium text-gray-700">
                  NIT
                </label>
                <input
                  type="text"
                  id="nit"
                  name="nit"
                  value={formData.nit}
                  onChange={handleInputChange}
                  className="input mt-1"
                  placeholder="Número de identificación tributaria"
                />
              </div>

              <div>
                <label htmlFor="amount" className="block text-sm font-medium text-gray-700">
                  Monto *
                </label>
                <input
                  type="number"
                  id="amount"
                  name="amount"
                  value={formData.amount}
                  onChange={handleInputChange}
                  required
                  min="0"
                  step="0.01"
                  className="input mt-1"
                  placeholder="0.00"
                />
              </div>

              <div>
                <label htmlFor="payment_method" className="block text-sm font-medium text-gray-700">
                  Método de Pago *
                </label>
                <select
                  id="payment_method"
                  name="payment_method"
                  value={formData.payment_method}
                  onChange={handleInputChange}
                  required
                  className="input mt-1"
                >
                  {Object.entries(PAYMENT_METHOD_LABELS).map(([key, label]) => (
                    <option key={key} value={key}>
                      {label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label htmlFor="category" className="block text-sm font-medium text-gray-700">
                  Categoría *
                </label>
                <select
                  id="category"
                  name="category"
                  value={formData.category}
                  onChange={handleInputChange}
                  required
                  className="input mt-1"
                >
                  {Object.entries(EXPENSE_CATEGORY_LABELS).map(([key, label]) => (
                    <option key={key} value={key}>
                      {label}
                    </option>
                  ))}
                </select>
              </div>
              </div>

            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                Descripción
              </label>
              <textarea
                id="description"
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                rows={3}
                className="input mt-1"
                placeholder="Descripción adicional (opcional)"
              />
            </div>

            <div>
              <label htmlFor="file" className="block text-sm font-medium text-gray-700">
                Archivo Adjunto
              </label>
              <div className="mt-1 flex justify-center px-4 lg:px-6 pt-4 lg:pt-5 pb-4 lg:pb-6 border-2 border-gray-300 border-dashed rounded-md">
                <div className="space-y-1 text-center">
                  <Upload className="mx-auto h-8 w-8 lg:h-12 lg:w-12 text-gray-400" />
                  <div className="flex flex-col sm:flex-row text-sm text-gray-600">
                    <label
                      htmlFor="file"
                      className="relative cursor-pointer bg-white rounded-md font-medium text-primary-600 hover:text-primary-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-primary-500"
                    >
                      <span>Subir archivo</span>
                      <input
                        id="file"
                        name="file"
                        type="file"
                        className="sr-only"
                        onChange={handleFileChange}
                        accept=".pdf,.jpg,.jpeg,.png,.xlsx,.xls"
                      />
                    </label>
                    <p className="sm:pl-1">o arrastra y suelta</p>
                  </div>
                  <p className="text-xs text-gray-500">PDF, JPG, PNG, Excel hasta 10MB</p>
                  {file && (
                    <p className="text-sm text-green-600 truncate">Archivo: {file.name}</p>
                  )}
                </div>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row justify-end space-y-3 sm:space-y-0 sm:space-x-3 pt-4">
              <button
                type="button"
                onClick={() => navigate('/invoices')}
                className="btn btn-secondary w-full sm:w-auto"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={createInvoiceMutation.isLoading}
                className="btn btn-primary w-full sm:w-auto"
              >
                {createInvoiceMutation.isLoading ? (
                  'Guardando...'
                ) : (
                  <>
                    <Save className="h-4 w-4 mr-2 inline" />
                    Guardar Factura
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
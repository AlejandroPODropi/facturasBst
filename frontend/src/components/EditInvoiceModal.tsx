import { useState, useEffect } from 'react'
import { useMutation, useQueryClient } from 'react-query'
import { invoicesApi, usersApi } from '../services/api'
import { X, Save, AlertCircle } from 'lucide-react'
import { Invoice, PaymentMethod, ExpenseCategory } from '../types'
import { PAYMENT_METHOD_LABELS, EXPENSE_CATEGORY_LABELS } from '../types'

interface EditInvoiceModalProps {
  invoice: Invoice | null
  isOpen: boolean
  onClose: () => void
}

export function EditInvoiceModal({ invoice, isOpen, onClose }: EditInvoiceModalProps) {
  const queryClient = useQueryClient()
  const [formData, setFormData] = useState({
    date: '',
    provider: '',
    amount: '',
    payment_method: '' as PaymentMethod,
    category: '' as ExpenseCategory,
    description: '',
    user_id: 0
  })

  const { data: users = [] } = useQueryClient().getQueryData('users') as any

  useEffect(() => {
    if (invoice) {
      setFormData({
        date: invoice.date ? new Date(invoice.date).toISOString().split('T')[0] : '',
        provider: invoice.provider || '',
        amount: invoice.amount?.toString() || '',
        payment_method: invoice.payment_method || 'efectivo',
        category: invoice.category || 'otros',
        description: invoice.description || '',
        user_id: invoice.user_id || 0
      })
    }
  }, [invoice])

  const updateInvoiceMutation = useMutation(
    (data: any) => invoicesApi.update(invoice!.id, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['invoices'])
        onClose()
      },
      onError: (error: any) => {
        console.error('Error actualizando factura:', error)
        alert('Error al actualizar la factura')
      }
    }
  )

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: name === 'amount' ? parseFloat(value) || 0 : value
    }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.provider || !formData.amount || formData.amount <= 0) {
      alert('Por favor completa todos los campos requeridos')
      return
    }

    updateInvoiceMutation.mutate({
      date: new Date(formData.date),
      provider: formData.provider,
      amount: formData.amount,
      payment_method: formData.payment_method,
      category: formData.category,
      description: formData.description,
      user_id: formData.user_id
    })
  }

  if (!isOpen || !invoice) return null

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={onClose}></div>

        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">
                Editar Factura #{invoice.id}
              </h3>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-6 w-6" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
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
                    {Object.entries(PAYMENT_METHOD_LABELS).map(([value, label]) => (
                      <option key={value} value={value}>
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
                    {Object.entries(EXPENSE_CATEGORY_LABELS).map(([value, label]) => (
                      <option key={value} value={value}>
                        {label}
                      </option>
                    ))}
                  </select>
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
                    <option value="">Seleccionar usuario</option>
                    {users.map((user: any) => (
                      <option key={user.id} value={user.id}>
                        {user.name}
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

              {updateInvoiceMutation.error && (
                <div className="flex items-center space-x-2 text-red-600 text-sm">
                  <AlertCircle className="h-4 w-4" />
                  <span>Error al actualizar la factura</span>
                </div>
              )}

              <div className="flex flex-col md:flex-row justify-end space-y-3 md:space-y-0 md:space-x-3 pt-4">
                <button
                  type="button"
                  onClick={onClose}
                  className="btn-mobile btn-secondary w-full md:w-auto"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={updateInvoiceMutation.isLoading}
                  className="btn-mobile btn-primary w-full md:w-auto"
                >
                  {updateInvoiceMutation.isLoading ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Guardando...
                    </>
                  ) : (
                    <>
                      <Save className="h-4 w-4 mr-2" />
                      Guardar Cambios
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}

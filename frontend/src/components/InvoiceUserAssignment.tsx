import React, { useState } from 'react'
import { useMutation, useQueryClient } from 'react-query'
import { invoicesApi } from '../services/api'
import type { 
  InvoiceAnalysisResult, 
  User,
  PaymentMethod,
  ExpenseCategory
} from '../types'
import { 
  PAYMENT_METHOD_LABELS,
  EXPENSE_CATEGORY_LABELS
} from '../types'
import { 
  User as UserIcon,
  Save,
  X,
  AlertCircle,
  CheckCircle,
  Loader2
} from 'lucide-react'

interface InvoiceUserAssignmentProps {
  invoice: InvoiceAnalysisResult
  users: User[]
  onSave: (invoice: InvoiceAnalysisResult, userId: number, paymentMethod: PaymentMethod, category: ExpenseCategory) => void
  onCancel: () => void
}

export function InvoiceUserAssignment({ 
  invoice, 
  users, 
  onSave, 
  onCancel 
}: InvoiceUserAssignmentProps) {
  const [selectedUserId, setSelectedUserId] = useState<number | ''>('')
  const [paymentMethod, setPaymentMethod] = useState<PaymentMethod>('EFECTIVO')
  const [category, setCategory] = useState<ExpenseCategory>('OTHER')
  const [isSaving, setIsSaving] = useState(false)

  const handleSave = async () => {
    if (!selectedUserId) {
      alert('Por favor, selecciona un usuario')
      return
    }

    setIsSaving(true)
    try {
      onSave(invoice, Number(selectedUserId), paymentMethod, category)
    } catch (error) {
      console.error('Error al asignar usuario:', error)
      alert('Error al asignar usuario. Por favor, inténtalo de nuevo.')
    } finally {
      setIsSaving(false)
    }
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0
    }).format(amount)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('es-CO')
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">
              Asignar Usuario a Factura
            </h3>
            <button
              onClick={onCancel}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          {/* Información de la factura */}
          <div className="bg-gray-50 rounded-lg p-4 mb-6">
            <h4 className="font-medium text-gray-900 mb-3">Información de la Factura</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-600">Proveedor:</span>
                <div className="font-medium">{invoice.provider}</div>
              </div>
              <div>
                <span className="text-gray-600">Monto:</span>
                <div className="font-medium">{formatCurrency(invoice.amount)}</div>
              </div>
              <div>
                <span className="text-gray-600">Fecha:</span>
                <div className="font-medium">{formatDate(invoice.date)}</div>
              </div>
              <div>
                <span className="text-gray-600">Remitente:</span>
                <div className="font-medium">{invoice.email_from}</div>
              </div>
              <div className="md:col-span-2">
                <span className="text-gray-600">Asunto:</span>
                <div className="font-medium">{invoice.email_subject}</div>
              </div>
            </div>
          </div>

          {/* Formulario de asignación */}
          <div className="space-y-4">
            {/* Selección de usuario */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Usuario *
              </label>
              <select
                value={selectedUserId}
                onChange={(e) => setSelectedUserId(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="">Selecciona un usuario</option>
                {users.map(user => (
                  <option key={user.id} value={user.id}>
                    {user.name} ({user.email})
                  </option>
                ))}
              </select>
            </div>

            {/* Método de pago */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Método de Pago
              </label>
              <select
                value={paymentMethod}
                onChange={(e) => setPaymentMethod(e.target.value as PaymentMethod)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {Object.values(PaymentMethod).map((method) => (
                  <option key={method} value={method}>
                    {PAYMENT_METHOD_LABELS[method as PaymentMethod]}
                  </option>
                ))}
              </select>
            </div>

            {/* Categoría */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Categoría
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value as ExpenseCategory)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {Object.values(ExpenseCategory).map((category) => (
                  <option key={category} value={category}>
                    {EXPENSE_CATEGORY_LABELS[category as ExpenseCategory]}
                  </option>
                ))}
              </select>
            </div>

            {/* Descripción */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Descripción (opcional)
              </label>
              <textarea
                value={invoice.description || ''}
                readOnly
                className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-600"
                rows={3}
                placeholder="Descripción extraída automáticamente del email"
              />
            </div>
          </div>

          {/* Botones */}
          <div className="flex items-center justify-end gap-3 mt-6 pt-4 border-t">
            <button
              onClick={onCancel}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
            >
              Cancelar
            </button>
            <button
              onClick={handleSave}
              disabled={!selectedUserId || isSaving}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {isSaving ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Save className="h-4 w-4" />
              )}
              {isSaving ? 'Guardando...' : 'Asignar y Guardar'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

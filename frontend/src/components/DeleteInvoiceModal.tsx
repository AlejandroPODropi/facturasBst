import { useMutation, useQueryClient } from 'react-query'
import { invoicesApi } from '../services/api'
import { X, Trash2, AlertTriangle } from 'lucide-react'
import { Invoice } from '../types'

interface DeleteInvoiceModalProps {
  invoice: Invoice | null
  isOpen: boolean
  onClose: () => void
}

export function DeleteInvoiceModal({ invoice, isOpen, onClose }: DeleteInvoiceModalProps) {
  const queryClient = useQueryClient()

  const deleteInvoiceMutation = useMutation(
    (id: number) => invoicesApi.delete(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['invoices'])
        onClose()
      },
      onError: (error: any) => {
        console.error('Error eliminando factura:', error)
        alert('Error al eliminar la factura')
      }
    }
  )

  const handleDelete = () => {
    if (invoice) {
      deleteInvoiceMutation.mutate(invoice.id)
    }
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
                Eliminar Factura
              </h3>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-6 w-6" />
              </button>
            </div>

            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0">
                <AlertTriangle className="h-6 w-6 text-red-600" />
              </div>
              <div className="flex-1">
                <p className="text-sm text-gray-700 mb-4">
                  ¿Estás seguro de que quieres eliminar esta factura? Esta acción no se puede deshacer.
                </p>
                
                <div className="bg-gray-50 rounded-lg p-4 mb-4">
                  <h4 className="font-medium text-gray-900 mb-2">Detalles de la factura:</h4>
                  <div className="text-sm text-gray-600 space-y-1">
                    <p><strong>ID:</strong> #{invoice.id}</p>
                    <p><strong>Proveedor:</strong> {invoice.provider}</p>
                    <p><strong>Monto:</strong> ${invoice.amount?.toLocaleString()}</p>
                    <p><strong>Fecha:</strong> {invoice.date ? new Date(invoice.date).toLocaleDateString() : 'N/A'}</p>
                    <p><strong>Estado:</strong> {invoice.status}</p>
                  </div>
                </div>
              </div>
            </div>

            {deleteInvoiceMutation.error && (
              <div className="flex items-center space-x-2 text-red-600 text-sm mb-4">
                <AlertTriangle className="h-4 w-4" />
                <span>Error al eliminar la factura</span>
              </div>
            )}

            <div className="flex flex-col md:flex-row justify-end space-y-3 md:space-y-0 md:space-x-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="btn-mobile btn-secondary w-full md:w-auto"
                disabled={deleteInvoiceMutation.isLoading}
              >
                Cancelar
              </button>
              <button
                type="button"
                onClick={handleDelete}
                disabled={deleteInvoiceMutation.isLoading}
                className="btn-mobile bg-red-600 hover:bg-red-700 text-white w-full md:w-auto"
              >
                {deleteInvoiceMutation.isLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Eliminando...
                  </>
                ) : (
                  <>
                    <Trash2 className="h-4 w-4 mr-2" />
                    Eliminar Factura
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

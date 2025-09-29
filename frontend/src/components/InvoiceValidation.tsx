import { useState } from 'react'
import { useMutation, useQueryClient, useQuery } from 'react-query'
import { invoicesApi } from '../services/api'
import { InvoiceStatus, INVOICE_STATUS_LABELS, PAYMENT_METHOD_LABELS, EXPENSE_CATEGORY_LABELS } from '../types'
import { CheckCircle, XCircle, FileText, Image, FileSpreadsheet, Download } from 'lucide-react'

interface InvoiceValidationProps {
  invoiceId: number
  currentStatus: InvoiceStatus
  onClose: () => void
}

export function InvoiceValidation({ invoiceId, currentStatus, onClose }: InvoiceValidationProps) {
  const [selectedStatus, setSelectedStatus] = useState<InvoiceStatus | null>(null)
  const [notes, setNotes] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const queryClient = useQueryClient()

  // Obtener datos de la factura
  const { data: invoice, isLoading } = useQuery(
    ['invoice', invoiceId],
    () => invoicesApi.getById(invoiceId),
    {
      enabled: !!invoiceId
    }
  )

  const validateMutation = useMutation(
    ({ status, notes }: { status: string; notes?: string }) =>
      invoicesApi.validate(invoiceId, status, notes),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('invoices')
        onClose()
      },
      onError: (error) => {
        console.error('Error al validar factura:', error)
        alert('Error al validar la factura')
      },
    }
  )

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!selectedStatus) {
      alert('Por favor selecciona un estado')
      return
    }

    setIsSubmitting(true)
    try {
      await validateMutation.mutateAsync({
        status: selectedStatus,
        notes: notes.trim() || undefined
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  // Función para obtener la URL del archivo
  const getFileUrl = () => {
    return `${(import.meta as any).env.VITE_API_URL || 'http://localhost:8000/api/v1'}/invoices/${invoiceId}/download`
  }

  // Función para determinar el tipo de archivo
  const getFileType = (filePath: string) => {
    const extension = filePath.split('.').pop()?.toLowerCase()
    switch (extension) {
      case 'pdf':
        return 'pdf'
      case 'jpg':
      case 'jpeg':
      case 'png':
        return 'image'
      case 'xlsx':
      case 'xls':
        return 'excel'
      case 'csv':
        return 'csv'
      default:
        return 'unknown'
    }
  }

  // Función para obtener el icono del archivo
  const getFileIcon = (filePath: string) => {
    const fileType = getFileType(filePath)
    switch (fileType) {
      case 'pdf':
        return <FileText className="h-5 w-5 text-red-500" />
      case 'image':
        return <Image className="h-5 w-5 text-blue-500" />
      case 'excel':
      case 'csv':
        return <FileSpreadsheet className="h-5 w-5 text-green-500" />
      default:
        return <FileText className="h-5 w-5 text-gray-500" />
    }
  }

  if (isLoading) {
    return (
      <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full flex justify-center items-center">
        <div className="bg-white p-8 rounded-lg shadow-xl">
          <div className="text-center">Cargando factura...</div>
        </div>
      </div>
    )
  }

  if (!invoice) {
    return (
      <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full flex justify-center items-center">
        <div className="bg-white p-8 rounded-lg shadow-xl">
          <div className="text-center text-red-600">Error al cargar la factura</div>
        </div>
      </div>
    )
  }

  const canValidate = currentStatus === InvoiceStatus.PENDING

  if (!canValidate) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-medium text-gray-900">
              Factura #{invoice.id} - {INVOICE_STATUS_LABELS[currentStatus]}
            </h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <XCircle className="h-6 w-6" />
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Información de la factura */}
            <div className="space-y-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-3">Información de la Factura</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Proveedor:</span>
                    <span className="font-medium">{invoice.provider}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Monto:</span>
                    <span className="font-medium">${invoice.amount.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Método de pago:</span>
                    <span className="font-medium">{PAYMENT_METHOD_LABELS[invoice.payment_method]}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Categoría:</span>
                    <span className="font-medium">{EXPENSE_CATEGORY_LABELS[invoice.category]}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Usuario:</span>
                    <span className="font-medium">{invoice.user.name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Fecha:</span>
                    <span className="font-medium">{new Date(invoice.date).toLocaleDateString()}</span>
                  </div>
                  {invoice.description && (
                    <div className="mt-3">
                      <span className="text-gray-600 block mb-1">Descripción:</span>
                      <p className="text-sm bg-white p-2 rounded border">{invoice.description}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Visualizador de archivos */}
            <div className="space-y-4">
              <h4 className="font-medium text-gray-900">Archivo Adjunto</h4>
              {invoice.file_path ? (
                <div className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-2">
                      {getFileIcon(invoice.file_path)}
                      <span className="text-sm font-medium text-gray-900">
                        {invoice.file_path.split('/').pop()}
                      </span>
                    </div>
                    <button
                      onClick={() => window.open(getFileUrl(), '_blank')}
                      className="text-blue-600 hover:text-blue-800 flex items-center space-x-1"
                    >
                      <Download className="h-4 w-4" />
                      <span className="text-sm">Abrir</span>
                    </button>
                  </div>

                  {/* Visualizador según el tipo de archivo */}
                  <div className="border border-gray-200 rounded-lg overflow-hidden">
                    {getFileType(invoice.file_path) === 'pdf' ? (
                      <iframe
                        src={getFileUrl()}
                        className="w-full h-96"
                        title="Vista previa del PDF"
                      />
                    ) : getFileType(invoice.file_path) === 'image' ? (
                      <img
                        src={getFileUrl()}
                        alt="Vista previa de la imagen"
                        className="w-full h-96 object-contain bg-gray-50"
                      />
                    ) : (
                      <div className="h-96 flex items-center justify-center bg-gray-50">
                        <div className="text-center">
                          {getFileIcon(invoice.file_path)}
                          <p className="text-sm text-gray-500 mt-2">
                            Vista previa no disponible para este tipo de archivo
                          </p>
                          <button
                            onClick={() => window.open(getFileUrl(), '_blank')}
                            className="mt-2 text-blue-600 hover:text-blue-800 text-sm"
                          >
                            Abrir archivo
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="border border-gray-200 rounded-lg p-8 text-center">
                  <FileText className="h-12 w-12 text-gray-400 mx-auto mb-3" />
                  <p className="text-gray-500">Esta factura no tiene archivo adjunto</p>
                </div>
              )}
            </div>
          </div>

          <div className="mt-6 flex justify-end">
            <button
              onClick={onClose}
              className="btn btn-secondary"
            >
              Cerrar
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-medium text-gray-900">
            Validar Factura #{invoice.id}
          </h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <XCircle className="h-6 w-6" />
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Información de la factura */}
          <div className="space-y-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-medium text-gray-900 mb-3">Información de la Factura</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Proveedor:</span>
                  <span className="font-medium">{invoice.provider}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Monto:</span>
                  <span className="font-medium">${invoice.amount.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Método de pago:</span>
                  <span className="font-medium">{PAYMENT_METHOD_LABELS[invoice.payment_method]}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Categoría:</span>
                  <span className="font-medium">{EXPENSE_CATEGORY_LABELS[invoice.category]}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Usuario:</span>
                  <span className="font-medium">{invoice.user.name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Fecha:</span>
                  <span className="font-medium">{new Date(invoice.date).toLocaleDateString()}</span>
                </div>
                {invoice.description && (
                  <div className="mt-3">
                    <span className="text-gray-600 block mb-1">Descripción:</span>
                    <p className="text-sm bg-white p-2 rounded border">{invoice.description}</p>
                  </div>
                )}
              </div>
            </div>

            {/* Formulario de validación */}
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Estado
                </label>
                <div className="space-y-2">
                  <label className="flex items-center">
                    <input
                      type="radio"
                      name="status"
                      value={InvoiceStatus.VALIDATED}
                      checked={selectedStatus === InvoiceStatus.VALIDATED}
                      onChange={(e) => setSelectedStatus(e.target.value as InvoiceStatus)}
                      className="mr-2"
                    />
                    <span className="flex items-center text-sm">
                      <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                      {INVOICE_STATUS_LABELS[InvoiceStatus.VALIDATED]}
                    </span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="radio"
                      name="status"
                      value={InvoiceStatus.REJECTED}
                      checked={selectedStatus === InvoiceStatus.REJECTED}
                      onChange={(e) => setSelectedStatus(e.target.value as InvoiceStatus)}
                      className="mr-2"
                    />
                    <span className="flex items-center text-sm">
                      <XCircle className="h-4 w-4 text-red-500 mr-2" />
                      {INVOICE_STATUS_LABELS[InvoiceStatus.REJECTED]}
                    </span>
                  </label>
                </div>
              </div>

              <div>
                <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-2">
                  Notas (opcional)
                </label>
                <textarea
                  id="notes"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  rows={3}
                  className="input"
                  placeholder="Añade comentarios sobre la validación..."
                />
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={onClose}
                  className="btn btn-secondary"
                  disabled={isSubmitting}
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting || !selectedStatus}
                  className="btn btn-primary"
                >
                  {isSubmitting ? 'Guardando...' : 'Guardar'}
                </button>
              </div>
            </form>
          </div>

          {/* Visualizador de archivos */}
          <div className="space-y-4">
            <h4 className="font-medium text-gray-900">Archivo Adjunto</h4>
            {invoice.file_path ? (
              <div className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    {getFileIcon(invoice.file_path)}
                    <span className="text-sm font-medium text-gray-900">
                      {invoice.file_path.split('/').pop()}
                    </span>
                  </div>
                    <button
                      onClick={() => window.open(getFileUrl(), '_blank')}
                      className="text-blue-600 hover:text-blue-800 flex items-center space-x-1"
                    >
                      <Download className="h-4 w-4" />
                      <span className="text-sm">Abrir</span>
                    </button>
                </div>

                {/* Visualizador según el tipo de archivo */}
                <div className="border border-gray-200 rounded-lg overflow-hidden">
                  {getFileType(invoice.file_path) === 'pdf' ? (
                    <iframe
                      src={getFileUrl()}
                      className="w-full h-96"
                      title="Vista previa del PDF"
                    />
                  ) : getFileType(invoice.file_path) === 'image' ? (
                    <img
                      src={getFileUrl()}
                      alt="Vista previa de la imagen"
                      className="w-full h-96 object-contain bg-gray-50"
                    />
                  ) : (
                    <div className="h-96 flex items-center justify-center bg-gray-50">
                      <div className="text-center">
                        {getFileIcon(invoice.file_path)}
                        <p className="text-sm text-gray-500 mt-2">
                          Vista previa no disponible para este tipo de archivo
                        </p>
                        <button
                          onClick={() => window.open(getFileUrl(), '_blank')}
                          className="mt-2 text-blue-600 hover:text-blue-800 text-sm"
                        >
                          Abrir archivo
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="border border-gray-200 rounded-lg p-8 text-center">
                <FileText className="h-12 w-12 text-gray-400 mx-auto mb-3" />
                <p className="text-gray-500">Esta factura no tiene archivo adjunto</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
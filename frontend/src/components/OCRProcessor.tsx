import React, { useState } from 'react'
import { useMutation, useQueryClient } from 'react-query'
import { 
  Upload, 
  FileText, 
  CheckCircle, 
  AlertCircle, 
  Loader2,
  Eye,
  Edit3,
  Save,
  X
} from 'lucide-react'
import { ocrApi } from '../services/api'
import { 
  PaymentMethod, 
  ExpenseCategory, 
  PAYMENT_METHOD_LABELS, 
  EXPENSE_CATEGORY_LABELS 
} from '../types'

interface OCRResult {
  amount: number | null
  provider: string | null
  date: string | null
  invoice_number: string | null
  confidence: number
  raw_text: string
  user_id: number
  user_name: string
}

interface OCRProcessorProps {
  userId: number
  onSuccess?: (invoiceId: number) => void
  onCancel?: () => void
}

export function OCRProcessor({ userId, onSuccess, onCancel }: OCRProcessorProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [ocrResult, setOcrResult] = useState<OCRResult | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [showPreview, setShowPreview] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  
  // Formulario para datos extraídos
  const [formData, setFormData] = useState({
    amount: '',
    provider: '',
    date: '',
    invoice_number: '',
    payment_method: '' as PaymentMethod,
    category: '' as ExpenseCategory,
    description: ''
  })
  
  const queryClient = useQueryClient()

  // Mutación para procesar OCR
  const processOCRMutation = useMutation(
    (file: File) => {
      return ocrApi.processInvoice(file, userId)
    },
    {
      onSuccess: (data) => {
        setOcrResult(data)
        setFormData({
          amount: data.amount?.toString() || '',
          provider: data.provider || '',
          date: data.date ? data.date.split('T')[0] : '',
          invoice_number: data.invoice_number || '',
          payment_method: '' as PaymentMethod,
          category: '' as ExpenseCategory,
          description: `Factura procesada con OCR. Confianza: ${(data.confidence * 100).toFixed(1)}%`
        })
        setIsProcessing(false)
      },
      onError: (error) => {
        console.error('Error procesando OCR:', error)
        setIsProcessing(false)
      }
    }
  )

  // Mutación para crear factura
  const createInvoiceMutation = useMutation(
    (data: any) => {
      return ocrApi.processAndCreateInvoice(selectedFile!, userId, data.payment_method, data.category, data.description)
    },
    {
      onSuccess: (invoice) => {
        queryClient.invalidateQueries('invoices')
        queryClient.invalidateQueries('dashboard-stats')
        onSuccess?.(invoice.id)
      },
      onError: (error) => {
        console.error('Error creando factura:', error)
      }
    }
  )

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      setOcrResult(null)
      setShowPreview(false)
      setIsEditing(false)
    }
  }

  const handleProcessOCR = () => {
    if (selectedFile) {
      setIsProcessing(true)
      processOCRMutation.mutate(selectedFile)
    }
  }

  const handleCreateInvoice = () => {
    if (selectedFile && formData.payment_method && formData.category) {
      createInvoiceMutation.mutate(formData)
    }
  }

  const handleEditData = () => {
    setIsEditing(true)
  }

  const handleSaveEdit = () => {
    setIsEditing(false)
  }

  const handleCancelEdit = () => {
    if (ocrResult) {
      setFormData({
        amount: ocrResult.amount?.toString() || '',
        provider: ocrResult.provider || '',
        date: ocrResult.date ? ocrResult.date.split('T')[0] : '',
        invoice_number: ocrResult.invoice_number || '',
        payment_method: formData.payment_method,
        category: formData.category,
        description: formData.description
      })
    }
    setIsEditing(false)
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600'
    if (confidence >= 0.6) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getConfidenceLabel = (confidence: number) => {
    if (confidence >= 0.8) return 'Alta'
    if (confidence >= 0.6) return 'Media'
    return 'Baja'
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center">
          <FileText className="h-6 w-6 mr-2 text-blue-600" />
          Procesar Factura con OCR
        </h2>
        {onCancel && (
          <button
            onClick={onCancel}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="h-6 w-6" />
          </button>
        )}
      </div>

      {/* Paso 1: Selección de archivo */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Seleccionar archivo de factura
        </label>
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
          <input
            type="file"
            accept=".jpg,.jpeg,.png,.pdf,.tiff,.bmp"
            onChange={handleFileSelect}
            className="hidden"
            id="file-upload"
          />
          <label
            htmlFor="file-upload"
            className="cursor-pointer flex flex-col items-center"
          >
            <Upload className="h-12 w-12 text-gray-400 mb-4" />
            <span className="text-lg font-medium text-gray-900">
              {selectedFile ? selectedFile.name : 'Hacer clic para seleccionar archivo'}
            </span>
            <span className="text-sm text-gray-500 mt-2">
              Formatos soportados: JPG, PNG, PDF, TIFF, BMP
            </span>
          </label>
        </div>
        
        {selectedFile && (
          <div className="mt-4 flex justify-center">
            <button
              onClick={handleProcessOCR}
              disabled={isProcessing}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center"
            >
              {isProcessing ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Procesando...
                </>
              ) : (
                <>
                  <FileText className="h-4 w-4 mr-2" />
                  Procesar con OCR
                </>
              )}
            </button>
          </div>
        )}
      </div>

      {/* Paso 2: Resultados del OCR */}
      {ocrResult ? (
        <div className="mb-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">
              Datos extraídos por OCR
            </h3>
            <div className="flex items-center space-x-2">
              <span className={`text-sm font-medium ${getConfidenceColor(ocrResult.confidence)}`}>
                Confianza: {getConfidenceLabel(ocrResult.confidence)} ({(ocrResult.confidence * 100).toFixed(1)}%)
              </span>
              <button
                onClick={() => setShowPreview(!showPreview)}
                className="text-blue-600 hover:text-blue-800 text-sm flex items-center"
              >
                <Eye className="h-4 w-4 mr-1" />
                {showPreview ? 'Ocultar' : 'Ver'} texto extraído
              </button>
            </div>
          </div>

          {/* Vista previa del texto extraído */}
          {showPreview && (
            <div className="mb-4 p-4 bg-gray-50 rounded-lg">
              <h4 className="text-sm font-medium text-gray-700 mb-2">Texto extraído:</h4>
              <pre className="text-sm text-gray-600 whitespace-pre-wrap max-h-40 overflow-y-auto">
                {ocrResult.raw_text}
              </pre>
            </div>
          )}

          {/* Formulario de datos extraídos */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Monto *
              </label>
              {isEditing ? (
                <input
                  type="number"
                  step="0.01"
                  value={formData.amount}
                  onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              ) : (
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                  <span className="text-gray-900">
                    {ocrResult.amount ? `$${ocrResult.amount.toLocaleString()}` : 'No detectado'}
                  </span>
                  {ocrResult.amount ? (
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  ) : (
                    <AlertCircle className="h-5 w-5 text-red-500" />
                  )}
                </div>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Proveedor
              </label>
              {isEditing ? (
                <input
                  type="text"
                  value={formData.provider}
                  onChange={(e) => setFormData({ ...formData, provider: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              ) : (
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                  <span className="text-gray-900">
                    {ocrResult.provider || 'No detectado'}
                  </span>
                  {ocrResult.provider ? (
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  ) : (
                    <AlertCircle className="h-5 w-5 text-red-500" />
                  )}
                </div>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Fecha
              </label>
              {isEditing ? (
                <input
                  type="date"
                  value={formData.date}
                  onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              ) : (
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                  <span className="text-gray-900">
                    {ocrResult.date ? new Date(ocrResult.date).toLocaleDateString() : 'No detectada'}
                  </span>
                  {ocrResult.date ? (
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  ) : (
                    <AlertCircle className="h-5 w-5 text-red-500" />
                  )}
                </div>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Número de factura
              </label>
              {isEditing ? (
                <input
                  type="text"
                  value={formData.invoice_number}
                  onChange={(e) => setFormData({ ...formData, invoice_number: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              ) : (
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                  <span className="text-gray-900">
                    {ocrResult.invoice_number || 'No detectado'}
                  </span>
                  {ocrResult.invoice_number ? (
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  ) : (
                    <AlertCircle className="h-5 w-5 text-red-500" />
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Botones de edición */}
          <div className="mt-4 flex justify-end space-x-2">
            {!isEditing ? (
              <button
                onClick={handleEditData}
                className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 flex items-center"
              >
                <Edit3 className="h-4 w-4 mr-2" />
                Editar datos
              </button>
            ) : (
              <>
                <button
                  onClick={handleCancelEdit}
                  className="bg-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-400"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleSaveEdit}
                  className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center"
                >
                  <Save className="h-4 w-4 mr-2" />
                  Guardar cambios
                </button>
              </>
            )}
          </div>
        </div>
      ) : null}

      {/* Paso 3: Completar información y crear factura */}
      {ocrResult ? (
        <div className="border-t pt-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Completar información
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Método de pago *
              </label>
              <select
                value={formData.payment_method}
                onChange={(e) => setFormData({ ...formData, payment_method: e.target.value as PaymentMethod })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="">Seleccionar método</option>
                {Object.entries(PAYMENT_METHOD_LABELS).map(([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Categoría *
              </label>
              <select
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value as ExpenseCategory })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="">Seleccionar categoría</option>
                {Object.entries(EXPENSE_CATEGORY_LABELS).map(([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Descripción
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Descripción adicional de la factura..."
            />
          </div>

          <div className="flex justify-end space-x-2">
            <button
              onClick={handleCreateInvoice}
              disabled={!formData.payment_method || !formData.category || createInvoiceMutation.isLoading}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center"
            >
              {createInvoiceMutation.isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Creando factura...
                </>
              ) : (
                <>
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Crear factura
                </>
              )}
            </button>
          </div>
        </div>
      ) : null}

      {/* Mensajes de error */}
      {processOCRMutation.error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center">
            <AlertCircle className="h-5 w-5 text-red-500 mr-2" />
            <span className="text-red-700">
              Error procesando la factura: {(processOCRMutation.error as Error)?.message || 'Error desconocido'}
            </span>
          </div>
        </div>
      )}

      {createInvoiceMutation.error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center">
            <AlertCircle className="h-5 w-5 text-red-500 mr-2" />
            <span className="text-red-700">
              Error creando la factura: {(createInvoiceMutation.error as Error)?.message || 'Error desconocido'}
            </span>
          </div>
        </div>
      )}
    </div>
  )
}
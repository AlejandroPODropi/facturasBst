import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { invoicesApi } from '../services/api'
import type { 
  InvoiceAnalysisResponse, 
  InvoiceAnalysisResult, 
  BulkInvoiceResponse
} from '../types'
import { PaymentMethod, ExpenseCategory } from '../types'
import { 
  Search, 
  Upload, 
  AlertCircle, 
  CheckCircle, 
  Clock, 
  FileText,
  Mail,
  Calendar,
  DollarSign,
  Building,
  Loader2,
  X
} from 'lucide-react'

interface InvoiceAnalysisProps {
  onClose?: () => void
}

export function InvoiceAnalysis({ onClose }: InvoiceAnalysisProps) {
  const [searchQuery, setSearchQuery] = useState('has:attachment newer_than:30d')
  const [maxResults, setMaxResults] = useState(50)
  const [selectedInvoices, setSelectedInvoices] = useState<Set<string>>(new Set())
  const [showWithoutUser, setShowWithoutUser] = useState(true)
  const [showWithUser, setShowWithUser] = useState(true)
  const [showDuplicates, setShowDuplicates] = useState(true)
  const [bulkProcessing, setBulkProcessing] = useState(false)
  
  const queryClient = useQueryClient()

  // Obtener usuarios para asignación (comentado por ahora)
  // const { data: users = [] } = useQuery<User[]>(
  //   ['users'],
  //   () => usersApi.getAll()
  // )

  // Análisis de facturas
  const { 
    data: analysisData, 
    isLoading: isAnalyzing, 
    error: analysisError,
    refetch: refetchAnalysis
  } = useQuery<InvoiceAnalysisResponse>(
    ['invoice-analysis', searchQuery, maxResults],
    () => invoicesApi.analyzeInvoices(searchQuery, maxResults),
    {
      enabled: false, // Solo se ejecuta manualmente
      retry: false
    }
  )

  // Mutación para procesamiento en lote
  const bulkCreateMutation = useMutation<BulkInvoiceResponse, Error, any[]>(
    (invoices) => invoicesApi.bulkCreate(invoices, true),
    {
      onSuccess: (data) => {
        alert(`Procesamiento completado: ${data.created_count} facturas creadas, ${data.skipped_count} omitidas, ${data.error_count} errores`)
        queryClient.invalidateQueries(['invoices'])
        queryClient.invalidateQueries(['dashboard-stats'])
        setSelectedInvoices(new Set())
        setBulkProcessing(false)
      },
      onError: (error) => {
        console.error('Error en procesamiento en lote:', error)
        alert('Error en el procesamiento en lote. Por favor, inténtalo de nuevo.')
        setBulkProcessing(false)
      }
    }
  )

  const handleAnalyze = () => {
    refetchAnalysis()
  }

  const handleSelectInvoice = (emailId: string) => {
    const newSelected = new Set(selectedInvoices)
    if (newSelected.has(emailId)) {
      newSelected.delete(emailId)
    } else {
      newSelected.add(emailId)
    }
    setSelectedInvoices(newSelected)
  }

  const handleSelectAll = (invoices: InvoiceAnalysisResult[]) => {
    if (selectedInvoices.size === invoices.length) {
      setSelectedInvoices(new Set())
    } else {
      setSelectedInvoices(new Set(invoices.map(inv => inv.email_id)))
    }
  }

  const handleBulkProcess = async () => {
    if (selectedInvoices.size === 0) {
      alert('Por favor, selecciona al menos una factura para procesar.')
      return
    }

    // Procesar facturas con usuario asignado
    const invoicesWithUser = analysisData?.invoices_to_upload.filter(
      inv => selectedInvoices.has(inv.email_id)
    ).map(inv => ({
      ...inv,
      user_id: inv.suggested_user_id,
      payment_method: PaymentMethod.CASH,
      category: ExpenseCategory.OTHER
    })) || []

    // Procesar facturas sin usuario (se marcarán como "sin usuario")
    const invoicesWithoutUser = analysisData?.invoices_without_user.filter(
      inv => selectedInvoices.has(inv.email_id)
    ).map(inv => ({
      ...inv,
      user_id: undefined, // Sin usuario asignado
      payment_method: PaymentMethod.CASH,
      category: ExpenseCategory.OTHER
    })) || []

    const allInvoicesToProcess = [...invoicesWithUser, ...invoicesWithoutUser]

    if (allInvoicesToProcess.length === 0) {
      alert('No hay facturas válidas seleccionadas para procesar.')
      return
    }

    setBulkProcessing(true)
    bulkCreateMutation.mutate(allInvoicesToProcess)
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

  const truncateText = (text: string, maxLength: number = 60) => {
    if (text.length <= maxLength) return text
    return text.substring(0, maxLength) + '...'
  }

  const formatSubject = (subject: string) => {
    // Limpiar el asunto removiendo patrones comunes de facturación
    let cleanSubject = subject
    
    // Remover patrones como: 901294241;PAGOS AUTOMATICOS DE COLOMBIA SAS;FVFE255128;01;PAGOS AUTOMATICOS DE COLOMBIA SAS
    cleanSubject = cleanSubject.replace(/^\d{9,12};[^;]+;[^;]+;\d{2};[^;]+/, '')
    
    // Remover códigos de factura al inicio
    cleanSubject = cleanSubject.replace(/^[A-Z0-9]{6,12}\s*[-–]\s*/, '')
    
    // Remover "Factura" o "Invoice" al inicio
    cleanSubject = cleanSubject.replace(/^(Factura|Invoice)\s+\d+\s*[-–]\s*/i, '')
    
    // Limpiar espacios extra
    cleanSubject = cleanSubject.trim()
    
    // Si queda vacío, usar el asunto original truncado
    if (!cleanSubject) {
      cleanSubject = subject
    }
    
    return truncateText(cleanSubject, 50)
  }

  const getStatusIcon = (invoice: InvoiceAnalysisResult) => {
    if (invoice.suggested_user_id) {
      return <CheckCircle className="h-4 w-4 text-green-500" />
    }
    return <AlertCircle className="h-4 w-4 text-yellow-500" />
  }

  const getStatusText = (invoice: InvoiceAnalysisResult) => {
    if (invoice.suggested_user_id) {
      return `Usuario: ${invoice.suggested_user_name}`
    }
    return `Sin usuario: ${invoice.reason_no_user || 'No identificado'}`
  }

  const renderInvoiceCard = (invoice: InvoiceAnalysisResult, isSelected: boolean) => (
    <div 
      key={invoice.email_id}
      className={`border rounded-lg p-4 cursor-pointer transition-all ${
        isSelected ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
      }`}
      onClick={() => handleSelectInvoice(invoice.email_id)}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            {getStatusIcon(invoice)}
            <h4 className="font-medium text-gray-900 truncate">
              {invoice.provider}
            </h4>
          </div>
          
          <div className="space-y-1 text-sm text-gray-600">
            <div className="flex items-center gap-2">
              <Mail className="h-3 w-3" />
              <span className="truncate" title={invoice.email_subject}>
                {formatSubject(invoice.email_subject)}
              </span>
            </div>
            
            <div className="flex items-center gap-2">
              <Building className="h-3 w-3" />
              <span className="truncate">{invoice.email_from}</span>
            </div>
            
            <div className="flex items-center gap-2">
              <Calendar className="h-3 w-3" />
              <span>{formatDate(invoice.date)}</span>
            </div>
            
            <div className="flex items-center gap-2">
              <DollarSign className="h-3 w-3" />
              <span className="font-medium">{formatCurrency(invoice.amount)}</span>
            </div>
            
            <div className="flex items-center gap-2">
              <FileText className="h-3 w-3" />
              <span>{invoice.attachments.length} archivo(s)</span>
            </div>
          </div>
          
          <div className="mt-2 text-xs text-gray-500">
            {getStatusText(invoice)}
          </div>
        </div>
        
        <div className="ml-4">
          <input
            type="checkbox"
            checked={isSelected}
            onChange={() => handleSelectInvoice(invoice.email_id)}
            className="h-4 w-4 text-blue-600 rounded"
          />
        </div>
      </div>
    </div>
  )

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Análisis de Facturas Gmail</h2>
          <p className="text-gray-600">Analiza y procesa facturas desde Gmail automáticamente</p>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="h-6 w-6" />
          </button>
        )}
      </div>

      {/* Controles de búsqueda */}
      <div className="bg-white p-6 rounded-lg border">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Query de Búsqueda Gmail
            </label>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="has:attachment newer_than:30d"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Máximo de Resultados
            </label>
            <input
              type="number"
              value={maxResults}
              onChange={(e) => setMaxResults(Number(e.target.value))}
              min="1"
              max="100"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div className="flex items-end">
            <button
              onClick={handleAnalyze}
              disabled={isAnalyzing}
              className="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isAnalyzing ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Search className="h-4 w-4" />
              )}
              {isAnalyzing ? 'Analizando...' : 'Analizar Facturas'}
            </button>
          </div>
        </div>
      </div>

      {/* Error de análisis */}
      {analysisError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center gap-2 text-red-800">
            <AlertCircle className="h-5 w-5" />
            <span className="font-medium">Error en el análisis</span>
          </div>
          <p className="text-red-700 mt-1">
            {analysisError instanceof Error ? analysisError.message : 'Error desconocido'}
          </p>
        </div>
      )}

      {/* Resultados del análisis */}
      {analysisData && (
        <div className="space-y-6">
          {/* Resumen */}
          <div className="bg-white p-6 rounded-lg border">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Resumen del Análisis</h3>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {analysisData.summary.total_emails_analyzed}
                </div>
                <div className="text-sm text-gray-600">Emails Analizados</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {analysisData.summary.invoices_found}
                </div>
                <div className="text-sm text-gray-600">Facturas Encontradas</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {analysisData.summary.invoices_with_user}
                </div>
                <div className="text-sm text-gray-600">Con Usuario</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-yellow-600">
                  {analysisData.summary.invoices_without_user}
                </div>
                <div className="text-sm text-gray-600">Sin Usuario</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-600">
                  {analysisData.summary.already_uploaded}
                </div>
                <div className="text-sm text-gray-600">Ya Subidas</div>
              </div>
            </div>
          </div>

          {/* Filtros de visualización */}
          <div className="bg-white p-4 rounded-lg border">
            <div className="flex items-center gap-4">
              <span className="text-sm font-medium text-gray-700">Mostrar:</span>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={showWithUser}
                  onChange={(e) => setShowWithUser(e.target.checked)}
                  className="h-4 w-4 text-blue-600 rounded"
                />
                <span className="text-sm text-gray-600">Con Usuario ({analysisData.invoices_to_upload.length})</span>
              </label>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={showWithoutUser}
                  onChange={(e) => setShowWithoutUser(e.target.checked)}
                  className="h-4 w-4 text-blue-600 rounded"
                />
                <span className="text-sm text-gray-600">Sin Usuario ({analysisData.invoices_without_user.length})</span>
              </label>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={showDuplicates}
                  onChange={(e) => setShowDuplicates(e.target.checked)}
                  className="h-4 w-4 text-blue-600 rounded"
                />
                <span className="text-sm text-gray-600">Duplicadas ({analysisData.already_uploaded.length})</span>
              </label>
            </div>
          </div>

          {/* Facturas con usuario */}
          {showWithUser && analysisData.invoices_to_upload.length > 0 && (
            <div className="bg-white p-6 rounded-lg border">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  Facturas con Usuario Asignado ({analysisData.invoices_to_upload.length})
                </h3>
                <button
                  onClick={() => handleSelectAll(analysisData.invoices_to_upload)}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  {selectedInvoices.size === analysisData.invoices_to_upload.length ? 'Deseleccionar Todo' : 'Seleccionar Todo'}
                </button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {analysisData.invoices_to_upload.map(invoice => 
                  renderInvoiceCard(invoice, selectedInvoices.has(invoice.email_id))
                )}
              </div>
            </div>
          )}

          {/* Facturas sin usuario */}
          {showWithoutUser && analysisData.invoices_without_user.length > 0 && (
            <div className="bg-white p-6 rounded-lg border">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2 mb-4">
                <AlertCircle className="h-5 w-5 text-yellow-500" />
                Facturas sin Usuario Asignado ({analysisData.invoices_without_user.length})
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {analysisData.invoices_without_user.map(invoice => 
                  renderInvoiceCard(invoice, selectedInvoices.has(invoice.email_id))
                )}
              </div>
            </div>
          )}

          {/* Facturas duplicadas */}
          {showDuplicates && analysisData.already_uploaded.length > 0 && (
            <div className="bg-white p-6 rounded-lg border">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2 mb-4">
                <Clock className="h-5 w-5 text-gray-500" />
                Facturas Ya Subidas ({analysisData.already_uploaded.length})
              </h3>
              <div className="space-y-2">
                {analysisData.already_uploaded.map(invoice => (
                  <div key={invoice.email_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div>
                      <div className="font-medium">{invoice.provider}</div>
                      <div className="text-sm text-gray-600">{invoice.email_subject}</div>
                    </div>
                    <div className="text-right">
                      <div className="font-medium">{formatCurrency(invoice.amount)}</div>
                      <div className="text-sm text-gray-600">Usuario: {invoice.existing_user}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Botón de procesamiento en lote */}
          {selectedInvoices.size > 0 && (
            <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium text-blue-900">
                    {selectedInvoices.size} factura(s) seleccionada(s)
                  </div>
                  <div className="text-sm text-blue-700">
                    Se procesarán todas las facturas seleccionadas. Las sin usuario quedarán marcadas como "sin usuario"
                  </div>
                </div>
                <button
                  onClick={handleBulkProcess}
                  disabled={bulkProcessing}
                  className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  {bulkProcessing ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Upload className="h-4 w-4" />
                  )}
                  {bulkProcessing ? 'Procesando...' : 'Procesar Seleccionadas'}
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

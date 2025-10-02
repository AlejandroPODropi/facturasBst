import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { dashboardApi } from '../services/api'
import { 
  Mail, 
  RefreshCw, 
  CheckCircle, 
  AlertCircle, 
  Settings, 
  Download,
  Eye,
  X,
  // Clock
} from 'lucide-react'

// interface GmailStats {
//   total_emails_7d: number
//   emails_with_attachments_7d: number
//   unread_emails_7d: number
//   attachment_rate: number
// }

interface ProcessedInvoice {
  invoice_id: number
  provider: string
  amount: number
  email_subject: string
}

export function GmailIntegration() {
  const [isProcessing, setIsProcessing] = useState(false)
  const [showAuthModal, setShowAuthModal] = useState(false)
  const [authCode, setAuthCode] = useState('')
  const [lastProcessed, setLastProcessed] = useState<ProcessedInvoice[]>([])
  const queryClient = useQueryClient()

  // Consultar estadísticas de Gmail
  const { data: gmailStats, isLoading: statsLoading, refetch: refetchStats } = useQuery(
    'gmail-stats',
    () => dashboardApi.getGmailStats(),
    {
      refetchInterval: 30000, // Refrescar cada 30 segundos
    }
  )

  // Consultar estado de autenticación
  const { data: authStatus, refetch: refetchAuth } = useQuery(
    'gmail-auth-status',
    () => dashboardApi.getGmailAuthStatus(),
    {
      refetchInterval: 60000, // Refrescar cada minuto
    }
  )

    // Mutación para obtener instrucciones de autorización manual
    const getManualAuthMutation = useMutation(
        () => dashboardApi.getGmailManualAuthInstructions(),
        {
            onSuccess: (data) => {
                if (data.auth_url) {
                    // Mostrar instrucciones detalladas y abrir modal
                    const instructions = data.instructions?.join('\n') || ''
                    const note = data.note || ''
                    alert(`Instrucciones para autorizar Gmail:\n\n${instructions}\n\n${note}\n\nSe abrirá la URL de autorización.`)
                    window.open(data.auth_url, '_blank', 'width=600,height=600')
                    setShowAuthModal(true)
                }
            },
            onError: (error) => {
                console.error('Error obteniendo instrucciones de autorización:', error)
                alert('Error obteniendo instrucciones de autorización. Por favor, inténtalo de nuevo.')
            }
        }
    )

    // Mutación para procesar el código de autorización
    const authCallbackMutation = useMutation(
        (code: string) => dashboardApi.authenticateGmail(code),
        {
            onSuccess: (data) => {
                alert('¡Autorización exitosa! Gmail está ahora conectado.')
                setShowAuthModal(false)
                setAuthCode('')
                queryClient.invalidateQueries(['gmail-auth-status'])
                queryClient.invalidateQueries(['gmail-stats'])
            },
            onError: (error) => {
                console.error('Error en autorización:', error)
                const errorMessage = error?.response?.data?.detail || 'Error en autorización. Por favor, verifica el código e inténtalo de nuevo.'
                alert(`Error: ${errorMessage}`)
            }
        }
    )

  // Mutación para procesar facturas
  const processInvoicesMutation = useMutation(
    (limit: number) => dashboardApi.processGmailInvoices(limit),
    {
      onSuccess: (data) => {
        setLastProcessed(data.processed_invoices || [])
        setIsProcessing(false)
        // Refrescar datos del dashboard
        queryClient.invalidateQueries('dashboard-stats')
        queryClient.invalidateQueries('invoices')
        queryClient.invalidateQueries('gmail-stats')
      },
      onError: (error) => {
        console.error('Error procesando facturas:', error)
        setIsProcessing(false)
      },
    }
  )


  const handleProcessInvoices = async () => {
    setIsProcessing(true)
    processInvoicesMutation.mutate(10)
  }

    const handleAuthenticate = () => {
        getManualAuthMutation.mutate()
    }

    const handleSubmitAuthCode = () => {
        if (authCode.trim()) {
            authCallbackMutation.mutate(authCode.trim())
        } else {
            alert('Por favor, ingresa el código de autorización.')
        }
    }

    const handleCloseAuthModal = () => {
        setShowAuthModal(false)
        setAuthCode('')
    }

  const handleRefreshStats = () => {
    refetchStats()
    refetchAuth()
  }

  if (statsLoading) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="space-y-3">
            <div className="h-4 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-200 rounded w-2/3"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Mail className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <h3 className="text-lg font-medium text-gray-900">Integración con Gmail</h3>
              <p className="text-sm text-gray-500">
                Procesamiento automático de facturas desde correos electrónicos
              </p>
            </div>
          </div>
          <div className="flex space-x-2">
            <button
              onClick={handleRefreshStats}
              className="btn btn-secondary"
              disabled={isProcessing}
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Actualizar
            </button>
        {!authStatus?.authenticated && (
            <button
                onClick={handleAuthenticate}
                className="btn btn-primary"
                disabled={getManualAuthMutation.isLoading}
            >
                <Settings className="h-4 w-4 mr-2" />
                Conectar Gmail
            </button>
        )}
          </div>
        </div>
      </div>

      {/* Estado de autenticación */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h4 className="text-md font-medium text-gray-900 mb-4">Estado de Conexión</h4>
        <div className="flex items-center space-x-3">
          {authStatus?.authenticated ? (
            <>
              <CheckCircle className="h-5 w-5 text-green-500" />
              <span className="text-green-700 font-medium">Conectado a Gmail</span>
            </>
          ) : (
            <>
              <AlertCircle className="h-5 w-5 text-red-500" />
              <span className="text-red-700 font-medium">No conectado</span>
            </>
          )}
        </div>
        {!authStatus?.authenticated && (
          <p className="text-sm text-gray-500 mt-2">
            Conecta tu cuenta de Gmail para procesar facturas automáticamente
          </p>
        )}
      </div>

      {/* Estadísticas de Gmail */}
      {gmailStats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center">
              <div className="flex-shrink-0 rounded-md p-2 bg-blue-100">
                <Mail className="h-5 w-5 text-blue-600" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Correos (7 días)</p>
                <p className="text-xl font-semibold text-gray-900">
                  {gmailStats.total_emails_7d}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center">
              <div className="flex-shrink-0 rounded-md p-2 bg-green-100">
                <Download className="h-5 w-5 text-green-600" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Con Adjuntos</p>
                <p className="text-xl font-semibold text-gray-900">
                  {gmailStats.emails_with_attachments_7d}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center">
              <div className="flex-shrink-0 rounded-md p-2 bg-orange-100">
                <Eye className="h-5 w-5 text-orange-600" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">No Leídos</p>
                <p className="text-xl font-semibold text-gray-900">
                  {gmailStats.unread_emails_7d}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center">
              <div className="flex-shrink-0 rounded-md p-2 bg-purple-100">
                <CheckCircle className="h-5 w-5 text-purple-600" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Tasa Adjuntos</p>
                <p className="text-xl font-semibold text-gray-900">
                  {gmailStats.attachment_rate.toFixed(1)}%
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Procesamiento de facturas */}
      {authStatus?.authenticated && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h4 className="text-md font-medium text-gray-900 mb-4">Procesamiento de Facturas</h4>
          <div className="space-y-4">
            <p className="text-sm text-gray-600">
              Procesa automáticamente los correos recientes para extraer facturas y crear registros en el sistema.
            </p>
            
            <button
              onClick={handleProcessInvoices}
              disabled={isProcessing}
              className="btn btn-primary"
            >
              {isProcessing ? (
                <>
                  <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                  Procesando...
                </>
              ) : (
                <>
                  <Mail className="h-4 w-4 mr-2" />
                  Procesar Facturas
                </>
              )}
            </button>

            {processInvoicesMutation.isError && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-md">
                <div className="flex items-center">
                  <AlertCircle className="h-5 w-5 text-red-500 mr-2" />
                  <span className="text-red-700 text-sm">
                    Error al procesar facturas. Intenta nuevamente.
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Resultados del último procesamiento */}
      {lastProcessed.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h4 className="text-md font-medium text-gray-900 mb-4">Último Procesamiento</h4>
          <div className="space-y-3">
            {lastProcessed.map((invoice, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      Factura #{invoice.invoice_id} - {invoice.provider}
                    </p>
                    <p className="text-xs text-gray-500">
                      ${invoice.amount.toLocaleString()} - {invoice.email_subject}
                    </p>
                  </div>
                </div>
                <span className="text-xs text-green-600 font-medium">
                  Procesada
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Información de configuración */}
      <div className="bg-blue-50 rounded-lg border border-blue-200 p-6">
        <h4 className="text-md font-medium text-blue-900 mb-2">Configuración Requerida</h4>
        <div className="text-sm text-blue-800 space-y-2">
          <p>Para usar la integración con Gmail, necesitas:</p>
          <ul className="list-disc list-inside space-y-1 ml-4">
            <li>Configurar las credenciales de Gmail API en el servidor</li>
            <li>Autorizar el acceso a tu cuenta de Gmail</li>
            <li>Permitir el acceso a correos con adjuntos</li>
          </ul>
          <p className="mt-3">
            <strong>Nota:</strong> Solo se procesarán correos que contengan palabras clave relacionadas con facturas y tengan archivos adjuntos.
          </p>
        </div>
      </div>

      {/* Modal para código de autorización */}
      {showAuthModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">Código de Autorización</h3>
              <button
                onClick={handleCloseAuthModal}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            
            <div className="mb-4">
              <p className="text-sm text-gray-600 mb-3">
                Después de autorizar la aplicación en Google, copia el código de autorización que aparece en la pantalla y pégalo aquí:
              </p>
              <textarea
                value={authCode}
                onChange={(e) => setAuthCode(e.target.value)}
                placeholder="Pega aquí el código de autorización..."
                className="w-full p-3 border border-gray-300 rounded-md resize-none"
                rows={3}
              />
            </div>
            
            <div className="flex space-x-3">
              <button
                onClick={handleCloseAuthModal}
                className="flex-1 px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
              >
                Cancelar
              </button>
              <button
                onClick={handleSubmitAuthCode}
                disabled={authCallbackMutation.isLoading || !authCode.trim()}
                className="flex-1 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {authCallbackMutation.isLoading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Procesando...
                  </>
                ) : (
                  'Autorizar'
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

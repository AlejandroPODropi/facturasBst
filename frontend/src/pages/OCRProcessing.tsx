import { useState } from 'react'
import { useQuery } from 'react-query'
import { usersApi } from '../services/api'
import { OCRProcessor } from '../components/OCRProcessor'
import { ArrowLeft, FileText, Users } from 'lucide-react'
import { Link } from 'react-router-dom'

export function OCRProcessing() {
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null)
  const [showProcessor, setShowProcessor] = useState(false)
  
  const { data: users = [], isLoading } = useQuery('users', () => usersApi.getAll())

  const handleUserSelect = (userId: number) => {
    setSelectedUserId(userId)
    setShowProcessor(true)
  }

  const handleSuccess = (invoiceId: number) => {
    // Redirigir a la página de facturas o mostrar mensaje de éxito
    setShowProcessor(false)
    setSelectedUserId(null)
    // Aquí podrías mostrar una notificación de éxito
    console.log('Factura creada exitosamente:', invoiceId)
  }

  const handleCancel = () => {
    setShowProcessor(false)
    setSelectedUserId(null)
  }

  if (showProcessor && selectedUserId) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mb-6">
            <Link
              to="/invoices"
              className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700"
            >
              <ArrowLeft className="h-4 w-4 mr-1" />
              Volver a facturas
            </Link>
          </div>
          
                  <OCRProcessor
                    userId={selectedUserId}
                    onSuccess={handleSuccess}
                    onCancel={handleCancel}
                  />
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center">
                <FileText className="h-8 w-8 mr-3 text-blue-600" />
                Procesar Facturas con OCR
              </h1>
              <p className="mt-2 text-gray-600">
                Digitaliza facturas físicas automáticamente usando tecnología OCR
              </p>
            </div>
            <Link
              to="/invoices"
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Volver a facturas
            </Link>
          </div>
        </div>

        {/* Información sobre OCR */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <FileText className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-3">
              <h3 className="text-lg font-medium text-blue-900">
                ¿Qué es el procesamiento OCR?
              </h3>
              <div className="mt-2 text-sm text-blue-700">
                <p className="mb-2">
                  El procesamiento OCR (Reconocimiento Óptico de Caracteres) permite extraer 
                  automáticamente información de facturas físicas escaneadas o fotografiadas.
                </p>
                <ul className="list-disc list-inside space-y-1">
                  <li>Extrae automáticamente el monto, proveedor, fecha y número de factura</li>
                  <li>Soporta formatos: JPG, PNG, PDF, TIFF, BMP</li>
                  <li>Proporciona un nivel de confianza para validar la extracción</li>
                  <li>Permite editar y corregir los datos extraídos antes de crear la factura</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Selección de usuario */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            <Users className="h-5 w-5 mr-2 text-gray-600" />
            Seleccionar usuario
          </h2>
          
          {isLoading ? (
            <div className="flex justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {users.map((user: any) => (
                <button
                  key={user.id}
                  onClick={() => handleUserSelect(user.id)}
                  className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors text-left"
                >
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="h-10 w-10 bg-blue-100 rounded-full flex items-center justify-center">
                        <span className="text-sm font-medium text-blue-600">
                          {user.name.charAt(0).toUpperCase()}
                        </span>
                      </div>
                    </div>
                    <div className="ml-3">
                      <p className="text-sm font-medium text-gray-900">{user.name}</p>
                      <p className="text-sm text-gray-500">{user.email}</p>
                      <p className="text-xs text-gray-400 capitalize">{user.role}</p>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Instrucciones */}
        <div className="mt-8 bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Instrucciones de uso
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">1. Seleccionar usuario</h4>
              <p className="text-sm text-gray-600">
                Elige el colaborador al que pertenece la factura que vas a procesar.
              </p>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-2">2. Subir archivo</h4>
              <p className="text-sm text-gray-600">
                Selecciona la imagen o PDF de la factura que deseas procesar.
              </p>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-2">3. Revisar datos</h4>
              <p className="text-sm text-gray-600">
                Revisa y edita los datos extraídos por el OCR si es necesario.
              </p>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-2">4. Completar información</h4>
              <p className="text-sm text-gray-600">
                Selecciona el método de pago y categoría, luego crea la factura.
              </p>
            </div>
          </div>
        </div>

        {/* Consejos para mejores resultados */}
        <div className="mt-8 bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-yellow-900 mb-4">
            💡 Consejos para mejores resultados
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h4 className="font-medium text-yellow-900 mb-2">Calidad de imagen</h4>
              <ul className="text-sm text-yellow-800 space-y-1">
                <li>• Usa buena iluminación al fotografiar</li>
                <li>• Mantén la cámara estable</li>
                <li>• Asegúrate de que todo el texto sea legible</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-yellow-900 mb-2">Formato de archivo</h4>
              <ul className="text-sm text-yellow-800 space-y-1">
                <li>• PDFs con texto son más precisos</li>
                <li>• Imágenes JPG/PNG de alta resolución</li>
                <li>• Evita archivos muy comprimidos</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

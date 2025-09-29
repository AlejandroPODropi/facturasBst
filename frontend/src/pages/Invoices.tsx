import { useState } from 'react'
import { useQuery } from 'react-query'
import { useNavigate } from 'react-router-dom'
import { invoicesApi, usersApi } from '../services/api'
import { 
  INVOICE_STATUS_LABELS, 
  INVOICE_STATUS_COLORS,
  PAYMENT_METHOD_LABELS,
  EXPENSE_CATEGORY_LABELS,
  InvoiceStatus,
  PaymentMethod,
  ExpenseCategory
} from '../types'
import { Plus, Download, Edit, Trash2, CheckCircle, Eye } from 'lucide-react'
import { InvoiceValidation } from '../components/InvoiceValidation'
import { InvoiceFilters } from '../components/InvoiceFilters'
import { InvoiceCard } from '../components/InvoiceCard'

export function Invoices() {
  const navigate = useNavigate()
  const [filters, setFilters] = useState<any>({})
  const { data: invoicesData, isLoading } = useQuery(['invoices', filters], () => invoicesApi.getAll(filters))
  const { data: users = [] } = useQuery('users', () => usersApi.getAll())
  
  const invoices = invoicesData?.items || []
  const [validationInvoice, setValidationInvoice] = useState<{ id: number; status: InvoiceStatus } | null>(null)

  const handleFiltersChange = (newFilters: any) => {
    // Limpiar filtros vacíos
    const cleanFilters = Object.fromEntries(
      Object.entries(newFilters).filter(([_, value]) => value !== '')
    )
    setFilters(cleanFilters)
  }

  const handleClearFilters = () => {
    setFilters({})
  }

  const handleEditInvoice = (id: number) => {
    // TODO: Implementar edición de facturas
    console.log('Editar factura:', id)
  }

  const handleDeleteInvoice = (id: number) => {
    // TODO: Implementar eliminación de facturas
    console.log('Eliminar factura:', id)
  }


  const handleExport = async () => {
    try {
      const result = await invoicesApi.export()
      // En un entorno real, aquí descargarías el archivo
      console.log('Archivo exportado:', result.file_path)
      alert(`Archivo exportado: ${result.file_path}`)
    } catch (error) {
      console.error('Error al exportar:', error)
      alert('Error al exportar las facturas')
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Cargando facturas...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Facturas</h1>
          <p className="mt-1 text-sm text-gray-500">
            Gestiona las facturas del sistema
          </p>
        </div>
        <div className="flex space-x-3">
          <button 
            onClick={handleExport}
            className="btn btn-secondary"
          >
            <Download className="h-4 w-4 mr-2" />
            Exportar Excel
          </button>
          <button 
            onClick={() => navigate('/invoices/create')}
            className="btn btn-primary"
          >
            <Plus className="h-4 w-4 mr-2" />
            Nueva Factura
          </button>
        </div>
      </div>

      {/* Componente de filtros */}
      <InvoiceFilters
        users={users}
        onFiltersChange={handleFiltersChange}
        onClearFilters={handleClearFilters}
      />

      <div className="card">
        <div className="card-content">
          {invoices.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No hay facturas registradas</p>
          ) : (
            <>
              {/* Vista de tarjetas para móviles */}
              <div className="block md:hidden space-y-4">
                {invoices.map((invoice) => (
                  <InvoiceCard
                    key={invoice.id}
                    invoice={invoice}
                    onValidate={(id, status) => setValidationInvoice({ id, status })}
                    onEdit={handleEditInvoice}
                    onDelete={handleDeleteInvoice}
                  />
                ))}
              </div>

              {/* Vista de tabla para desktop */}
              <div className="hidden md:block overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      ID
                    </th>
                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[200px]">
                      Proveedor
                    </th>
                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider hidden md:table-cell">
                      Usuario
                    </th>
                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Monto
                    </th>
                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider hidden lg:table-cell">
                      Categoría
                    </th>
                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Estado
                    </th>
                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider hidden sm:table-cell">
                      Fecha
                    </th>
                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Acciones
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {invoices.map((invoice) => (
                    <tr key={invoice.id} className="hover:bg-gray-50">
                      <td className="px-3 py-3 whitespace-nowrap text-sm font-medium text-gray-900">
                        #{invoice.id}
                      </td>
                      <td className="px-3 py-3">
                        <div className="text-sm font-medium text-gray-900 truncate max-w-[180px]" title={invoice.provider}>
                          {invoice.provider}
                        </div>
                        {invoice.description && (
                          <div className="text-xs text-gray-500 truncate max-w-[180px]" title={invoice.description}>
                            {invoice.description}
                          </div>
                        )}
                        {/* Mostrar información adicional en móvil */}
                        <div className="md:hidden text-xs text-gray-500 mt-1">
                          <div>{invoice.user.name}</div>
                          <div className="flex items-center space-x-2 mt-1">
                            <span className="inline-flex px-1.5 py-0.5 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">
                              {EXPENSE_CATEGORY_LABELS[invoice.category as ExpenseCategory]}
                            </span>
                            <span className="text-gray-400">•</span>
                            <span>{new Date(invoice.date).toLocaleDateString()}</span>
                          </div>
                        </div>
                      </td>
                      <td className="px-3 py-3 whitespace-nowrap hidden md:table-cell">
                        <div className="text-sm text-gray-900">{invoice.user.name}</div>
                        <div className="text-xs text-gray-500">{invoice.user.email}</div>
                      </td>
                      <td className="px-3 py-3 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          ${invoice.amount.toLocaleString()}
                        </div>
                        <div className="text-xs text-gray-500">
                          {PAYMENT_METHOD_LABELS[invoice.payment_method as PaymentMethod]}
                        </div>
                      </td>
                      <td className="px-3 py-3 whitespace-nowrap hidden lg:table-cell">
                        <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">
                          {EXPENSE_CATEGORY_LABELS[invoice.category as ExpenseCategory]}
                        </span>
                      </td>
                      <td className="px-3 py-3 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          INVOICE_STATUS_COLORS[invoice.status as InvoiceStatus]
                        }`}>
                          {INVOICE_STATUS_LABELS[invoice.status as InvoiceStatus]}
                        </span>
                      </td>
                      <td className="px-3 py-3 whitespace-nowrap text-sm text-gray-500 hidden sm:table-cell">
                        {new Date(invoice.date).toLocaleDateString()}
                      </td>
                      <td className="px-3 py-3 whitespace-nowrap text-sm font-medium">
                        <div className="flex space-x-1">
                          <button 
                            onClick={() => setValidationInvoice({ id: invoice.id, status: invoice.status as InvoiceStatus })}
                            className="text-blue-600 hover:text-blue-900 p-1 rounded hover:bg-blue-50"
                            title="Validar factura"
                          >
                            {invoice.status === InvoiceStatus.PENDING ? (
                              <CheckCircle className="h-4 w-4" />
                            ) : (
                              <Eye className="h-4 w-4" />
                            )}
                          </button>
                          <button 
                            onClick={() => handleEditInvoice(invoice.id)}
                            className="text-green-600 hover:text-green-900 p-1 rounded hover:bg-green-50" 
                            title="Editar"
                          >
                            <Edit className="h-4 w-4" />
                          </button>
                          <button 
                            onClick={() => handleDeleteInvoice(invoice.id)}
                            className="text-red-600 hover:text-red-900 p-1 rounded hover:bg-red-50" 
                            title="Eliminar"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
                </table>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Modal de validación */}
      {validationInvoice && (
        <InvoiceValidation
          invoiceId={validationInvoice.id}
          currentStatus={validationInvoice.status}
          onClose={() => setValidationInvoice(null)}
        />
      )}
    </div>
  )
}

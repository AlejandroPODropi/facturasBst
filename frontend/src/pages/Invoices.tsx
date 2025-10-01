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
  ExpenseCategory,
  Invoice
} from '../types'
import { Plus, Download, Edit, Trash2, CheckCircle, Eye, ChevronLeft, ChevronRight } from 'lucide-react'
import { InvoiceValidation } from '../components/InvoiceValidation'
import { InvoiceFilters } from '../components/InvoiceFilters'
import { InvoiceCard } from '../components/InvoiceCard'
import { EditInvoiceModal } from '../components/EditInvoiceModal'
import { DeleteInvoiceModal } from '../components/DeleteInvoiceModal'

export function Invoices() {
  const navigate = useNavigate()
  const [filters, setFilters] = useState<any>({})
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize] = useState(10)
  
  const queryParams = {
    ...filters,
    page: currentPage,
    size: pageSize
  }
  
  const { data: invoicesData, isLoading } = useQuery(['invoices', queryParams], () => invoicesApi.getAll(queryParams))
  const { data: users = [] } = useQuery('users', () => usersApi.getAll())
  
  const invoices = invoicesData?.items || []
  const totalPages = invoicesData?.pages || 1
  const totalItems = invoicesData?.total || 0
  
  const [validationInvoice, setValidationInvoice] = useState<{ id: number; status: InvoiceStatus } | null>(null)
  const [editInvoice, setEditInvoice] = useState<Invoice | null>(null)
  const [deleteInvoice, setDeleteInvoice] = useState<Invoice | null>(null)

  const handleFiltersChange = (newFilters: any) => {
    // Limpiar filtros vacíos
    const cleanFilters = Object.fromEntries(
      Object.entries(newFilters).filter(([_, value]) => value !== '')
    )
    setFilters(cleanFilters)
    setCurrentPage(1) // Reset to first page when filters change
  }

  const handleClearFilters = () => {
    setFilters({})
    setCurrentPage(1)
  }

  const handleEditInvoice = (invoice: Invoice) => {
    setEditInvoice(invoice)
  }

  const handleDeleteInvoice = (invoice: Invoice) => {
    setDeleteInvoice(invoice)
  }

  const handlePageChange = (page: number) => {
    setCurrentPage(page)
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
    <div className="space-y-4 md:space-y-6">
      <div className="flex flex-col md:flex-row md:justify-between md:items-center space-y-4 md:space-y-0">
        <div>
          <h1 className="text-lg md:text-xl lg:text-2xl font-bold text-gray-900">Facturas</h1>
          <p className="mt-1 text-sm text-gray-500">
            Gestiona las facturas del sistema
          </p>
        </div>
        <div className="flex flex-col md:flex-row space-y-2 md:space-y-0 md:space-x-3">
          <button 
            onClick={handleExport}
            className="btn-mobile btn-secondary w-full md:w-auto"
          >
            <Download className="h-4 w-4 mr-2" />
            Exportar Excel
          </button>
          <button 
            onClick={() => navigate('/invoices/create')}
            className="btn-mobile btn-primary w-full md:w-auto"
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
              {/* Vista de tarjetas para móviles (<640px) */}
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

              {/* Vista de tabla para tablet y desktop (≥640px) */}
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
                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider hidden lg:table-cell">
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
                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider hidden lg:table-cell">
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
                        {/* Mostrar información adicional en tablet */}
                        <div className="lg:hidden text-xs text-gray-500 mt-1">
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
                      <td className="px-3 py-3 whitespace-nowrap hidden lg:table-cell">
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
                      <td className="px-3 py-3 whitespace-nowrap text-sm text-gray-500 hidden lg:table-cell">
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
                            onClick={() => handleEditInvoice(invoice)}
                            className="text-green-600 hover:text-green-900 p-1 rounded hover:bg-green-50" 
                            title="Editar"
                          >
                            <Edit className="h-4 w-4" />
                          </button>
                          <button 
                            onClick={() => handleDeleteInvoice(invoice)}
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

        {/* Paginación */}
        {totalPages > 1 && (
          <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
            <div className="flex-1 flex justify-between sm:hidden">
              <button
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage === 1}
                className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Anterior
              </button>
              <button
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage === totalPages}
                className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Siguiente
              </button>
            </div>
            <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
              <div>
                <p className="text-sm text-gray-700">
                  Mostrando{' '}
                  <span className="font-medium">{(currentPage - 1) * pageSize + 1}</span>
                  {' '}a{' '}
                  <span className="font-medium">
                    {Math.min(currentPage * pageSize, totalItems)}
                  </span>
                  {' '}de{' '}
                  <span className="font-medium">{totalItems}</span>
                  {' '}resultados
                </p>
              </div>
              <div>
                <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                  <button
                    onClick={() => handlePageChange(currentPage - 1)}
                    disabled={currentPage === 1}
                    className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <ChevronLeft className="h-5 w-5" />
                  </button>
                  
                  {/* Páginas */}
                  {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                    let pageNum;
                    if (totalPages <= 5) {
                      pageNum = i + 1;
                    } else if (currentPage <= 3) {
                      pageNum = i + 1;
                    } else if (currentPage >= totalPages - 2) {
                      pageNum = totalPages - 4 + i;
                    } else {
                      pageNum = currentPage - 2 + i;
                    }
                    
                    return (
                      <button
                        key={pageNum}
                        onClick={() => handlePageChange(pageNum)}
                        className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                          currentPage === pageNum
                            ? 'z-10 bg-primary-50 border-primary-500 text-primary-600'
                            : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                        }`}
                      >
                        {pageNum}
                      </button>
                    );
                  })}
                  
                  <button
                    onClick={() => handlePageChange(currentPage + 1)}
                    disabled={currentPage === totalPages}
                    className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <ChevronRight className="h-5 w-5" />
                  </button>
                </nav>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Modal de validación */}
      {validationInvoice && (
        <InvoiceValidation
          invoiceId={validationInvoice.id}
          currentStatus={validationInvoice.status}
          onClose={() => setValidationInvoice(null)}
        />
      )}

      {/* Modal de edición */}
      <EditInvoiceModal
        invoice={editInvoice}
        isOpen={!!editInvoice}
        onClose={() => setEditInvoice(null)}
      />

      {/* Modal de eliminación */}
      <DeleteInvoiceModal
        invoice={deleteInvoice}
        isOpen={!!deleteInvoice}
        onClose={() => setDeleteInvoice(null)}
      />
    </div>
  )
}

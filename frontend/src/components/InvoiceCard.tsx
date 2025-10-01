import { 
  InvoiceStatus, 
  PaymentMethod, 
  ExpenseCategory,
  INVOICE_STATUS_LABELS,
  INVOICE_STATUS_COLORS,
  PAYMENT_METHOD_LABELS,
  EXPENSE_CATEGORY_LABELS
} from '../types'
import { CheckCircle, Eye, Edit, Trash2, Calendar, User, CreditCard, Tag } from 'lucide-react'

interface InvoiceCardProps {
  invoice: {
    id: number
    provider: string
    description?: string
    amount: number
    payment_method: PaymentMethod
    category: ExpenseCategory
    status: InvoiceStatus
    date: string
    file_path?: string
    user: {
      name: string
      email: string
    }
  }
  onValidate: (id: number, status: InvoiceStatus) => void
  onEdit: (id: number) => void
  onDelete: (id: number) => void
}

export function InvoiceCard({ invoice, onValidate, onEdit, onDelete }: InvoiceCardProps) {
  return (
    <div className="card hover:shadow-md transition-shadow">
      <div className="card-content">
        {/* Header con ID y estado */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2 min-w-0 flex-1">
            <span className="text-sm font-medium text-gray-900">#{invoice.id}</span>
            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
              INVOICE_STATUS_COLORS[invoice.status]
            }`}>
              {INVOICE_STATUS_LABELS[invoice.status]}
            </span>
          </div>
          <div className="flex space-x-1 flex-shrink-0">
            <button 
              onClick={() => onValidate(invoice.id, invoice.status)}
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
              onClick={() => onEdit(invoice.id)}
              className="text-green-600 hover:text-green-900 p-1 rounded hover:bg-green-50" 
              title="Editar"
            >
              <Edit className="h-4 w-4" />
            </button>
            <button 
              onClick={() => onDelete(invoice.id)}
              className="text-red-600 hover:text-red-900 p-1 rounded hover:bg-red-50" 
              title="Eliminar"
            >
              <Trash2 className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Información principal */}
        <div className="space-y-2">
          <div>
            <h3 className="text-sm font-medium text-gray-900 truncate" title={invoice.provider}>
              {invoice.provider}
            </h3>
            {invoice.description && (
              <p className="text-xs text-gray-500 truncate" title={invoice.description}>
                {invoice.description}
              </p>
            )}
          </div>

          {/* Monto destacado */}
          <div className="flex items-center justify-between">
            <div className="text-base lg:text-lg font-semibold text-gray-900">
              ${invoice.amount.toLocaleString()}
            </div>
            <div className="flex items-center space-x-1 text-xs text-gray-500">
              <CreditCard className="h-3 w-3 flex-shrink-0" />
              <span className="truncate">{PAYMENT_METHOD_LABELS[invoice.payment_method]}</span>
            </div>
          </div>

          {/* Información adicional */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-gray-500">
            <div className="flex items-center space-x-1 min-w-0">
              <User className="h-3 w-3 flex-shrink-0" />
              <span className="truncate" title={invoice.user.name}>
                {invoice.user.name}
              </span>
            </div>
            <div className="flex items-center space-x-1">
              <Calendar className="h-3 w-3 flex-shrink-0" />
              <span>{new Date(invoice.date).toLocaleDateString()}</span>
            </div>
          </div>

          {/* Categoría */}
          <div className="flex items-center space-x-1">
            <Tag className="h-3 w-3 text-gray-400 flex-shrink-0" />
            <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">
              {EXPENSE_CATEGORY_LABELS[invoice.category]}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

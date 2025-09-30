import { useState } from 'react'
import { 
  // InvoiceStatus, 
  // PaymentMethod, 
  // ExpenseCategory, 
  User,
  INVOICE_STATUS_LABELS,
  PAYMENT_METHOD_LABELS,
  EXPENSE_CATEGORY_LABELS
} from '../types'
import { Search, Filter, X, Calendar, User as UserIcon, Tag, CreditCard } from 'lucide-react'

interface InvoiceFiltersProps {
  users: User[]
  onFiltersChange: (filters: any) => void
  onClearFilters: () => void
}

export function InvoiceFilters({ users, onFiltersChange, onClearFilters }: InvoiceFiltersProps) {
  const [isExpanded, setIsExpanded] = useState(false)
  const [filters, setFilters] = useState({
    search_text: '',
    user_id: '',
    status: '',
    category: '',
    payment_method: '',
    start_date: '',
    end_date: '',
    provider: ''
  })

  const handleFilterChange = (key: string, value: string) => {
    const newFilters = { ...filters, [key]: value }
    setFilters(newFilters)
    onFiltersChange(newFilters)
  }

  const handleClearFilters = () => {
    const clearedFilters = {
      search_text: '',
      user_id: '',
      status: '',
      category: '',
      payment_method: '',
      start_date: '',
      end_date: '',
      provider: ''
    }
    setFilters(clearedFilters)
    onClearFilters()
  }

  const hasActiveFilters = Object.values(filters).some(value => value !== '')

  return (
    <div className="card mb-6">
      <div className="card-content">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <Filter className="h-5 w-5 text-gray-500 mr-2" />
            <h3 className="text-lg font-medium text-gray-900">Filtros</h3>
            {hasActiveFilters && (
              <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                Filtros activos
              </span>
            )}
          </div>
          <div className="flex items-center space-x-2">
            {hasActiveFilters && (
              <button
                onClick={handleClearFilters}
                className="text-sm text-gray-500 hover:text-gray-700 flex items-center"
              >
                <X className="h-4 w-4 mr-1" />
                Limpiar filtros
              </button>
            )}
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              {isExpanded ? 'Ocultar' : 'Mostrar'} filtros
            </button>
          </div>
        </div>

        {/* Búsqueda rápida */}
        <div className="mb-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar por proveedor o descripción..."
              value={filters.search_text}
              onChange={(e) => handleFilterChange('search_text', e.target.value)}
              className="input pl-10"
            />
          </div>
        </div>

        {isExpanded && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Filtro por usuario */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <UserIcon className="h-4 w-4 inline mr-1" />
                Usuario
              </label>
              <select
                value={filters.user_id}
                onChange={(e) => handleFilterChange('user_id', e.target.value)}
                className="input"
              >
                <option value="">Todos los usuarios</option>
                {users.map((user) => (
                  <option key={user.id} value={user.id}>
                    {user.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Filtro por estado */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Tag className="h-4 w-4 inline mr-1" />
                Estado
              </label>
              <select
                value={filters.status}
                onChange={(e) => handleFilterChange('status', e.target.value)}
                className="input"
              >
                <option value="">Todos los estados</option>
                {Object.entries(INVOICE_STATUS_LABELS).map(([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </select>
            </div>

            {/* Filtro por categoría */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Tag className="h-4 w-4 inline mr-1" />
                Categoría
              </label>
              <select
                value={filters.category}
                onChange={(e) => handleFilterChange('category', e.target.value)}
                className="input"
              >
                <option value="">Todas las categorías</option>
                {Object.entries(EXPENSE_CATEGORY_LABELS).map(([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </select>
            </div>

            {/* Filtro por método de pago */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <CreditCard className="h-4 w-4 inline mr-1" />
                Método de Pago
              </label>
              <select
                value={filters.payment_method}
                onChange={(e) => handleFilterChange('payment_method', e.target.value)}
                className="input"
              >
                <option value="">Todos los métodos</option>
                {Object.entries(PAYMENT_METHOD_LABELS).map(([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </select>
            </div>

            {/* Filtro por proveedor */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Proveedor
              </label>
              <input
                type="text"
                placeholder="Nombre del proveedor..."
                value={filters.provider}
                onChange={(e) => handleFilterChange('provider', e.target.value)}
                className="input"
              />
            </div>

            {/* Filtro por rango de fechas */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Calendar className="h-4 w-4 inline mr-1" />
                Rango de Fechas
              </label>
              <div className="space-y-2">
                <input
                  type="date"
                  placeholder="Fecha inicio"
                  value={filters.start_date}
                  onChange={(e) => handleFilterChange('start_date', e.target.value)}
                  className="input"
                />
                <input
                  type="date"
                  placeholder="Fecha fin"
                  value={filters.end_date}
                  onChange={(e) => handleFilterChange('end_date', e.target.value)}
                  className="input"
                />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

import { useQuery } from 'react-query'
import { usersApi, invoicesApi, dashboardApi } from '../services/api'
import { 
  Users, 
  FileText, 
  DollarSign, 
  Clock,
  CheckCircle,
  XCircle,
  Activity
} from 'lucide-react'
import { Chart } from '../components/Chart'
import { UserStats } from '../components/UserStats'
import { InvoiceTrends } from '../components/InvoiceTrends'
import { GmailIntegration } from '../components/GmailIntegration'

export function Dashboard() {
  // Consultas para datos básicos (mantener compatibilidad)
  const { data: users = [] } = useQuery('users', () => usersApi.getAll())
  const { data: invoicesData } = useQuery('invoices', () => invoicesApi.getAll())
  
  // Consultas para estadísticas avanzadas del dashboard
  const { data: dashboardStats, isLoading: statsLoading } = useQuery(
    'dashboard-stats',
    () => dashboardApi.getStats(),
    {
      refetchInterval: 30000, // Refrescar cada 30 segundos
    }
  )

  const invoices = invoicesData?.items || []
  const totalAmount = invoices.reduce((sum, invoice) => sum + invoice.amount, 0)
  const pendingInvoices = invoices.filter(invoice => invoice.status === 'pendiente').length
  const validatedInvoices = invoices.filter(invoice => invoice.status === 'validada').length
  const rejectedInvoices = invoices.filter(invoice => invoice.status === 'rechazada').length

  // Estadísticas básicas (fallback si no hay datos del dashboard)
  const basicStats = dashboardStats?.basic_stats || {
    total_users: users.length,
    total_invoices: invoices.length,
    total_amount: totalAmount,
    invoices_by_status: {
      pendiente: pendingInvoices,
      validada: validatedInvoices,
      rechazada: rejectedInvoices
    }
  }

  const stats = [
    {
      name: 'Total Usuarios',
      value: basicStats.total_users,
      icon: Users,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
    },
    {
      name: 'Total Facturas',
      value: basicStats.total_invoices,
      icon: FileText,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
    },
    {
      name: 'Monto Total',
      value: `$${basicStats.total_amount.toLocaleString()}`,
      icon: DollarSign,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-100',
    },
    {
      name: 'Facturas Pendientes',
      value: basicStats.invoices_by_status?.pendiente || 0,
      icon: Clock,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100',
    },
  ]

  const statusStats = [
    {
      name: 'Validadas',
      value: basicStats.invoices_by_status?.validada || 0,
      icon: CheckCircle,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
    },
    {
      name: 'Rechazadas',
      value: basicStats.invoices_by_status?.rechazada || 0,
      icon: XCircle,
      color: 'text-red-600',
      bgColor: 'bg-red-100',
    },
  ]

  // Preparar datos para gráficos
  const categoryData = dashboardStats?.category_distribution?.map((cat: any) => ({
    label: cat.category_label,
    value: cat.count,
    total_amount: cat.total_amount
  })) || []

  const paymentMethodData = dashboardStats?.payment_method_distribution?.map((method: any) => ({
    label: method.method_label,
    value: method.count,
    total_amount: method.total_amount
  })) || []

  return (
    <div className="space-y-4 md:space-y-6">
      <div>
        <h1 className="text-lg md:text-xl lg:text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Resumen del sistema de control de facturas
        </p>
      </div>

      {/* Stats Grid - Mobile: 1 col, Tablet: 2 cols, Desktop: 4 cols */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
        {stats.map((stat) => (
          <div key={stat.name} className="card">
            <div className="card-content">
              <div className="flex items-center">
                <div className={`flex-shrink-0 rounded-md p-3 ${stat.bgColor}`}>
                  <stat.icon className={`h-6 w-6 ${stat.color}`} />
                </div>
                <div className="ml-4 min-w-0 flex-1">
                  <p className="text-sm font-medium text-gray-500 truncate">{stat.name}</p>
                  <p className="text-xl md:text-2xl font-semibold text-gray-900 truncate">{stat.value}</p>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Status Stats - Mobile: 1 col, Tablet: 2 cols, Desktop: 4 cols */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
        {statusStats.map((stat) => (
          <div key={stat.name} className="card">
            <div className="card-content">
              <div className="flex items-center">
                <div className={`flex-shrink-0 rounded-md p-3 ${stat.bgColor}`}>
                  <stat.icon className={`h-6 w-6 ${stat.color}`} />
                </div>
                <div className="ml-4 min-w-0 flex-1">
                  <p className="text-sm font-medium text-gray-500 truncate">{stat.name}</p>
                  <p className="text-xl md:text-2xl font-semibold text-gray-900 truncate">{stat.value}</p>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Métricas de rendimiento - Mobile: 1 col, Tablet: 2 cols, Desktop: 3 cols */}
      {dashboardStats?.validation_performance && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
          <div className="card">
            <div className="card-content">
              <div className="flex items-center">
                <div className="flex-shrink-0 rounded-md p-3 bg-purple-100">
                  <Activity className="h-6 w-6 text-purple-600" />
                </div>
                <div className="ml-4 min-w-0 flex-1">
                  <p className="text-sm font-medium text-gray-500 truncate">Tasa de Validación</p>
                  <p className="text-xl md:text-2xl font-semibold text-gray-900 truncate">
                    {dashboardStats.validation_performance.validation_rate}%
                  </p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="card">
            <div className="card-content">
              <div className="flex items-center">
                <div className="flex-shrink-0 rounded-md p-3 bg-indigo-100">
                  <Clock className="h-6 w-6 text-indigo-600" />
                </div>
                <div className="ml-4 min-w-0 flex-1">
                  <p className="text-sm font-medium text-gray-500 truncate">Tiempo Promedio</p>
                  <p className="text-xl md:text-2xl font-semibold text-gray-900 truncate">
                    {dashboardStats.validation_performance.avg_validation_time_hours}h
                  </p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="card md:col-span-2 lg:col-span-1">
            <div className="card-content">
              <div className="flex items-center">
                <div className="flex-shrink-0 rounded-md p-3 bg-teal-100">
                  <CheckCircle className="h-6 w-6 text-teal-600" />
                </div>
                <div className="ml-4 min-w-0 flex-1">
                  <p className="text-sm font-medium text-gray-500 truncate">Total Validadas</p>
                  <p className="text-xl md:text-2xl font-semibold text-gray-900 truncate">
                    {dashboardStats.validation_performance.total_validated}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Gráficos y estadísticas avanzadas */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Tendencias mensuales */}
        <div className="lg:col-span-2">
          <InvoiceTrends 
            trends={dashboardStats?.monthly_trends || []} 
            isLoading={statsLoading}
          />
        </div>

        {/* Distribución por categorías */}
        <Chart
          title="Distribución por Categorías"
          data={categoryData}
          type="pie"
          height={300}
        />

        {/* Distribución por métodos de pago */}
        <Chart
          title="Distribución por Métodos de Pago"
          data={paymentMethodData}
          type="doughnut"
          height={300}
        />
      </div>

      {/* Estadísticas por usuario */}
      <UserStats 
        userStats={dashboardStats?.user_stats || []} 
        isLoading={statsLoading}
      />

      {/* Recent Invoices - Vista dual responsive */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-base md:text-lg font-medium text-gray-900">Facturas Recientes</h3>
        </div>
        <div className="card-content">
          {invoices.length === 0 ? (
            <p className="text-gray-500 text-center py-4">No hay facturas registradas</p>
          ) : (
            <>
              {/* Desktop Table - Solo visible en ≥1024px */}
              <div className="hidden lg:block overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Proveedor
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Usuario
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Monto
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Estado
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Fecha
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {invoices.slice(0, 5).map((invoice) => (
                      <tr key={invoice.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {invoice.provider}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {invoice.user.name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          ${invoice.amount.toLocaleString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            invoice.status === 'validada' ? 'bg-green-100 text-green-800' :
                            invoice.status === 'rechazada' ? 'bg-red-100 text-red-800' :
                            'bg-yellow-100 text-yellow-800'
                          }`}>
                            {invoice.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(invoice.date).toLocaleDateString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Mobile/Tablet Cards - Visible en <1024px */}
              <div className="lg:hidden space-y-3">
                {invoices.slice(0, 5).map((invoice) => (
                  <div key={invoice.id} className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <h4 className="text-sm font-medium text-gray-900 truncate">
                          {invoice.provider}
                        </h4>
                        <p className="text-xs text-gray-500 mt-1">
                          {invoice.user.name}
                        </p>
                      </div>
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        invoice.status === 'validada' ? 'bg-green-100 text-green-800' :
                        invoice.status === 'rechazada' ? 'bg-red-100 text-red-800' :
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {invoice.status}
                      </span>
                    </div>
                    <div className="mt-2 flex items-center justify-between">
                      <span className="text-sm font-semibold text-gray-900">
                        ${invoice.amount.toLocaleString()}
                      </span>
                      <span className="text-xs text-gray-500">
                        {new Date(invoice.date).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </div>

      {/* Gmail Integration */}
      <GmailIntegration />
    </div>
  )
}
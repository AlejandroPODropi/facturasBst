import React from 'react'
import { Chart } from './Chart'
import { TrendingUp, Calendar, DollarSign } from 'lucide-react'

interface TrendData {
  year: number
  month: number
  month_name: string
  count: number
  total_amount: number
}

interface InvoiceTrendsProps {
  trends: TrendData[]
  isLoading?: boolean
}

export function InvoiceTrends({ trends, isLoading = false }: InvoiceTrendsProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Tendencias Mensuales</h3>
        <div className="animate-pulse">
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    )
  }

  if (!trends || trends.length === 0) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Tendencias Mensuales</h3>
        <div className="text-center py-8">
          <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-3" />
          <p className="text-gray-500">No hay datos de tendencias disponibles</p>
        </div>
      </div>
    )
  }

  // Preparar datos para el gráfico
  const chartData = trends.map(trend => ({
    label: trend.month_name,
    value: trend.count,
    total_amount: trend.total_amount
  }))

  // Calcular estadísticas
  const totalInvoices = trends.reduce((sum, trend) => sum + trend.count, 0)
  const totalAmount = trends.reduce((sum, trend) => sum + trend.total_amount, 0)
  const avgInvoicesPerMonth = totalInvoices / trends.length
  const avgAmountPerMonth = totalAmount / trends.length

  // Encontrar el mes con más facturas
  const peakMonth = trends.reduce((max, trend) => 
    trend.count > max.count ? trend : max, trends[0]
  )

  // Encontrar el mes con mayor monto
  const peakAmountMonth = trends.reduce((max, trend) => 
    trend.total_amount > max.total_amount ? trend : max, trends[0]
  )

  return (
    <div className="space-y-6">
      {/* Gráfico de tendencias */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Tendencias Mensuales</h3>
        <Chart
          title=""
          data={chartData}
          type="line"
          height={300}
          className="border-0 p-0"
        />
      </div>

      {/* Estadísticas de tendencias */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total de facturas */}
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center">
            <div className="flex-shrink-0 rounded-md p-2 bg-blue-100">
              <TrendingUp className="h-5 w-5 text-blue-600" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Total Facturas</p>
              <p className="text-xl font-semibold text-gray-900">{totalInvoices}</p>
            </div>
          </div>
        </div>

        {/* Total de monto */}
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center">
            <div className="flex-shrink-0 rounded-md p-2 bg-green-100">
              <DollarSign className="h-5 w-5 text-green-600" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Monto Total</p>
              <p className="text-xl font-semibold text-gray-900">
                ${totalAmount.toLocaleString()}
              </p>
            </div>
          </div>
        </div>

        {/* Promedio mensual de facturas */}
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center">
            <div className="flex-shrink-0 rounded-md p-2 bg-purple-100">
              <Calendar className="h-5 w-5 text-purple-600" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Promedio/Mes</p>
              <p className="text-xl font-semibold text-gray-900">
                {avgInvoicesPerMonth.toFixed(1)}
              </p>
            </div>
          </div>
        </div>

        {/* Promedio mensual de monto */}
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center">
            <div className="flex-shrink-0 rounded-md p-2 bg-orange-100">
              <DollarSign className="h-5 w-5 text-orange-600" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Monto/Mes</p>
              <p className="text-xl font-semibold text-gray-900">
                ${avgAmountPerMonth.toLocaleString()}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Insights */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h4 className="text-md font-medium text-gray-900 mb-4">Insights</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-blue-50 rounded-lg">
            <h5 className="text-sm font-medium text-blue-900 mb-2">Mes con más facturas</h5>
            <p className="text-sm text-blue-700">
              <strong>{peakMonth.month_name}</strong> con {peakMonth.count} facturas
            </p>
          </div>
          <div className="p-4 bg-green-50 rounded-lg">
            <h5 className="text-sm font-medium text-green-900 mb-2">Mes con mayor monto</h5>
            <p className="text-sm text-green-700">
              <strong>{peakAmountMonth.month_name}</strong> con ${peakAmountMonth.total_amount.toLocaleString()}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

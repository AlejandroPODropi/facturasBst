// import React from 'react'
import { User, DollarSign, FileText, TrendingUp } from 'lucide-react'

interface UserStat {
  user_id: number
  name: string
  email: string
  invoice_count: number
  total_amount: number
  avg_amount: number
}

interface UserStatsProps {
  userStats: UserStat[]
  isLoading?: boolean
}

export function UserStats({ userStats, isLoading = false }: UserStatsProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Top Usuarios por Gastos</h3>
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="animate-pulse">
              <div className="flex items-center space-x-4">
                <div className="w-10 h-10 bg-gray-200 rounded-full"></div>
                <div className="flex-1">
                  <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                </div>
                <div className="text-right">
                  <div className="h-4 bg-gray-200 rounded w-16 mb-1"></div>
                  <div className="h-3 bg-gray-200 rounded w-12"></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (!userStats || userStats.length === 0) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Top Usuarios por Gastos</h3>
        <div className="text-center py-8">
          <User className="h-12 w-12 text-gray-400 mx-auto mb-3" />
          <p className="text-gray-500">No hay datos de usuarios disponibles</p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Top Usuarios por Gastos</h3>
      <div className="space-y-4">
        {userStats.map((user, index) => (
          <div key={user.user_id} className="flex items-center space-x-4 p-3 rounded-lg hover:bg-gray-50 transition-colors">
            {/* Ranking */}
            <div className="flex-shrink-0">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                index === 0 ? 'bg-yellow-100 text-yellow-800' :
                index === 1 ? 'bg-gray-100 text-gray-800' :
                index === 2 ? 'bg-orange-100 text-orange-800' :
                'bg-blue-100 text-blue-800'
              }`}>
                {index + 1}
              </div>
            </div>
            
            {/* Avatar */}
            <div className="flex-shrink-0">
              <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                <User className="h-5 w-5 text-blue-600" />
              </div>
            </div>
            
            {/* User Info */}
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate" title={user.name}>
                {user.name}
              </p>
              <p className="text-xs text-gray-500 truncate" title={user.email}>
                {user.email}
              </p>
            </div>
            
            {/* Stats */}
            <div className="flex-shrink-0 text-right">
              <div className="flex items-center space-x-4">
                {/* Total Amount */}
                <div className="text-right">
                  <div className="flex items-center space-x-1">
                    <DollarSign className="h-4 w-4 text-green-600" />
                    <span className="text-sm font-medium text-gray-900">
                      ${user.total_amount.toLocaleString()}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500">Total</p>
                </div>
                
                {/* Invoice Count */}
                <div className="text-right">
                  <div className="flex items-center space-x-1">
                    <FileText className="h-4 w-4 text-blue-600" />
                    <span className="text-sm font-medium text-gray-900">
                      {user.invoice_count}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500">Facturas</p>
                </div>
                
                {/* Average Amount */}
                <div className="text-right">
                  <div className="flex items-center space-x-1">
                    <TrendingUp className="h-4 w-4 text-purple-600" />
                    <span className="text-sm font-medium text-gray-900">
                      ${user.avg_amount.toLocaleString()}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500">Promedio</p>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {userStats.length > 5 && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <p className="text-xs text-gray-500 text-center">
            Mostrando los {userStats.length} usuarios con mayor gasto
          </p>
        </div>
      )}
    </div>
  )
}

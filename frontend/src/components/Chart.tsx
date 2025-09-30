// import React from 'react'

interface ChartProps {
  title: string
  data: any[]
  type: 'bar' | 'line' | 'pie' | 'doughnut'
  height?: number
  className?: string
}

export function Chart({ title, data, type, height = 300, className = '' }: ChartProps) {
  // Componente simple de gráfico usando CSS
  // En un proyecto real, usarías una librería como Chart.js o Recharts
  
  const renderBarChart = () => {
    if (!data || data.length === 0) {
      return (
        <div className="flex items-center justify-center h-full text-gray-500">
          No hay datos disponibles
        </div>
      )
    }

    const maxValue = Math.max(...data.map(item => item.value || item.count || item.total_amount || 0))
    
    return (
      <div className="space-y-2">
        {data.map((item, index) => {
          const value = item.value || item.count || item.total_amount || 0
          const percentage = maxValue > 0 ? (value / maxValue) * 100 : 0
          const label = item.label || item.name || item.category_label || item.method_label || `Item ${index + 1}`
          
          return (
            <div key={index} className="flex items-center space-x-3">
              <div className="w-20 text-sm text-gray-600 truncate" title={label}>
                {label}
              </div>
              <div className="flex-1 bg-gray-200 rounded-full h-6 relative">
                <div
                  className="bg-blue-500 h-6 rounded-full transition-all duration-500 ease-out"
                  style={{ width: `${percentage}%` }}
                />
                <div className="absolute inset-0 flex items-center justify-center text-xs font-medium text-gray-700">
                  {value.toLocaleString()}
                </div>
              </div>
            </div>
          )
        })}
      </div>
    )
  }

  const renderPieChart = () => {
    if (!data || data.length === 0) {
      return (
        <div className="flex items-center justify-center h-full text-gray-500">
          No hay datos disponibles
        </div>
      )
    }

    const total = data.reduce((sum, item) => sum + (item.value || item.count || item.total_amount || 0), 0)
    
    if (total === 0) {
      return (
        <div className="flex items-center justify-center h-full text-gray-500">
          No hay datos disponibles
        </div>
      )
    }

    let cumulativePercentage = 0
    
    return (
      <div className="relative w-full h-full">
        <svg viewBox="0 0 100 100" className="w-full h-full">
          {data.map((item, index) => {
            const value = item.value || item.count || item.total_amount || 0
            const percentage = (value / total) * 100
            const startAngle = (cumulativePercentage / 100) * 360
            const endAngle = ((cumulativePercentage + percentage) / 100) * 360
            
            cumulativePercentage += percentage
            
            const colors = [
              '#3B82F6', '#EF4444', '#10B981', '#F59E0B', 
              '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16'
            ]
            const color = colors[index % colors.length]
            
            const radius = 40
            const centerX = 50
            const centerY = 50
            
            const startAngleRad = (startAngle - 90) * (Math.PI / 180)
            const endAngleRad = (endAngle - 90) * (Math.PI / 180)
            
            const x1 = centerX + radius * Math.cos(startAngleRad)
            const y1 = centerY + radius * Math.sin(startAngleRad)
            const x2 = centerX + radius * Math.cos(endAngleRad)
            const y2 = centerY + radius * Math.sin(endAngleRad)
            
            const largeArcFlag = percentage > 50 ? 1 : 0
            
            const pathData = [
              `M ${centerX} ${centerY}`,
              `L ${x1} ${y1}`,
              `A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x2} ${y2}`,
              'Z'
            ].join(' ')
            
            return (
              <path
                key={index}
                d={pathData}
                fill={color}
                stroke="white"
                strokeWidth="0.5"
              />
            )
          })}
        </svg>
        
        {/* Leyenda */}
        <div className="absolute bottom-0 left-0 right-0 grid grid-cols-2 gap-1 text-xs">
          {data.map((item, index) => {
            const value = item.value || item.count || item.total_amount || 0
            const percentage = ((value / total) * 100).toFixed(1)
            const label = item.label || item.name || item.category_label || item.method_label || `Item ${index + 1}`
            const colors = [
              '#3B82F6', '#EF4444', '#10B981', '#F59E0B', 
              '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16'
            ]
            const color = colors[index % colors.length]
            
            return (
              <div key={index} className="flex items-center space-x-1">
                <div 
                  className="w-2 h-2 rounded-full" 
                  style={{ backgroundColor: color }}
                />
                <span className="truncate" title={label}>
                  {label} ({percentage}%)
                </span>
              </div>
            )
          })}
        </div>
      </div>
    )
  }

  const renderLineChart = () => {
    if (!data || data.length === 0) {
      return (
        <div className="flex items-center justify-center h-full text-gray-500">
          No hay datos disponibles
        </div>
      )
    }

    const maxValue = Math.max(...data.map(item => item.value || item.count || item.total_amount || 0))
    const minValue = Math.min(...data.map(item => item.value || item.count || item.total_amount || 0))
    const range = maxValue - minValue
    
    return (
      <div className="relative h-full">
        <svg viewBox="0 0 100 100" className="w-full h-full">
          {/* Grid lines */}
          {[0, 25, 50, 75, 100].map((y, index) => (
            <line
              key={index}
              x1="10"
              y1={y}
              x2="90"
              y2={y}
              stroke="#E5E7EB"
              strokeWidth="0.5"
            />
          ))}
          
          {/* Data line */}
          <polyline
            fill="none"
            stroke="#3B82F6"
            strokeWidth="2"
            points={data.map((item, index) => {
              const value = item.value || item.count || item.total_amount || 0
              const normalizedValue = range > 0 ? ((value - minValue) / range) * 80 + 10 : 50
              const x = 10 + (index / (data.length - 1)) * 80
              return `${x},${100 - normalizedValue}`
            }).join(' ')}
          />
          
          {/* Data points */}
          {data.map((item, index) => {
            const value = item.value || item.count || item.total_amount || 0
            const normalizedValue = range > 0 ? ((value - minValue) / range) * 80 + 10 : 50
            const x = 10 + (index / (data.length - 1)) * 80
            
            return (
              <circle
                key={index}
                cx={x}
                cy={100 - normalizedValue}
                r="2"
                fill="#3B82F6"
                stroke="white"
                strokeWidth="1"
              />
            )
          })}
        </svg>
        
        {/* X-axis labels */}
        <div className="absolute bottom-0 left-0 right-0 flex justify-between text-xs text-gray-500 px-2">
          {data.map((item, index) => {
            const label = item.label || item.name || item.month_name || `M${index + 1}`
            return (
              <span key={index} className="truncate" title={label}>
                {label}
              </span>
            )
          })}
        </div>
      </div>
    )
  }

  const renderChart = () => {
    switch (type) {
      case 'bar':
        return renderBarChart()
      case 'pie':
      case 'doughnut':
        return renderPieChart()
      case 'line':
        return renderLineChart()
      default:
        return renderBarChart()
    }
  }

  return (
    <div className={`bg-white rounded-lg border border-gray-200 p-4 ${className}`}>
      <h3 className="text-lg font-medium text-gray-900 mb-4">{title}</h3>
      <div style={{ height: `${height}px` }} className="relative">
        {renderChart()}
      </div>
    </div>
  )
}

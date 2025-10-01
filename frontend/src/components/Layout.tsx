import { Link, useLocation } from 'react-router-dom'
import { useState } from 'react'
import { 
  LayoutDashboard, 
  Users, 
  FileText, 
  Plus, 
  Building2,
  Scan,
  Menu,
  X
} from 'lucide-react'
import { clsx } from 'clsx'

interface LayoutProps {
  children: React.ReactNode
}

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Usuarios', href: '/users', icon: Users },
  { name: 'Facturas', href: '/invoices', icon: FileText },
  { name: 'Nueva Factura', href: '/invoices/create', icon: Plus },
  { name: 'OCR Facturas', href: '/ocr', icon: Scan },
]

export function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-gray-600 bg-opacity-75 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar - Colapsa automáticamente en <640px (sm) */}
      <div className={clsx(
        'fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out',
        // Desktop (lg: >1024px): siempre visible
        'lg:translate-x-0',
        // Tablet (md: 641-1024px): siempre visible
        'md:translate-x-0',
        // Móvil (sm: <640px): colapsable
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      )}>
        <div className="flex h-16 items-center justify-between px-6 border-b border-gray-200">
          <div className="flex items-center">
            <Building2 className="h-8 w-8 text-primary-600" />
            <span className="ml-2 text-xl font-semibold text-gray-900">
              Boosting
            </span>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="md:hidden p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100"
          >
            <X className="h-6 w-6" />
          </button>
        </div>
        
        <nav className="mt-6 px-3">
          <ul className="space-y-1">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href
              return (
                <li key={item.name}>
                  <Link
                    to={item.href}
                    onClick={() => setSidebarOpen(false)}
                    className={clsx(
                      'group flex items-center px-3 py-3 text-sm font-medium rounded-md transition-colors',
                      // Botones ≥44px de alto para móvil
                      'min-h-[44px]',
                      isActive
                        ? 'bg-primary-100 text-primary-700'
                        : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
                    )}
                  >
                    <item.icon
                      className={clsx(
                        'mr-3 h-5 w-5 flex-shrink-0',
                        isActive ? 'text-primary-500' : 'text-gray-400 group-hover:text-gray-500'
                      )}
                    />
                    {item.name}
                  </Link>
                </li>
              )
            })}
          </ul>
        </nav>
      </div>

      {/* Main content */}
      <div className="md:pl-64">
        {/* Mobile header - Solo visible en <640px */}
        <div className="md:hidden flex items-center justify-between h-16 px-4 bg-white border-b border-gray-200 shadow-sm">
          <button
            onClick={() => setSidebarOpen(true)}
            className="p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 min-h-[44px] min-w-[44px] flex items-center justify-center"
          >
            <Menu className="h-6 w-6" />
          </button>
          <div className="flex items-center">
            <Building2 className="h-6 w-6 text-primary-600" />
            <span className="ml-2 text-lg font-semibold text-gray-900">
              Boosting
            </span>
          </div>
          <div className="w-10" /> {/* Spacer for centering */}
        </div>

        <main className="py-4 md:py-6">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}

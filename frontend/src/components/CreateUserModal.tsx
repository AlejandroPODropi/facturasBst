import { useState } from 'react'
import { useMutation, useQueryClient } from 'react-query'
import { usersApi } from '../services/api'
import { UserRole, USER_ROLE_LABELS } from '../types'
import { XCircle, UserPlus } from 'lucide-react'

interface CreateUserModalProps {
  isOpen: boolean
  onClose: () => void
}

export function CreateUserModal({ isOpen, onClose }: CreateUserModalProps) {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    role: UserRole.COLLABORATOR,
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const queryClient = useQueryClient()

  const createUserMutation = useMutation(
    (userData: any) => usersApi.create(userData),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('users')
        onClose()
        resetForm()
      },
      onError: (error: any) => {
        console.error('Error al crear usuario:', error)
        const errorMessage = error.response?.data?.detail || 'Error al crear el usuario'
        alert(errorMessage)
      },
    }
  )

  const resetForm = () => {
    setFormData({
      name: '',
      email: '',
      role: UserRole.COLLABORATOR,
    })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.name.trim() || !formData.email.trim()) {
      alert('Por favor completa todos los campos requeridos')
      return
    }

    setIsSubmitting(true)
    try {
      await createUserMutation.mutateAsync(formData)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleClose = () => {
    resetForm()
    onClose()
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <div className="mx-auto flex items-center justify-center h-8 w-8 rounded-full bg-blue-100 mr-3">
              <UserPlus className="h-4 w-4 text-blue-600" />
            </div>
            <h3 className="text-lg font-medium text-gray-900">
              Nuevo Usuario
            </h3>
          </div>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <XCircle className="h-6 w-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
              Nombre Completo *
            </label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              required
              className="input"
              placeholder="Ingresa el nombre completo"
            />
          </div>

          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
              Correo Electrónico *
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              required
              className="input"
              placeholder="usuario@boosting.com"
            />
          </div>

          <div>
            <label htmlFor="role" className="block text-sm font-medium text-gray-700 mb-2">
              Rol *
            </label>
            <select
              id="role"
              name="role"
              value={formData.role}
              onChange={handleInputChange}
              required
              className="input"
            >
              {Object.entries(USER_ROLE_LABELS).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={handleClose}
              className="btn btn-secondary"
              disabled={isSubmitting}
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !formData.name.trim() || !formData.email.trim()}
              className="btn btn-primary"
            >
              {isSubmitting ? 'Creando...' : 'Crear Usuario'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

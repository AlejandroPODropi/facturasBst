import { useState, useEffect } from 'react'
import { useMutation, useQueryClient } from 'react-query'
import { usersApi } from '../services/api'
import { User as UserType, UserRole, USER_ROLE_LABELS } from '../types'
import { XCircle, User } from 'lucide-react'

interface EditUserModalProps {
  user: UserType | null
  isOpen: boolean
  onClose: () => void
}

export function EditUserModal({ user, isOpen, onClose }: EditUserModalProps) {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    role: UserRole.COLLABORATOR,
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const queryClient = useQueryClient()

  const updateUserMutation = useMutation(
    ({ id, userData }: { id: number; userData: any }) => usersApi.update(id, userData),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('users')
        onClose()
      },
      onError: (error: any) => {
        console.error('Error al actualizar usuario:', error)
        const errorMessage = error.response?.data?.detail || 'Error al actualizar el usuario'
        alert(errorMessage)
      },
    }
  )

  useEffect(() => {
    if (user) {
      setFormData({
        name: user.name,
        email: user.email,
        role: user.role as UserRole,
      })
    }
  }, [user])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!user) return

    if (!formData.name.trim() || !formData.email.trim()) {
      alert('Por favor completa todos los campos requeridos')
      return
    }

    setIsSubmitting(true)
    try {
      await updateUserMutation.mutateAsync({
        id: user.id,
        userData: formData
      })
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

  if (!isOpen || !user) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <div className="mx-auto flex items-center justify-center h-8 w-8 rounded-full bg-green-100 mr-3">
              <User className="h-4 w-4 text-green-600" />
            </div>
            <h3 className="text-lg font-medium text-gray-900">
              Editar Usuario
            </h3>
          </div>
          <button
            onClick={onClose}
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

          <div className="bg-gray-50 p-3 rounded-md">
            <p className="text-sm text-gray-600">
              <strong>ID:</strong> {user.id}
            </p>
            <p className="text-sm text-gray-600">
              <strong>Fecha de registro:</strong> {new Date(user.created_at).toLocaleDateString()}
            </p>
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
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
              {isSubmitting ? 'Actualizando...' : 'Actualizar Usuario'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

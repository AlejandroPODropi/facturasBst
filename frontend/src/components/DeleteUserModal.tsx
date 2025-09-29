import { useState } from 'react'
import { useMutation, useQueryClient } from 'react-query'
import { usersApi } from '../services/api'
import { User } from '../types'
import { XCircle, AlertTriangle, Trash2 } from 'lucide-react'

interface DeleteUserModalProps {
  user: User | null
  isOpen: boolean
  onClose: () => void
}

export function DeleteUserModal({ user, isOpen, onClose }: DeleteUserModalProps) {
  const [isDeleting, setIsDeleting] = useState(false)
  const queryClient = useQueryClient()

  const deleteUserMutation = useMutation(
    (id: number) => usersApi.delete(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('users')
        onClose()
      },
      onError: (error: any) => {
        console.error('Error al eliminar usuario:', error)
        const errorMessage = error.response?.data?.detail || 'Error al eliminar el usuario'
        alert(errorMessage)
      },
    }
  )

  const handleDelete = async () => {
    if (!user) return

    setIsDeleting(true)
    try {
      await deleteUserMutation.mutateAsync(user.id)
    } finally {
      setIsDeleting(false)
    }
  }

  if (!isOpen || !user) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <div className="mx-auto flex items-center justify-center h-8 w-8 rounded-full bg-red-100 mr-3">
              <AlertTriangle className="h-4 w-4 text-red-600" />
            </div>
            <h3 className="text-lg font-medium text-gray-900">
              Eliminar Usuario
            </h3>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <XCircle className="h-6 w-6" />
          </button>
        </div>

        <div className="space-y-4">
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <AlertTriangle className="h-5 w-5 text-red-400" />
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">
                  ¿Estás seguro de que quieres eliminar este usuario?
                </h3>
                <div className="mt-2 text-sm text-red-700">
                  <p>Esta acción no se puede deshacer. Se eliminará permanentemente:</p>
                  <ul className="list-disc list-inside mt-1">
                    <li>El usuario y todos sus datos</li>
                    <li>Las facturas asociadas al usuario</li>
                    <li>El historial de transacciones</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-gray-50 p-4 rounded-md">
            <h4 className="text-sm font-medium text-gray-900 mb-2">Información del usuario:</h4>
            <div className="space-y-1 text-sm text-gray-600">
              <p><strong>Nombre:</strong> {user.name}</p>
              <p><strong>Email:</strong> {user.email}</p>
              <p><strong>Rol:</strong> {user.role}</p>
              <p><strong>ID:</strong> {user.id}</p>
              <p><strong>Registrado:</strong> {new Date(user.created_at).toLocaleDateString()}</p>
            </div>
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="btn btn-secondary"
              disabled={isDeleting}
            >
              Cancelar
            </button>
            <button
              onClick={handleDelete}
              disabled={isDeleting}
              className="btn btn-error"
            >
              {isDeleting ? (
                'Eliminando...'
              ) : (
                <>
                  <Trash2 className="h-4 w-4 mr-2" />
                  Eliminar Usuario
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

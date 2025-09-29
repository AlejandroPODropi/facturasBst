"""
Pruebas unitarias para endpoints de usuarios.
Cubre casos de éxito, borde y fallo.
"""

import pytest
from fastapi.testclient import TestClient
from src.models import UserRole


class TestUserEndpoints:
    """Clase de pruebas para endpoints de usuarios."""
    
    def test_create_user_success(self, client, test_user):
        """
        Caso de éxito: Crear usuario válido.
        
        Verifica que se puede crear un usuario con datos válidos.
        """
        response = client.post("/api/v1/users/", json=test_user)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == test_user["name"]
        assert data["email"] == test_user["email"]
        assert data["role"] == test_user["role"]
        assert "id" in data
        assert "created_at" in data
    
    def test_create_user_duplicate_email(self, client, test_user):
        """
        Caso de fallo: Crear usuario con email duplicado.
        
        Verifica que no se puede crear un usuario con un email ya existente.
        """
        # Crear primer usuario
        client.post("/api/v1/users/", json=test_user)
        
        # Intentar crear segundo usuario con mismo email
        response = client.post("/api/v1/users/", json=test_user)
        
        assert response.status_code == 400
        assert "email ya está registrado" in response.json()["detail"]
    
    def test_create_user_invalid_email(self, client):
        """
        Caso de fallo: Crear usuario con email inválido.
        
        Verifica que no se puede crear un usuario con formato de email inválido.
        """
        invalid_user = {
            "name": "Test User",
            "email": "invalid-email",
            "role": UserRole.COLLABORATOR
        }
        
        response = client.post("/api/v1/users/", json=invalid_user)
        
        assert response.status_code == 422  # Validation error
    
    def test_create_user_empty_name(self, client):
        """
        Caso de borde: Crear usuario con nombre vacío.
        
        Verifica que no se puede crear un usuario sin nombre.
        """
        invalid_user = {
            "name": "",
            "email": "test@boosting.com",
            "role": UserRole.COLLABORATOR
        }
        
        response = client.post("/api/v1/users/", json=invalid_user)
        
        assert response.status_code == 422  # Validation error
    
    def test_get_users_success(self, client, test_user):
        """
        Caso de éxito: Obtener lista de usuarios.
        
        Verifica que se puede obtener la lista de usuarios.
        """
        # Crear algunos usuarios
        for i in range(3):
            user_data = {**test_user, "email": f"user{i}@boosting.com"}
            client.post("/api/v1/users/", json=user_data)
        
        response = client.get("/api/v1/users/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all("id" in user for user in data)
    
    def test_get_users_pagination(self, client, test_user):
        """
        Caso de borde: Paginación de usuarios.
        
        Verifica que la paginación funciona correctamente.
        """
        # Crear 5 usuarios
        for i in range(5):
            user_data = {**test_user, "email": f"user{i}@boosting.com"}
            client.post("/api/v1/users/", json=user_data)
        
        # Obtener primera página
        response = client.get("/api/v1/users/?skip=0&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        
        # Obtener segunda página
        response = client.get("/api/v1/users/?skip=2&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
    
    def test_get_user_success(self, client, created_user):
        """
        Caso de éxito: Obtener usuario específico.
        
        Verifica que se puede obtener un usuario por ID.
        """
        response = client.get(f"/api/v1/users/{created_user['id']}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_user["id"]
        assert data["name"] == created_user["name"]
    
    def test_get_user_not_found(self, client):
        """
        Caso de fallo: Obtener usuario inexistente.
        
        Verifica que se retorna error 404 para usuario no encontrado.
        """
        response = client.get("/api/v1/users/999")
        
        assert response.status_code == 404
        assert "Usuario no encontrado" in response.json()["detail"]
    
    def test_update_user_success(self, client, created_user):
        """
        Caso de éxito: Actualizar usuario existente.
        
        Verifica que se puede actualizar un usuario con datos válidos.
        """
        update_data = {
            "name": "Juan Carlos Pérez",
            "role": UserRole.ACCOUNTING_ASSISTANT
        }
        
        response = client.put(f"/api/v1/users/{created_user['id']}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["role"] == update_data["role"]
        assert data["email"] == created_user["email"]  # No se cambió
    
    def test_update_user_duplicate_email(self, client, test_user):
        """
        Caso de fallo: Actualizar usuario con email duplicado.
        
        Verifica que no se puede actualizar un usuario con un email ya existente.
        """
        # Crear dos usuarios
        user1 = {**test_user, "email": "user1@boosting.com"}
        user2 = {**test_user, "email": "user2@boosting.com"}
        
        response1 = client.post("/api/v1/users/", json=user1)
        response2 = client.post("/api/v1/users/", json=user2)
        
        user1_id = response1.json()["id"]
        
        # Intentar cambiar email del primer usuario al del segundo
        update_data = {"email": "user2@boosting.com"}
        response = client.put(f"/api/v1/users/{user1_id}", json=update_data)
        
        assert response.status_code == 400
        assert "email ya está registrado" in response.json()["detail"]
    
    def test_update_user_not_found(self, client):
        """
        Caso de fallo: Actualizar usuario inexistente.
        
        Verifica que se retorna error 404 para usuario no encontrado.
        """
        update_data = {"name": "Nuevo Nombre"}
        
        response = client.put("/api/v1/users/999", json=update_data)
        
        assert response.status_code == 404
        assert "Usuario no encontrado" in response.json()["detail"]
    
    def test_delete_user_success(self, client, created_user):
        """
        Caso de éxito: Eliminar usuario existente.
        
        Verifica que se puede eliminar un usuario.
        """
        response = client.delete(f"/api/v1/users/{created_user['id']}")
        
        assert response.status_code == 204
        
        # Verificar que el usuario ya no existe
        response = client.get(f"/api/v1/users/{created_user['id']}")
        assert response.status_code == 404
    
    def test_delete_user_not_found(self, client):
        """
        Caso de fallo: Eliminar usuario inexistente.
        
        Verifica que se retorna error 404 para usuario no encontrado.
        """
        response = client.delete("/api/v1/users/999")
        
        assert response.status_code == 404
        assert "Usuario no encontrado" in response.json()["detail"]

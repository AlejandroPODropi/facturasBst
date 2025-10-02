"""
Servicio para manejo de Google Secret Manager.
Permite almacenar y recuperar tokens de OAuth de forma persistente.
"""

import os
import json
import logging
from typing import Optional, Dict, Any
from google.cloud import secretmanager
from google.auth.exceptions import DefaultCredentialsError

logger = logging.getLogger(__name__)

class SecretManagerService:
    """Servicio para manejo de Google Secret Manager."""
    
    def __init__(self, project_id: str = None):
        """
        Inicializar el servicio de Secret Manager.
        
        Args:
            project_id: ID del proyecto de Google Cloud. Si no se proporciona,
                       se intentará obtener automáticamente.
        """
        self.project_id = project_id or self._get_project_id()
        self.client = None
        self._initialize_client()
    
    def _get_project_id(self) -> str:
        """Obtener el ID del proyecto de Google Cloud."""
        # Intentar obtener desde variable de entorno
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        if project_id:
            return project_id
        
        # Intentar obtener desde metadata del servidor
        try:
            import requests
            response = requests.get(
                'http://metadata.google.internal/computeMetadata/v1/project/project-id',
                headers={'Metadata-Flavor': 'Google'},
                timeout=5
            )
            if response.status_code == 200:
                return response.text
        except Exception as e:
            logger.warning(f"No se pudo obtener project_id desde metadata: {e}")
        
        # Fallback: usar el project_id del archivo de configuración
        return "facturasbst"
    
    def _initialize_client(self):
        """Inicializar el cliente de Secret Manager."""
        try:
            self.client = secretmanager.SecretManagerServiceClient()
            logger.info(f"Cliente de Secret Manager inicializado para proyecto: {self.project_id}")
        except DefaultCredentialsError as e:
            logger.error(f"Error inicializando Secret Manager: {e}")
            self.client = None
        except Exception as e:
            logger.error(f"Error inesperado inicializando Secret Manager: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Verificar si Secret Manager está disponible."""
        return self.client is not None
    
    def create_secret(self, secret_id: str, description: str = "") -> bool:
        """
        Crear un secreto en Secret Manager.
        
        Args:
            secret_id: ID del secreto
            description: Descripción del secreto
            
        Returns:
            True si se creó exitosamente, False en caso contrario
        """
        if not self.is_available():
            logger.error("Secret Manager no está disponible")
            return False
        
        try:
            parent = f"projects/{self.project_id}"
            
            # Verificar si el secreto ya existe
            if self.secret_exists(secret_id):
                logger.info(f"El secreto {secret_id} ya existe")
                return True
            
            # Crear el secreto
            secret = {
                "replication": {
                    "automatic": {}
                }
            }
            
            if description:
                secret["labels"] = {"description": description}
            
            response = self.client.create_secret(
                request={
                    "parent": parent,
                    "secret_id": secret_id,
                    "secret": secret,
                }
            )
            
            logger.info(f"Secreto {secret_id} creado exitosamente: {response.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creando secreto {secret_id}: {e}")
            return False
    
    def secret_exists(self, secret_id: str) -> bool:
        """
        Verificar si un secreto existe.
        
        Args:
            secret_id: ID del secreto
            
        Returns:
            True si existe, False en caso contrario
        """
        if not self.is_available():
            return False
        
        try:
            name = f"projects/{self.project_id}/secrets/{secret_id}"
            self.client.get_secret(request={"name": name})
            return True
        except Exception:
            return False
    
    def store_secret(self, secret_id: str, secret_data: str, description: str = "") -> bool:
        """
        Almacenar un secreto en Secret Manager.
        
        Args:
            secret_id: ID del secreto
            secret_data: Datos del secreto
            description: Descripción del secreto
            
        Returns:
            True si se almacenó exitosamente, False en caso contrario
        """
        if not self.is_available():
            logger.error("Secret Manager no está disponible")
            return False
        
        try:
            # Crear el secreto si no existe
            if not self.secret_exists(secret_id):
                if not self.create_secret(secret_id, description):
                    return False
            
            # Agregar una nueva versión del secreto
            parent = f"projects/{self.project_id}/secrets/{secret_id}"
            
            response = self.client.add_secret_version(
                request={
                    "parent": parent,
                    "payload": {
                        "data": secret_data.encode("UTF-8")
                    }
                }
            )
            
            logger.info(f"Secreto {secret_id} almacenado exitosamente: {response.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error almacenando secreto {secret_id}: {e}")
            return False
    
    def retrieve_secret(self, secret_id: str, version: str = "latest") -> Optional[str]:
        """
        Recuperar un secreto de Secret Manager.
        
        Args:
            secret_id: ID del secreto
            version: Versión del secreto (default: "latest")
            
        Returns:
            Contenido del secreto o None si no se pudo recuperar
        """
        if not self.is_available():
            logger.error("Secret Manager no está disponible")
            return None
        
        try:
            name = f"projects/{self.project_id}/secrets/{secret_id}/versions/{version}"
            
            response = self.client.access_secret_version(request={"name": name})
            
            secret_data = response.payload.data.decode("UTF-8")
            logger.info(f"Secreto {secret_id} recuperado exitosamente")
            return secret_data
            
        except Exception as e:
            logger.warning(f"Error recuperando secreto {secret_id}: {e}")
            return None
    
    def delete_secret(self, secret_id: str) -> bool:
        """
        Eliminar un secreto de Secret Manager.
        
        Args:
            secret_id: ID del secreto
            
        Returns:
            True si se eliminó exitosamente, False en caso contrario
        """
        if not self.is_available():
            logger.error("Secret Manager no está disponible")
            return False
        
        try:
            name = f"projects/{self.project_id}/secrets/{secret_id}"
            
            self.client.delete_secret(request={"name": name})
            
            logger.info(f"Secreto {secret_id} eliminado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error eliminando secreto {secret_id}: {e}")
            return False
    
    def list_secrets(self) -> list:
        """
        Listar todos los secretos del proyecto.
        
        Returns:
            Lista de IDs de secretos
        """
        if not self.is_available():
            logger.error("Secret Manager no está disponible")
            return []
        
        try:
            parent = f"projects/{self.project_id}"
            
            secrets = []
            for secret in self.client.list_secrets(request={"parent": parent}):
                secret_id = secret.name.split("/")[-1]
                secrets.append(secret_id)
            
            return secrets
            
        except Exception as e:
            logger.error(f"Error listando secretos: {e}")
            return []


# Instancia global del servicio
secret_manager_service = SecretManagerService()

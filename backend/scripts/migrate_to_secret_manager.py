#!/usr/bin/env python3
"""
Script para migrar credenciales de Gmail a Google Secret Manager.
Este script debe ejecutarse una vez para migrar las credenciales existentes.
"""

import os
import sys
import json
import logging
from pathlib import Path

# Agregar el directorio src al path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from services.secret_manager import secret_manager_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_credentials():
    """Migrar credenciales de Gmail a Secret Manager."""
    
    # Verificar si Secret Manager está disponible
    if not secret_manager_service.is_available():
        logger.error("Secret Manager no está disponible. Verifica la configuración de Google Cloud.")
        return False
    
    logger.info("Secret Manager está disponible")
    
    # Migrar credenciales
    credentials_file = "credentials.json"
    if os.path.exists(credentials_file):
        try:
            with open(credentials_file, 'r') as f:
                credentials_data = json.load(f)
            
            # Verificar que las credenciales sean válidas
            if 'installed' not in credentials_data:
                logger.error("Formato de credentials.json inválido")
                return False
            
            # Guardar en Secret Manager
            success = secret_manager_service.store_secret(
                "gmail-oauth-credentials",
                json.dumps(credentials_data),
                "Gmail OAuth Credentials para Facturas BST"
            )
            
            if success:
                logger.info("✅ Credenciales migradas exitosamente a Secret Manager")
                return True
            else:
                logger.error("❌ Error migrando credenciales a Secret Manager")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error leyendo credentials.json: {e}")
            return False
    else:
        logger.warning("⚠️  Archivo credentials.json no encontrado")
        return False

def migrate_token():
    """Migrar token de Gmail a Secret Manager."""
    
    token_file = "token.json"
    if os.path.exists(token_file):
        try:
            with open(token_file, 'r') as f:
                token_data = f.read()
            
            # Verificar que el token sea válido
            try:
                json.loads(token_data)
            except json.JSONDecodeError:
                logger.error("Formato de token.json inválido")
                return False
            
            # Guardar en Secret Manager
            success = secret_manager_service.store_secret(
                "gmail-oauth-token",
                token_data,
                "Gmail OAuth Token para Facturas BST"
            )
            
            if success:
                logger.info("✅ Token migrado exitosamente a Secret Manager")
                return True
            else:
                logger.error("❌ Error migrando token a Secret Manager")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error leyendo token.json: {e}")
            return False
    else:
        logger.info("ℹ️  Archivo token.json no encontrado (esto es normal si no hay token)")
        return True

def main():
    """Función principal."""
    logger.info("🚀 Iniciando migración a Secret Manager...")
    
    # Cambiar al directorio del backend
    backend_dir = Path(__file__).parent.parent
    os.chdir(backend_dir)
    
    # Migrar credenciales
    credentials_success = migrate_credentials()
    
    # Migrar token
    token_success = migrate_token()
    
    if credentials_success and token_success:
        logger.info("🎉 Migración completada exitosamente!")
        logger.info("📝 Próximos pasos:")
        logger.info("   1. Despliega la nueva versión del backend")
        logger.info("   2. Verifica que Gmail funcione correctamente")
        logger.info("   3. Opcionalmente, elimina los archivos locales credentials.json y token.json")
        return True
    else:
        logger.error("❌ Migración falló. Revisa los errores anteriores.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

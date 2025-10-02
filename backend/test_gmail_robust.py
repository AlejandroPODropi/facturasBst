#!/usr/bin/env python3
"""
Script para probar el servicio robusto de Gmail.
"""

import os
import sys
sys.path.append('src')

from src.services.gmail_service_robust import RobustGmailService

def test_gmail_robust():
    """Probar el servicio robusto de Gmail."""
    print("🔐 Probando servicio robusto de Gmail...")
    
    try:
        gmail_service = RobustGmailService()
        print("✅ RobustGmailService creado correctamente")
        
        # Verificar configuración
        print("\n🔍 Verificando configuración...")
        config_status = gmail_service.check_configuration()
        print(f"   - Credentials file exists: {config_status['credentials_file_exists']}")
        print(f"   - Token file exists: {config_status['token_file_exists']}")
        print(f"   - Is configured: {config_status['is_configured']}")
        
        if not config_status['is_configured']:
            print(f"❌ Configuración incompleta: {config_status['error_message']}")
            print("\n📋 Para configurar Gmail:")
            print("   1. Ve a Google Cloud Console")
            print("   2. Crea un proyecto y habilita Gmail API")
            print("   3. Crea credenciales OAuth 2.0")
            print("   4. Descarga credentials.json")
            print("   5. Colócalo en la raíz del backend")
            return False
        
        # Probar autenticación
        print("\n🔑 Probando autenticación...")
        auth_result = gmail_service.authenticate()
        
        if auth_result['success']:
            print("🎉 ¡Autenticación exitosa!")
            print("✅ Token guardado en token.json")
            
            # Probar búsqueda de emails
            print("\n📧 Probando búsqueda de emails...")
            search_result = gmail_service.search_emails_safe("in:inbox", 5)
            
            if search_result['success']:
                print(f"✅ Búsqueda exitosa: {search_result['total']} emails encontrados")
                
                # Probar estadísticas
                print("\n📊 Probando estadísticas...")
                stats_result = gmail_service.get_stats_safe()
                
                if stats_result['success']:
                    print("✅ Estadísticas obtenidas:")
                    print(f"   - Total emails (7d): {stats_result['total_emails_7d']}")
                    print(f"   - Con adjuntos (7d): {stats_result['emails_with_attachments_7d']}")
                    print(f"   - No leídos (7d): {stats_result['unread_emails_7d']}")
                    print(f"   - Tasa adjuntos: {stats_result['attachment_rate']:.2f}%")
                else:
                    print(f"⚠️  Error en estadísticas: {stats_result['error_message']}")
                
                return True
            else:
                print(f"⚠️  Error en búsqueda: {search_result['error_message']}")
                return False
        else:
            print(f"❌ Error en autenticación: {auth_result['error_message']}")
            if auth_result['requires_setup']:
                print("\n📋 Se requiere configuración adicional")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_endpoints():
    """Probar endpoints de Gmail."""
    print("\n🌐 Probando endpoints de Gmail...")
    
    try:
        import requests
        
        # Probar endpoint de estado
        print("   - Probando /api/v1/gmail/auth/status...")
        response = requests.get("http://localhost:8000/api/v1/gmail/auth/status")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Estado: {data['message']}")
        else:
            print(f"   ❌ Error: {response.status_code}")
        
        # Probar endpoint de configuración
        print("   - Probando /api/v1/gmail/config/check...")
        response = requests.get("http://localhost:8000/api/v1/gmail/config/check")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Configuración: {'OK' if data['is_configured'] else 'Requiere setup'}")
        else:
            print(f"   ❌ Error: {response.status_code}")
            
    except ImportError:
        print("   ⚠️  requests no disponible, saltando pruebas de endpoints")
    except Exception as e:
        print(f"   ❌ Error probando endpoints: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas del servicio robusto de Gmail\n")
    
    success = test_gmail_robust()
    
    if success:
        print("\n🎉 ¡Gmail API está funcionando correctamente!")
        test_endpoints()
    else:
        print("\n⚠️  Gmail API requiere configuración")
        print("\n📋 Pasos para configurar:")
        print("   1. Ve a https://console.cloud.google.com/")
        print("   2. Crea un proyecto o selecciona uno existente")
        print("   3. Habilita Gmail API")
        print("   4. Crea credenciales OAuth 2.0 (Desktop application)")
        print("   5. Descarga el archivo JSON")
        print("   6. Renómbralo a 'credentials.json'")
        print("   7. Colócalo en la raíz del backend")
        print("   8. Ejecuta este script nuevamente")
    
    print("\n✨ Pruebas completadas")

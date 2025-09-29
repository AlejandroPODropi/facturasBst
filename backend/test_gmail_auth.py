#!/usr/bin/env python3
"""
Script simple para probar la autenticación Gmail.
"""

import os
import sys
sys.path.append('src')

from src.services.gmail_service import GmailService

def test_gmail_auth():
    """Probar autenticación Gmail."""
    print("🔐 Iniciando autenticación Gmail...")
    
    try:
        gmail_service = GmailService()
        print("✅ GmailService creado correctamente")
        
        print("🔑 Intentando autenticar...")
        is_authenticated = gmail_service.authenticate()
        
        if is_authenticated:
            print("🎉 ¡Autenticación exitosa!")
            print("✅ Token guardado en token.json")
            return True
        else:
            print("❌ Error en la autenticación")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_gmail_auth()
    if success:
        print("\n🚀 ¡Gmail API está listo para usar!")
    else:
        print("\n⚠️  Revisa la configuración de Google Cloud Console")

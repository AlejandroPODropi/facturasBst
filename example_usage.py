"""
Ejemplo de uso de la API de Control de Facturas Boosting.
Este archivo muestra cómo interactuar con los endpoints principales.
"""

import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://127.0.0.1:8000"
API_BASE = f"{BASE_URL}/api/v1"

def create_user_example():
    """Ejemplo de creación de usuario."""
    user_data = {
        "name": "Juan Pérez",
        "email": "juan.perez@boosting.com",
        "role": "colaborador"
    }
    
    response = requests.post(f"{API_BASE}/users/", json=user_data)
    print(f"Crear usuario: {response.status_code}")
    if response.status_code == 201:
        return response.json()
    return None

def create_invoice_example(user_id):
    """Ejemplo de creación de factura."""
    invoice_data = {
        "date": "2024-01-15T10:30:00",
        "provider": "Restaurante El Buen Sabor",
        "amount": 25.50,
        "payment_method": "tarjeta",
        "category": "alimentacion",
        "user_id": user_id,
        "description": "Almuerzo de trabajo"
    }
    
    response = requests.post(f"{API_BASE}/invoices/upload", data=invoice_data)
    print(f"Crear factura: {response.status_code}")
    if response.status_code == 201:
        return response.json()
    return None

def get_invoices_example():
    """Ejemplo de consulta de facturas."""
    response = requests.get(f"{API_BASE}/invoices/")
    print(f"Obtener facturas: {response.status_code}")
    if response.status_code == 200:
        return response.json()
    return None

def export_invoices_example():
    """Ejemplo de exportación a Excel."""
    response = requests.get(f"{API_BASE}/invoices/export/excel")
    print(f"Exportar facturas: {response.status_code}")
    if response.status_code == 200:
        return response.json()
    return None

def main():
    """Función principal de ejemplo."""
    print("=== Ejemplo de uso de la API de Control de Facturas Boosting ===\n")
    
    # 1. Crear usuario
    print("1. Creando usuario...")
    user = create_user_example()
    if user:
        print(f"   Usuario creado: {user['name']} (ID: {user['id']})")
        user_id = user['id']
    else:
        print("   Error al crear usuario")
        return
    
    print()
    
    # 2. Crear factura
    print("2. Creando factura...")
    invoice = create_invoice_example(user_id)
    if invoice:
        print(f"   Factura creada: {invoice['provider']} - ${invoice['amount']}")
    else:
        print("   Error al crear factura")
        return
    
    print()
    
    # 3. Consultar facturas
    print("3. Consultando facturas...")
    invoices = get_invoices_example()
    if invoices:
        print(f"   Total de facturas: {invoices['total']}")
        for inv in invoices['items']:
            print(f"   - {inv['provider']}: ${inv['amount']} ({inv['status']})")
    
    print()
    
    # 4. Exportar a Excel
    print("4. Exportando a Excel...")
    export_result = export_invoices_example()
    if export_result:
        print(f"   Archivo generado: {export_result['file_path']}")
        print(f"   Total de facturas exportadas: {export_result['total_invoices']}")
    
    print("\n=== Ejemplo completado ===")

if __name__ == "__main__":
    main()

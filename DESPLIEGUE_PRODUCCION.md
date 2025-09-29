# 🚀 Guía de Despliegue en Producción - Sistema de Control de Facturas Boosting

## 🎯 Objetivo

Esta guía te ayudará a desplegar el Sistema de Control de Facturas Boosting en un entorno de producción seguro, escalable y mantenible.

---

## 🏗️ Opciones de Despliegue

### 1. **Google Cloud Platform (Recomendado)**
- **Ventajas:** Integración nativa con Gmail API, escalabilidad automática, alta disponibilidad
- **Servicios:** Cloud Run, Cloud SQL, Cloud Storage
- **Costo:** Pay-per-use, económico para startups

### 2. **Amazon Web Services (AWS)**
- **Ventajas:** Amplia gama de servicios, alta disponibilidad, buena documentación
- **Servicios:** ECS/Fargate, RDS, S3
- **Costo:** Competitivo, descuentos por uso prolongado

### 3. **DigitalOcean**
- **Ventajas:** Simplicidad, precios fijos, buena para proyectos medianos
- **Servicios:** Droplets, Managed Databases, Spaces
- **Costo:** Predecible, ideal para presupuestos fijos

### 4. **VPS Tradicional**
- **Ventajas:** Control total, costos bajos
- **Servicios:** VPS con Docker
- **Costo:** Muy económico

---

## 🐳 Despliegue con Docker (Recomendado)

### 1. **Preparar Archivos Docker**

#### Dockerfile para Backend
```dockerfile
# backend/Dockerfile
FROM python:3.12-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-spa \
    tesseract-ocr-eng \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir Pillow pytesseract PyMuPDF

# Copiar código fuente
COPY . .

# Crear directorio de uploads
RUN mkdir -p uploads

# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Dockerfile para Frontend
```dockerfile
# frontend/Dockerfile
FROM node:18-alpine as build

WORKDIR /app

# Copiar package files
COPY package*.json ./

# Instalar dependencias
RUN npm ci --only=production

# Copiar código fuente
COPY . .

# Build de producción
RUN npm run build

# Servidor nginx
FROM nginx:alpine

# Copiar archivos build
COPY --from=build /app/dist /usr/share/nginx/html

# Copiar configuración nginx
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

#### docker-compose.yml
```yaml
version: '3.8'

services:
  # Base de datos PostgreSQL
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: facturas_boosting
      POSTGRES_USER: boosting_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  # Backend FastAPI
  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://boosting_user:${DB_PASSWORD}@db:5432/facturas_boosting
      GMAIL_CREDENTIALS_FILE: credentials.json
      GMAIL_TOKEN_FILE: token.json
    volumes:
      - ./backend/uploads:/app/uploads
      - ./backend/credentials.json:/app/credentials.json
      - ./backend/token.json:/app/token.json
    ports:
      - "8000:8000"
    depends_on:
      - db
    restart: unless-stopped

  # Frontend React
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped

  # Nginx reverse proxy (opcional)
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend
    restart: unless-stopped

volumes:
  postgres_data:
```

### 2. **Configuración Nginx**
```nginx
# nginx/nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:80;
    }

    server {
        listen 80;
        server_name tu-dominio.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl;
        server_name tu-dominio.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # API Backend
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

---

## ☁️ Despliegue en Google Cloud Platform

### 1. **Configurar Google Cloud**

```bash
# Instalar Google Cloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Autenticar
gcloud auth login
gcloud config set project tu-proyecto-id
```

### 2. **Desplegar Backend en Cloud Run**

```bash
# Construir y desplegar backend
cd backend
gcloud builds submit --tag gcr.io/tu-proyecto-id/facturas-backend
gcloud run deploy facturas-backend \
  --image gcr.io/tu-proyecto-id/facturas-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL=postgresql://user:pass@/db?host=/cloudsql/tu-proyecto-id:us-central1:facturas-db
```

### 3. **Configurar Cloud SQL**

```bash
# Crear instancia de Cloud SQL
gcloud sql instances create facturas-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1

# Crear base de datos
gcloud sql databases create facturas_boosting --instance=facturas-db

# Crear usuario
gcloud sql users create boosting_user \
  --instance=facturas-db \
  --password=tu-password-seguro
```

### 4. **Desplegar Frontend en Cloud Storage**

```bash
# Build del frontend
cd frontend
npm run build

# Subir a Cloud Storage
gsutil -m cp -r dist/* gs://tu-bucket-frontend

# Configurar como sitio web
gsutil web set -m index.html -e 404.html gs://tu-bucket-frontend
```

---

## 🐳 Despliegue en DigitalOcean

### 1. **Crear Droplet**

```bash
# Crear droplet con Docker preinstalado
doctl compute droplet create facturas-server \
  --image docker-20-04 \
  --size s-2vcpu-4gb \
  --region nyc1 \
  --ssh-keys tu-ssh-key-id
```

### 2. **Configurar Servidor**

```bash
# Conectar al servidor
ssh root@tu-ip-servidor

# Clonar repositorio
git clone https://github.com/tu-usuario/facturasBst.git
cd facturasBst

# Configurar variables de entorno
cp .env.example .env
nano .env
```

### 3. **Ejecutar con Docker Compose**

```bash
# Ejecutar servicios
docker-compose up -d

# Verificar estado
docker-compose ps
```

---

## 🔒 Configuración de Seguridad

### 1. **Variables de Entorno**

```bash
# .env.production
# Base de datos
DATABASE_URL=postgresql://usuario:password-seguro@host:5432/facturas_boosting

# Gmail API
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_TOKEN_FILE=token.json

# Seguridad
SECRET_KEY=tu-secret-key-muy-seguro
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com

# SSL
SSL_CERT_PATH=/etc/ssl/certs/cert.pem
SSL_KEY_PATH=/etc/ssl/private/key.pem
```

### 2. **Configurar SSL**

```bash
# Usando Let's Encrypt
sudo apt install certbot
sudo certbot --nginx -d tu-dominio.com

# O usar Cloudflare para SSL automático
```

### 3. **Firewall**

```bash
# Configurar UFW
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

---

## 📊 Monitoreo y Logs

### 1. **Configurar Logs**

```python
# backend/src/main.py
import logging
from logging.handlers import RotatingFileHandler

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        RotatingFileHandler('logs/app.log', maxBytes=10000000, backupCount=5),
        logging.StreamHandler()
    ]
)
```

### 2. **Health Checks**

```bash
# Script de monitoreo
#!/bin/bash
# health_check.sh

BACKEND_URL="https://tu-dominio.com/api/health"
FRONTEND_URL="https://tu-dominio.com"

# Verificar backend
if curl -f -s $BACKEND_URL > /dev/null; then
    echo "Backend OK"
else
    echo "Backend ERROR"
    # Enviar alerta
fi

# Verificar frontend
if curl -f -s $FRONTEND_URL > /dev/null; then
    echo "Frontend OK"
else
    echo "Frontend ERROR"
    # Enviar alerta
fi
```

### 3. **Backup Automático**

```bash
#!/bin/bash
# backup.sh

# Backup de base de datos
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup de archivos
tar -czf uploads_backup_$(date +%Y%m%d_%H%M%S).tar.gz uploads/

# Subir a cloud storage
gsutil cp backup_*.sql gs://tu-bucket-backups/
gsutil cp uploads_backup_*.tar.gz gs://tu-bucket-backups/
```

---

## 🚀 Scripts de Despliegue

### 1. **Script de Despliegue Automático**

```bash
#!/bin/bash
# deploy.sh

set -e

echo "🚀 Iniciando despliegue..."

# Pull latest code
git pull origin main

# Build y deploy backend
cd backend
docker build -t facturas-backend .
docker-compose up -d backend

# Build y deploy frontend
cd ../frontend
npm run build
docker build -t facturas-frontend .
docker-compose up -d frontend

# Ejecutar migraciones
docker-compose exec backend alembic upgrade head

echo "✅ Despliegue completado!"
```

### 2. **Script de Rollback**

```bash
#!/bin/bash
# rollback.sh

echo "🔄 Ejecutando rollback..."

# Volver a versión anterior
git checkout HEAD~1

# Reconstruir y desplegar
docker-compose down
docker-compose up -d

echo "✅ Rollback completado!"
```

---

## 📈 Escalabilidad

### 1. **Load Balancer**

```yaml
# docker-compose.scale.yml
version: '3.8'

services:
  backend:
    deploy:
      replicas: 3
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/facturas_boosting

  nginx:
    volumes:
      - ./nginx/load-balancer.conf:/etc/nginx/nginx.conf
```

### 2. **Base de Datos Escalada**

```bash
# Configurar read replicas
gcloud sql instances create facturas-db-read \
  --master-instance-name=facturas-db \
  --replica-type=READ
```

---

## 💰 Estimación de Costos

### **Google Cloud Platform (Mensual)**
- **Cloud Run:** $0-50 (dependiendo del tráfico)
- **Cloud SQL:** $25-100 (dependiendo del tamaño)
- **Cloud Storage:** $5-20
- **Total estimado:** $30-170/mes

### **DigitalOcean (Mensual)**
- **Droplet 2GB:** $12/mes
- **Managed Database:** $15/mes
- **Spaces Storage:** $5/mes
- **Total:** $32/mes

### **AWS (Mensual)**
- **ECS Fargate:** $20-80
- **RDS:** $25-100
- **S3:** $5-15
- **Total estimado:** $50-195/mes

---

## 🔄 CI/CD Pipeline

### 1. **GitHub Actions**

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Deploy to Google Cloud
      run: |
        gcloud builds submit --tag gcr.io/${{ secrets.PROJECT_ID }}/facturas-backend
        gcloud run deploy facturas-backend --image gcr.io/${{ secrets.PROJECT_ID }}/facturas-backend
```

### 2. **Automatización Completa**

```bash
# Configurar webhook
curl -X POST https://api.github.com/repos/tu-usuario/facturasBst/hooks \
  -H "Authorization: token $GITHUB_TOKEN" \
  -d '{
    "name": "web",
    "active": true,
    "events": ["push"],
    "config": {
      "url": "https://tu-servidor.com/webhook",
      "content_type": "json"
    }
  }'
```

---

## 🎯 Checklist de Despliegue

### ✅ **Pre-Despliegue**
- [ ] Configurar dominio y DNS
- [ ] Obtener certificados SSL
- [ ] Configurar variables de entorno
- [ ] Preparar credenciales de Gmail API
- [ ] Configurar base de datos
- [ ] Configurar monitoreo

### ✅ **Despliegue**
- [ ] Desplegar backend
- [ ] Desplegar frontend
- [ ] Configurar reverse proxy
- [ ] Ejecutar migraciones
- [ ] Configurar SSL
- [ ] Configurar firewall

### ✅ **Post-Despliegue**
- [ ] Verificar funcionalidades
- [ ] Configurar backups
- [ ] Configurar monitoreo
- [ ] Configurar alertas
- [ ] Documentar acceso
- [ ] Capacitar usuarios

---

## 🆘 Soporte en Producción

### 1. **Monitoreo 24/7**

```bash
# Configurar alertas
curl -X POST https://api.monitoring.com/alerts \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Facturas Backend Down",
    "condition": "backend_health_check == 0",
    "notification": "email:admin@empresa.com"
  }'
```

### 2. **Logs Centralizados**

```bash
# Configurar ELK Stack o similar
docker run -d \
  --name elasticsearch \
  -p 9200:9200 \
  elasticsearch:7.15.0
```

---

## 🎉 **¡Sistema Listo para Producción!**

Con esta guía, puedes desplegar el Sistema de Control de Facturas Boosting en cualquier entorno de producción de manera segura y escalable.

### 🚀 **Próximos Pasos**
1. **Elegir plataforma** de despliegue
2. **Configurar infraestructura** según la guía
3. **Desplegar sistema** paso a paso
4. **Configurar monitoreo** y alertas
5. **Capacitar usuarios** finales

**¡El sistema está listo para manejar la carga de producción! 🎉**

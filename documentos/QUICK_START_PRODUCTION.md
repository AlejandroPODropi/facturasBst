# 🚀 Quick Start - Despliegue en Producción

## ⚡ Despliegue en 5 Minutos

### 1. **Preparar Servidor**

```bash
# Conectar al servidor
ssh root@tu-servidor.com

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Instalar Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

### 2. **Clonar y Configurar**

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/facturasBst.git
cd facturasBst

# Configurar variables de entorno
cp env.example .env
nano .env  # Configurar variables importantes
```

### 3. **Configurar Variables Críticas**

```bash
# Editar .env con valores de producción
nano .env
```

**Variables importantes:**
```env
DB_PASSWORD=password-super-seguro-2024
SECRET_KEY=clave-secreta-muy-larga-y-aleatoria
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
```

### 4. **Desplegar**

```bash
# Hacer ejecutable el script
chmod +x scripts/deploy.sh

# Desplegar en producción
./scripts/deploy.sh production
```

### 5. **Configurar Dominio**

```bash
# Configurar DNS para apuntar a tu servidor
# A record: tu-dominio.com -> IP_DEL_SERVIDOR
# CNAME: www.tu-dominio.com -> tu-dominio.com
```

### 6. **Configurar SSL**

```bash
# Instalar Certbot
apt install certbot

# Obtener certificado SSL
certbot --nginx -d tu-dominio.com -d www.tu-dominio.com
```

---

## 🔧 Configuración de Gmail API (Opcional)

### 1. **Crear Proyecto en Google Cloud**

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto
3. Habilita Gmail API
4. Crea credenciales OAuth 2.0
5. Descarga `credentials.json`

### 2. **Subir Credenciales**

```bash
# Subir archivo de credenciales
scp credentials.json root@tu-servidor.com:/root/facturasBst/backend/
```

### 3. **Autenticar**

```bash
# Acceder al sistema y autenticar
curl -X POST https://tu-dominio.com/api/v1/gmail/auth/authenticate
```

---

## 📊 Verificar Despliegue

### 1. **Health Check**

```bash
# Verificar salud del sistema
./scripts/health-check.sh
```

### 2. **Acceder al Sistema**

- **Frontend:** https://tu-dominio.com
- **API:** https://tu-dominio.com/api/v1
- **Documentación:** https://tu-dominio.com/docs

### 3. **Probar Funcionalidades**

1. **Crear usuario** en el sistema
2. **Subir factura** manual
3. **Probar OCR** con imagen de factura
4. **Configurar Gmail** (si aplica)

---

## 🔒 Seguridad Básica

### 1. **Firewall**

```bash
# Configurar UFW
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS
ufw enable
```

### 2. **Backup Automático**

```bash
# Configurar cron para backup diario
crontab -e

# Agregar línea:
0 2 * * * /root/facturasBst/scripts/backup.sh
```

### 3. **Monitoreo**

```bash
# Configurar monitoreo básico
apt install htop iotop

# Ver logs en tiempo real
docker-compose logs -f
```

---

## 🆘 Comandos Útiles

### **Gestión del Sistema**

```bash
# Ver estado de servicios
docker-compose ps

# Ver logs
docker-compose logs -f

# Reiniciar servicios
docker-compose restart

# Detener servicios
docker-compose down

# Actualizar sistema
git pull && ./scripts/deploy.sh production
```

### **Backup y Restauración**

```bash
# Crear backup manual
./scripts/backup.sh

# Ver backups disponibles
ls -la backups/

# Restaurar desde backup
# (Ver documentación completa en DESPLIEGUE_PRODUCCION.md)
```

### **Troubleshooting**

```bash
# Verificar salud
./scripts/health-check.sh

# Ver logs de errores
docker-compose logs backend | grep ERROR

# Reiniciar servicio específico
docker-compose restart backend
```

---

## 📞 Soporte

### **En caso de problemas:**

1. **Verificar logs:** `docker-compose logs -f`
2. **Health check:** `./scripts/health-check.sh`
3. **Consultar documentación:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
4. **Revisar configuración:** Verificar archivo `.env`

### **Información para soporte:**

- Sistema operativo: `uname -a`
- Versión Docker: `docker --version`
- Logs de error: `docker-compose logs backend`
- Estado de servicios: `docker-compose ps`

---

## 🎉 **¡Sistema Listo!**

Con estos pasos, tu Sistema de Control de Facturas Boosting estará funcionando en producción en menos de 10 minutos.

### **Próximos pasos recomendados:**

1. **Configurar monitoreo** avanzado
2. **Configurar backups** automáticos
3. **Capacitar usuarios** finales
4. **Configurar alertas** de sistema

**¡Disfruta tu nuevo sistema de gestión de facturas! 🚀**

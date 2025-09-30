# Dockerfile para Frontend - Sistema de Control de Facturas Boosting
FROM node:18-alpine as build

# Establecer directorio de trabajo
WORKDIR /app

# Copiar package files
COPY package*.json ./

# Instalar dependencias (incluyendo dev para build)
RUN npm ci

# Copiar código fuente
COPY . .

# Configurar variable de entorno para producción
ENV VITE_API_URL=https://backend-493189429371.us-central1.run.app/api/v1

# Build de producción
RUN npm run build

# Servidor nginx para producción
FROM nginx:alpine

# Instalar curl para health checks
RUN apk add --no-cache curl

# Copiar archivos build
COPY --from=build /app/dist /usr/share/nginx/html

# Copiar configuración nginx personalizada
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copiar script de inicio
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Crear usuario no-root
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

# Configurar permisos
RUN chown -R nextjs:nodejs /usr/share/nginx/html
RUN chown -R nextjs:nodejs /var/cache/nginx
RUN chown -R nextjs:nodejs /var/log/nginx
RUN chown -R nextjs:nodejs /etc/nginx/conf.d
RUN touch /var/run/nginx.pid
RUN chown -R nextjs:nodejs /var/run/nginx.pid

USER nextjs

# Exponer puerto
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/ || exit 1

# Comando de inicio
CMD ["/start.sh"]

#!/bin/sh

# Obtener el puerto de la variable de entorno PORT, por defecto 80
PORT=${PORT:-80}

# Reemplazar el puerto en la configuración de nginx
sed -i "s/listen 80;/listen $PORT;/g" /etc/nginx/conf.d/default.conf

# Iniciar nginx
nginx -g 'daemon off;'

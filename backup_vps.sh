#!/bin/bash

# 1. Crear directorio de backup
echo "Creating backup directory..."
mkdir -p ~/proyectos/srs-crm-vps-backup

# 2. Descargar todo el proyecto del VPS
echo "Downloading project files from VPS (srs-crm)..."
scp -r root@72.62.41.234:/var/www/srs-crm/* ~/proyectos/srs-crm-vps-backup/

# 3. Descargar configuración de Nginx
echo "Downloading Nginx configuration..."
scp root@72.62.41.234:/etc/nginx/sites-available/srs-crm ~/proyectos/srs-crm-vps-backup/nginx-config.conf

# 4. Descargar variables de entorno de PM2
echo "Downloading PM2 environment..."
ssh root@72.62.41.234 "pm2 env 1" > ~/proyectos/srs-crm-vps-backup/pm2-env.txt

# 5. Exportar lista de procesos PM2
echo "Downloading PM2 process list..."
ssh root@72.62.41.234 "pm2 list" > ~/proyectos/srs-crm-vps-backup/pm2-list.txt

# 6. Verificar que todo se descargó
echo "---------------------------------------------------"
echo "Backup verification (listing contents):"
ls -la ~/proyectos/srs-crm-vps-backup/
echo "---------------------------------------------------"
echo "Check for: backend/, frontend/, nginx-config.conf above."

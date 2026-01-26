#!/bin/bash

# Configuration
SERVER_IP="72.62.41.234"
USER="root"
REMOTE_PATH="/var/www/srs-crm"

echo "🚀 Iniciando despliegue manual a $SERVER_IP..."

# 1. Build Frontend
echo "📦 Construyendo Frontend..."
cd frontend
npm install
npm run build
cd ..

# 2. Upload Frontend
echo "📤 Subiendo Frontend..."
scp -r frontend/build/* $USER@$SERVER_IP:$REMOTE_PATH/frontend/build/

# 3. Upload Backend Config
echo "⚙️ Subiendo configuración Backend (.env)..."
scp backend/.env $USER@$SERVER_IP:$REMOTE_PATH/backend/.env

# 4. Fix Permissions & Restart Services
echo "🔧 Ajustando permisos y reiniciando servicios..."
ssh $USER@$SERVER_IP << EOF
    # Fix permissions
    chown -R www-data:www-data $REMOTE_PATH/frontend/build
    chmod -R 755 $REMOTE_PATH/frontend/build
    
    # Restart Backend
    pm2 restart srs-backend
    
    # Check Nginx Config
    nginx -t
    systemctl reload nginx
EOF

echo "✅ Despliegue finalizado."
echo "👉 Verifica en: https://crm.systemrapidsolutions.com:3001"

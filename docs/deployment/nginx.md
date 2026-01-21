# Configuracion Nginx

## Arquitectura

```
Internet
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  NGINX (Puerto 3001 SSL)                                        │
│                                                                 │
│  /              → Frontend (build estatico)                     │
│  /api/*         → Backend (proxy a localhost:8000)              │
└─────────────────────────────────────────────────────────────────┘
    │                                    │
    ▼                                    ▼
┌─────────────────┐              ┌─────────────────┐
│ Frontend Build  │              │ FastAPI Backend │
│ /var/www/srs-   │              │ localhost:8000  │
│ crm/frontend/   │              │                 │
│ build/          │              │                 │
└─────────────────┘              └─────────────────┘
```

## Configuracion del Sitio

### Crear Archivo de Configuracion

```bash
sudo nano /etc/nginx/sites-available/srs-crm
```

### Contenido

```nginx
# /etc/nginx/sites-available/srs-crm

server {
    listen 3001 ssl http2;
    listen [::]:3001 ssl http2;

    server_name crm.systemrapidsolutions.com;

    # SSL (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/crm.systemrapidsolutions.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/crm.systemrapidsolutions.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Logs
    access_log /var/log/nginx/srs-crm.access.log;
    error_log /var/log/nginx/srs-crm.error.log;

    # Tamaño máximo de upload (para importar Excel)
    client_max_body_size 10M;

    # Frontend (archivos estaticos)
    root /var/www/srs-crm/frontend/build;
    index index.html;

    # Ruta raiz - servir React app
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API - proxy al backend FastAPI
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Health check directo
    location /health {
        proxy_pass http://127.0.0.1:8000/api/health;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }

    # Archivos estaticos - cache agresivo
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # Bloquear acceso a archivos ocultos
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
}

# Redirigir HTTP a HTTPS (puerto 80 a 3001)
server {
    listen 80;
    listen [::]:80;
    server_name crm.systemrapidsolutions.com;
    return 301 https://$server_name:3001$request_uri;
}
```

### Habilitar Sitio

```bash
# Crear enlace simbolico
sudo ln -s /etc/nginx/sites-available/srs-crm /etc/nginx/sites-enabled/

# Verificar configuracion
sudo nginx -t

# Recargar Nginx
sudo systemctl reload nginx
```

## Comandos Utiles

### Verificar Configuracion

```bash
sudo nginx -t
# nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
# nginx: configuration file /etc/nginx/nginx.conf test is successful
```

### Recargar (sin downtime)

```bash
sudo systemctl reload nginx
```

### Reiniciar

```bash
sudo systemctl restart nginx
```

### Ver Logs

```bash
# Logs de acceso
sudo tail -f /var/log/nginx/srs-crm.access.log

# Logs de error
sudo tail -f /var/log/nginx/srs-crm.error.log
```

### Estado

```bash
sudo systemctl status nginx
```

## Headers de Seguridad (Opcional)

Añadir al bloque `server`:

```nginx
# Security headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://accounts.google.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https://accounts.google.com;" always;
```

## CORS

Si necesitas CORS adicional (normalmente manejado por FastAPI):

```nginx
location /api/ {
    # ... existing config ...

    # CORS headers
    add_header 'Access-Control-Allow-Origin' 'https://crm.systemrapidsolutions.com:3001' always;
    add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, PATCH, DELETE, OPTIONS' always;
    add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type' always;

    if ($request_method = 'OPTIONS') {
        return 204;
    }
}
```

## Troubleshooting

### 502 Bad Gateway

El backend no esta corriendo o no es accesible:

```bash
# Verificar que el backend esta corriendo
pm2 status

# Verificar que escucha en el puerto correcto
ss -tlnp | grep 8000

# Verificar logs del backend
pm2 logs srs-crm-backend
```

### 504 Gateway Timeout

La peticion tarda demasiado:

```nginx
# Aumentar timeouts
proxy_read_timeout 600s;
proxy_connect_timeout 300s;
```

### 413 Request Entity Too Large

Archivo muy grande:

```nginx
# Aumentar limite
client_max_body_size 50M;
```

### Certificado SSL invalido

```bash
# Verificar certificado
sudo certbot certificates

# Renovar si es necesario
sudo certbot renew --dry-run
```

# Configuracion SSL con Let's Encrypt

## Requisitos Previos

1. Dominio apuntando al servidor (DNS configurado)
2. Nginx instalado y funcionando
3. Puertos 80 y 443 abiertos en firewall

## Instalacion de Certbot

```bash
sudo apt install certbot python3-certbot-nginx -y
```

## Obtener Certificado

### Metodo Automatico (Recomendado)

```bash
sudo certbot --nginx -d crm.systemrapidsolutions.com
```

Certbot:
1. Verifica propiedad del dominio
2. Genera certificados
3. Configura Nginx automaticamente
4. Configura renovacion automatica

### Metodo Manual

```bash
# Solo obtener certificado (sin modificar Nginx)
sudo certbot certonly --nginx -d crm.systemrapidsolutions.com
```

Luego configurar Nginx manualmente (ver nginx.md).

## Ubicacion de Certificados

```
/etc/letsencrypt/live/crm.systemrapidsolutions.com/
├── cert.pem        # Certificado
├── chain.pem       # Cadena intermedia
├── fullchain.pem   # Certificado + cadena (usar este)
├── privkey.pem     # Clave privada
└── README
```

## Configuracion Nginx

```nginx
server {
    listen 3001 ssl http2;
    server_name crm.systemrapidsolutions.com;

    # Certificados
    ssl_certificate /etc/letsencrypt/live/crm.systemrapidsolutions.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/crm.systemrapidsolutions.com/privkey.pem;

    # Configuracion SSL recomendada
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # ... resto de configuracion
}
```

## Renovacion Automatica

Certbot instala un timer de systemd para renovacion automatica:

```bash
# Verificar timer
sudo systemctl status certbot.timer

# Ver proxima ejecucion
sudo systemctl list-timers | grep certbot
```

### Test de Renovacion

```bash
sudo certbot renew --dry-run
```

### Renovacion Manual

```bash
sudo certbot renew
sudo systemctl reload nginx
```

## Verificar Certificado

### Desde Linea de Comandos

```bash
# Ver informacion del certificado
sudo certbot certificates

# Output ejemplo:
Certificate Name: crm.systemrapidsolutions.com
    Domains: crm.systemrapidsolutions.com
    Expiry Date: 2026-04-21 (VALID: 89 days)
    Certificate Path: /etc/letsencrypt/live/crm.systemrapidsolutions.com/fullchain.pem
    Private Key Path: /etc/letsencrypt/live/crm.systemrapidsolutions.com/privkey.pem
```

### Desde Navegador

1. Abrir https://crm.systemrapidsolutions.com:3001
2. Click en el candado
3. Ver certificado

### Online

- https://www.ssllabs.com/ssltest/

## Configuracion SSL Optima

Crear archivo de opciones SSL:

```bash
sudo nano /etc/letsencrypt/options-ssl-nginx.conf
```

Contenido recomendado:

```nginx
ssl_session_cache shared:le_nginx_SSL:10m;
ssl_session_timeout 1440m;
ssl_session_tickets off;

ssl_protocols TLSv1.2 TLSv1.3;
ssl_prefer_server_ciphers off;

ssl_ciphers "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384";
```

Generar parametros DH:

```bash
sudo openssl dhparam -out /etc/letsencrypt/ssl-dhparams.pem 2048
```

## Troubleshooting

### Error: Unable to find domain

Verificar que el DNS apunta al servidor:

```bash
dig crm.systemrapidsolutions.com
# Debe mostrar la IP del servidor
```

### Error: Connection refused

Verificar firewall:

```bash
sudo ufw status
# Debe mostrar 80 y 443 abiertos

# Si no:
sudo ufw allow 'Nginx Full'
```

### Error: Challenge failed

1. Verificar que Nginx esta corriendo
2. Verificar que puerto 80 esta accesible
3. Verificar que no hay otro servidor en puerto 80

```bash
sudo systemctl status nginx
sudo ss -tlnp | grep :80
```

### Certificado expirado

```bash
# Renovar manualmente
sudo certbot renew --force-renewal
sudo systemctl reload nginx
```

### Puerto no estandar (3001)

Let's Encrypt valida en puerto 80. Para usar puerto 3001:

1. Temporalmente permitir puerto 80 para validacion
2. Obtener certificado
3. Configurar Nginx para usar 3001

O usar validacion DNS (mas compleja).

## Certificado para Multiples Dominios

```bash
sudo certbot --nginx \
  -d crm.systemrapidsolutions.com \
  -d api.systemrapidsolutions.com
```

## Revocar Certificado

```bash
sudo certbot revoke --cert-path /etc/letsencrypt/live/crm.systemrapidsolutions.com/cert.pem
sudo certbot delete --cert-name crm.systemrapidsolutions.com
```

## Backup de Certificados

```bash
# Los certificados estan en:
/etc/letsencrypt/

# Backup
sudo tar -czf letsencrypt-backup.tar.gz /etc/letsencrypt/
```

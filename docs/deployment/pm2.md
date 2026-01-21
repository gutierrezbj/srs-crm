# Configuracion PM2

## Que es PM2

PM2 es un gestor de procesos para Node.js/Python que permite:
- Mantener aplicaciones corriendo 24/7
- Reinicio automatico ante crashes
- Logs centralizados
- Monitoreo de recursos

## Configuracion Backend

### Iniciar Proceso

```bash
cd /var/www/srs-crm/backend
source venv/bin/activate

# Iniciar con PM2
pm2 start server.py \
  --name srs-crm-backend \
  --interpreter python \
  --cwd /var/www/srs-crm/backend
```

### Archivo de Configuracion (ecosystem.config.js)

```javascript
// /var/www/srs-crm/ecosystem.config.js
module.exports = {
  apps: [
    {
      name: "srs-crm-backend",
      script: "server.py",
      cwd: "/var/www/srs-crm/backend",
      interpreter: "/var/www/srs-crm/backend/venv/bin/python",
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: "500M",
      env: {
        NODE_ENV: "production"
      },
      error_file: "/var/log/srs-crm/backend-error.log",
      out_file: "/var/log/srs-crm/backend-out.log",
      log_date_format: "YYYY-MM-DD HH:mm:ss Z"
    }
  ]
};
```

### Iniciar con Ecosystem

```bash
pm2 start ecosystem.config.js
```

## Comandos Utiles

### Estado de Procesos

```bash
pm2 status
# o
pm2 list

# Output:
┌────┬────────────────────┬──────────┬──────┬───────────┬──────────┬──────────┐
│ id │ name               │ mode     │ ↺    │ status    │ cpu      │ memory   │
├────┼────────────────────┼──────────┼──────┼───────────┼──────────┼──────────┤
│ 0  │ srs-crm-backend    │ fork     │ 5    │ online    │ 0%       │ 120mb    │
└────┴────────────────────┴──────────┴──────┴───────────┴──────────┴──────────┘
```

### Ver Logs

```bash
# Logs en tiempo real
pm2 logs srs-crm-backend

# Ultimas 100 lineas
pm2 logs srs-crm-backend --lines 100

# Solo errores
pm2 logs srs-crm-backend --err

# Todos los procesos
pm2 logs
```

### Reiniciar

```bash
# Reiniciar proceso especifico
pm2 restart srs-crm-backend

# Reiniciar todos
pm2 restart all

# Reiniciar con update de environment
pm2 restart srs-crm-backend --update-env
```

### Detener

```bash
pm2 stop srs-crm-backend
pm2 stop all
```

### Eliminar

```bash
pm2 delete srs-crm-backend
pm2 delete all
```

### Monitoreo

```bash
# Monitor interactivo
pm2 monit

# Info detallada de proceso
pm2 show srs-crm-backend

# Metricas web (opcional)
pm2 web
```

## Auto-inicio al Reiniciar Servidor

```bash
# Generar script de startup
pm2 startup

# El comando anterior mostrara algo como:
# sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u deployer --hp /home/deployer

# Ejecutar el comando mostrado, luego:
pm2 save
```

## Configurar Logs

### Crear Directorio de Logs

```bash
sudo mkdir -p /var/log/srs-crm
sudo chown deployer:deployer /var/log/srs-crm
```

### Rotacion de Logs

```bash
# Instalar modulo de rotacion
pm2 install pm2-logrotate

# Configurar
pm2 set pm2-logrotate:max_size 10M
pm2 set pm2-logrotate:retain 7
pm2 set pm2-logrotate:compress true
```

## Troubleshooting

### Proceso no inicia

```bash
# Ver logs de error
pm2 logs srs-crm-backend --err --lines 50

# Verificar que el entorno virtual tiene las dependencias
cd /var/www/srs-crm/backend
source venv/bin/activate
python -c "import fastapi; print('OK')"
```

### Proceso se reinicia constantemente

```bash
# Ver numero de reinicios
pm2 status

# Si ↺ es muy alto, revisar logs
pm2 logs srs-crm-backend --lines 200
```

### Alto consumo de memoria

```bash
# Verificar memoria
pm2 show srs-crm-backend | grep memory

# Reiniciar si supera limite
pm2 restart srs-crm-backend
```

### Actualizar codigo

```bash
cd /var/www/srs-crm
git pull origin main

# Backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
pm2 restart srs-crm-backend

# Frontend
cd ../frontend
yarn install
yarn build
```

## Variables de Entorno

PM2 carga las variables del archivo `.env` automaticamente si usas `dotenv` en el codigo Python.

Para variables especificas de PM2:

```bash
# Ver variables actuales
pm2 env 0  # 0 es el ID del proceso

# Actualizar variables
pm2 restart srs-crm-backend --update-env
```

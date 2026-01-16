#!/bin/bash
# Script de inicio para SRS CRM Backend
# Usa el virtual environment correcto

cd /var/www/srs-crm/backend
source /var/www/srs-crm/venv/bin/activate

# Asegurar que PYTHONPATH incluye el directorio backend
export PYTHONPATH="/var/www/srs-crm/backend:$PYTHONPATH"

# Iniciar uvicorn con el módulo server (server.py)
exec uvicorn server:app --host 0.0.0.0 --port 8000

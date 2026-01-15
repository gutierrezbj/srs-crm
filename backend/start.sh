#!/bin/bash
source /var/www/srs-crm/backend/venv/bin/activate
exec uvicorn server:app --host 0.0.0.0 --port 8000

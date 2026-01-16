module.exports = {
  apps: [{
    name: 'srs-crm-backend',
    script: '/var/www/srs-crm/venv/bin/uvicorn',
    args: 'server:app --host 0.0.0.0 --port 8000',
    cwd: '/var/www/srs-crm/backend',
    interpreter: 'none',
    env: {
      PATH: '/var/www/srs-crm/venv/bin:' + process.env.PATH,
      VIRTUAL_ENV: '/var/www/srs-crm/venv',
      PYTHONPATH: '/var/www/srs-crm/backend'
    },
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '500M',
    error_file: '/var/www/srs-crm/logs/backend-error.log',
    out_file: '/var/www/srs-crm/logs/backend-out.log',
    log_file: '/var/www/srs-crm/logs/backend-combined.log',
    time: true
  }]
};

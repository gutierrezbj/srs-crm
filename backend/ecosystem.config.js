module.exports = {
  apps: [{
    name: 'srs-crm-backend',
    script: '/opt/apps/srs-crm/venv/bin/uvicorn',
    args: 'server:app --host 0.0.0.0 --port 8000',
    cwd: '/opt/apps/srs-crm/backend',
    interpreter: 'none',
    env: {
      PATH: '/opt/apps/srs-crm/venv/bin:' + process.env.PATH,
      VIRTUAL_ENV: '/opt/apps/srs-crm/venv',
      PYTHONPATH: '/opt/apps/srs-crm/backend'
    },
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '500M',
    error_file: '/opt/apps/srs-crm/logs/backend-error.log',
    out_file: '/opt/apps/srs-crm/logs/backend-out.log',
    log_file: '/opt/apps/srs-crm/logs/backend-combined.log',
    time: true
  }]
};

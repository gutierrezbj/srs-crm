module.exports = {
  apps: [{
    name: 'srs-crm-backend',
    script: '/var/www/srs-crm/backend/venv/bin/uvicorn',
    args: 'server:app --host 0.0.0.0 --port 8000',
    cwd: '/var/www/srs-crm/backend',
    interpreter: 'none',
    env: {
      PATH: '/var/www/srs-crm/backend/venv/bin:' + process.env.PATH
    }
  }]
}

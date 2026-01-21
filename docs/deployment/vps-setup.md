# Configuracion Inicial del VPS

## Datos del Servidor

| Campo | Valor |
|-------|-------|
| Proveedor | Hostinger |
| IP | 72.62.41.234 |
| OS | Ubuntu 22.04 LTS |
| RAM | 4GB |
| CPU | 2 vCPU |
| Disco | 80GB SSD |

## Acceso SSH

```bash
# Configurar en ~/.ssh/config
Host srs
    HostName 72.62.41.234
    User root
    IdentityFile ~/.ssh/id_rsa

# Conectar
ssh srs
```

## Configuracion Inicial

### 1. Actualizar Sistema

```bash
apt update && apt upgrade -y
```

### 2. Crear Usuario No-Root

```bash
adduser deployer
usermod -aG sudo deployer

# Copiar SSH keys
mkdir -p /home/deployer/.ssh
cp ~/.ssh/authorized_keys /home/deployer/.ssh/
chown -R deployer:deployer /home/deployer/.ssh
chmod 700 /home/deployer/.ssh
chmod 600 /home/deployer/.ssh/authorized_keys
```

### 3. Instalar Dependencias Base

```bash
# Python 3.11
add-apt-repository ppa:deadsnakes/ppa -y
apt update
apt install python3.11 python3.11-venv python3.11-dev -y

# Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install nodejs -y

# Yarn
npm install -g yarn

# Git
apt install git -y

# Build tools
apt install build-essential -y
```

### 4. Instalar MongoDB Tools (opcional)

```bash
# Solo si necesitas herramientas CLI de MongoDB
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list
apt update
apt install mongodb-mongosh -y
```

### 5. Instalar Nginx

```bash
apt install nginx -y
systemctl enable nginx
systemctl start nginx
```

### 6. Instalar PM2

```bash
npm install -g pm2
```

### 7. Instalar Certbot (SSL)

```bash
apt install certbot python3-certbot-nginx -y
```

## Estructura de Directorios

```bash
mkdir -p /var/www/srs-crm
chown -R deployer:deployer /var/www/srs-crm
```

## Firewall

```bash
# UFW
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw allow 3001/tcp  # API
ufw enable
ufw status
```

## Clonar Repositorio

```bash
cd /var/www/srs-crm
git clone https://github.com/gutierrezbj/srs-crm.git .
```

## Configurar Backend

```bash
cd /var/www/srs-crm/backend

# Crear virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# Crear archivo .env
cp .env.example .env
nano .env  # Editar con credenciales reales
```

## Configurar Frontend

```bash
cd /var/www/srs-crm/frontend

# Instalar dependencias
yarn install

# Crear archivo .env
cp .env.example .env
nano .env  # Configurar URL backend

# Build produccion
yarn build
```

## Verificar Instalacion

```bash
# Python
python3.11 --version  # 3.11.x

# Node
node --version  # v18.x.x

# Yarn
yarn --version  # 1.22.x

# PM2
pm2 --version

# Nginx
nginx -v
```

## Siguientes Pasos

1. [Configurar PM2](pm2.md)
2. [Configurar Nginx](nginx.md)
3. [Configurar SSL](ssl.md)

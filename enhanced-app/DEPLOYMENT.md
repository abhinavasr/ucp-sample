# Deployment Guide

## Prerequisites

1. **Ollama Setup**
   ```bash
   # Install Ollama
   curl -fsSL https://ollama.ai/install.sh | sh

   # Pull required model (choose one)
   ollama pull qwen2.5:latest
   # OR
   ollama pull gemma2:latest

   # Verify Ollama is running
   ollama serve  # Run in separate terminal
   curl http://localhost:11434/api/version
   ```

2. **Python 3.11+**
   ```bash
   python --version
   ```

3. **Node.js 18+**
   ```bash
   node --version
   npm --version
   ```

## Quick Start (Development)

1. **Clone and Navigate**
   ```bash
   git clone https://github.com/abhinavasr/ucp-sample.git
   cd ucp-sample/enhanced-app
   ```

2. **Option A: Use Start Script (Recommended)**
   ```bash
   ./start.sh
   ```

   This will:
   - Check Ollama connection
   - Create Python virtual environment
   - Install all dependencies
   - Start all services
   - Show access URLs

3. **Option B: Manual Start**

   **Backend:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python main.py
   ```

   **Chat Interface:**
   ```bash
   cd frontend/chat
   npm install
   npm run dev
   ```

   **Merchant Portal:**
   ```bash
   cd frontend/merchant-portal
   npm install
   npm run dev
   ```

## Access Points

- **Chat Interface**: http://localhost:8450
- **Merchant Portal**: http://localhost:8451
- **API Documentation**: http://localhost:8451/docs
- **Health Check**: http://localhost:8451/health

## Production Deployment

### 1. Build Frontend Applications

```bash
# Chat Interface
cd frontend/chat
npm install
npm run build

# Merchant Portal
cd frontend/merchant-portal
npm install
npm run build
```

### 2. Setup Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/enhanced-app

# Chat Interface - chat.abhinava.xyz
server {
    listen 443 ssl http2;
    server_name chat.abhinava.xyz;

    ssl_certificate /etc/letsencrypt/live/chat.abhinava.xyz/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/chat.abhinava.xyz/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    location / {
        proxy_pass http://localhost:8450;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Merchant Portal - app.abhinava.xyz
server {
    listen 443 ssl http2;
    server_name app.abhinava.xyz;

    ssl_certificate /etc/letsencrypt/live/app.abhinava.xyz/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.abhinava.xyz/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    location / {
        proxy_pass http://localhost:8451;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# HTTP to HTTPS redirect
server {
    listen 80;
    server_name chat.abhinava.xyz app.abhinava.xyz;
    return 301 https://$server_name$request_uri;
}
```

### 3. Setup Systemd Services

**Backend Service** (`/etc/systemd/system/enhanced-backend.service`):
```ini
[Unit]
Description=Enhanced Business Agent Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/ucp-sample/enhanced-app/backend
Environment="PATH=/var/www/ucp-sample/enhanced-app/backend/venv/bin"
ExecStart=/var/www/ucp-sample/enhanced-app/backend/venv/bin/python main.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Chat Frontend** (`/etc/systemd/system/enhanced-chat.service`):
```ini
[Unit]
Description=Enhanced Chat Interface
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/ucp-sample/enhanced-app/frontend/chat
ExecStart=/usr/bin/npm run preview
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Merchant Portal** (`/etc/systemd/system/enhanced-merchant.service`):
```ini
[Unit]
Description=Enhanced Merchant Portal
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/ucp-sample/enhanced-app/frontend/merchant-portal
ExecStart=/usr/bin/npm run preview
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and Start Services:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable enhanced-backend enhanced-chat enhanced-merchant
sudo systemctl start enhanced-backend enhanced-chat enhanced-merchant
sudo systemctl status enhanced-backend enhanced-chat enhanced-merchant
```

### 4. SSL Certificates with Let's Encrypt

```bash
sudo certbot --nginx -d chat.abhinava.xyz -d app.abhinava.xyz
```

## Docker Deployment (Alternative)

```bash
cd enhanced-app

# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Environment Configuration

Create `.env` file in `backend/`:

```env
# Database
DATABASE_URL=sqlite+aiosqlite:///./data/enhanced_app.db

# Ollama Configuration
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:latest

# Server
HOST=0.0.0.0
PORT=8451
```

## Monitoring and Logs

### View Logs (Script Method)
```bash
tail -f logs/backend.log
tail -f logs/chat.log
tail -f logs/merchant.log
```

### View Logs (Systemd Method)
```bash
journalctl -u enhanced-backend -f
journalctl -u enhanced-chat -f
journalctl -u enhanced-merchant -f
```

### Health Checks
```bash
# Backend health
curl http://localhost:8451/health

# Frontend availability
curl -I http://localhost:8450
curl -I http://localhost:8451
```

## Backup and Restore

### Backup Database
```bash
cp backend/enhanced_app.db backup/enhanced_app_$(date +%Y%m%d_%H%M%S).db
```

### Restore Database
```bash
cp backup/enhanced_app_YYYYMMDD_HHMMSS.db backend/enhanced_app.db
sudo systemctl restart enhanced-backend
```

## Troubleshooting

### Ollama Not Responding
```bash
# Check if Ollama is running
ps aux | grep ollama

# Restart Ollama
sudo systemctl restart ollama  # If installed as service
# OR
ollama serve  # If running manually
```

### Port Already in Use
```bash
# Find process using port
lsof -ti:8450
lsof -ti:8451

# Kill process
kill -9 $(lsof -ti:8450)
kill -9 $(lsof -ti:8451)
```

### Database Issues
```bash
# Reset database (WARNING: Deletes all data)
rm backend/enhanced_app.db
python backend/main.py  # Will auto-create with sample data
```

### Permission Issues
```bash
# Fix ownership
sudo chown -R www-data:www-data /var/www/ucp-sample/enhanced-app

# Fix permissions
chmod +x enhanced-app/start.sh
chmod +x enhanced-app/stop.sh
```

## Security Considerations

1. **Firewall Configuration**
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw deny 8450/tcp  # Only allow through nginx
   sudo ufw deny 8451/tcp  # Only allow through nginx
   ```

2. **Authentication**
   - Add authentication middleware to merchant portal
   - Implement JWT tokens for API access
   - Use environment variables for secrets

3. **Rate Limiting**
   - Configure nginx rate limiting
   - Implement API rate limiting in FastAPI

4. **CORS Configuration**
   - Update CORS settings in `backend/main.py`
   - Specify exact origins in production

## Performance Optimization

1. **Database**
   - Consider PostgreSQL for production
   - Add database indexes
   - Implement connection pooling

2. **Caching**
   - Add Redis for session caching
   - Cache product catalog queries
   - Implement HTTP caching headers

3. **Frontend**
   - Enable gzip compression
   - Optimize images
   - Use CDN for static assets

## Updating the Application

```bash
cd /var/www/ucp-sample
git pull origin main

# Update backend
cd enhanced-app/backend
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart enhanced-backend

# Update frontends
cd ../frontend/chat
npm install
npm run build
sudo systemctl restart enhanced-chat

cd ../merchant-portal
npm install
npm run build
sudo systemctl restart enhanced-merchant
```

## Support

For issues:
1. Check logs first
2. Verify Ollama is running
3. Ensure all dependencies are installed
4. Check firewall and port availability
5. Review API documentation at http://localhost:8451/docs

# Enhanced Business Agent with Merchant Portal

A comprehensive AI-powered shopping assistant with Ollama integration and merchant portal for product management.

## Features

- **AI Chat Interface** (Port 8450 → https://chat.abhinava.xyz)
  - Beautiful, modern chat UI built with React and Tailwind CSS
  - Ollama-powered conversational AI (using Qwen or Gemma models)
  - Product search and recommendations
  - Shopping cart management
  - Order completion

- **Merchant Portal** (Port 8451 → https://app.abhinava.xyz)
  - Product management (Create, Read, Update, Delete)
  - Pricing configuration
  - Category and brand management
  - Real-time product statistics
  - Beautiful admin dashboard

- **Python Backend** (Port 8451)
  - FastAPI-based REST API
  - Ollama LLM integration
  - SQLite persistent database
  - Extends existing business_agent functionality
  - Full CRUD API for products

## Prerequisites

- Python 3.11+
- Node.js 18+
- Ollama running on http://host.docker.internal:11434 (or localhost:11434)
  - With `qwen2.5:latest` or `gemma2:latest` model installed

## Quick Start

### 1. Install Ollama and Models

```bash
# Install Ollama (if not already installed)
# Visit: https://ollama.ai/download

# Pull the required model (choose one)
ollama pull qwen2.5:latest
# OR
ollama pull gemma2:latest

# Verify Ollama is running
curl http://localhost:11434/api/version
```

### 2. Configure Environment Variables

```bash
cd enhanced-app/backend

# Copy the example environment file
cp .env.example .env

# Edit .env to customize your settings (optional)
# nano .env
```

**Key Configuration Options in `.env`:**
```env
# Ollama URL - change based on your setup
OLLAMA_URL=http://host.docker.internal:11434  # For Docker
# OLLAMA_URL=http://localhost:11434  # For local Ollama

# Choose your preferred model
OLLAMA_MODEL=qwen2.5:latest
# OLLAMA_MODEL=gemma2:latest

# Database location
DATABASE_URL=sqlite+aiosqlite:///./enhanced_app.db
```

### 3. Setup Backend

```bash
cd enhanced-app/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run backend server
python main.py
```

The backend will start on **http://localhost:8451**

### 4. Setup Chat Interface

```bash
cd enhanced-app/frontend/chat

# Install dependencies
npm install

# Start development server
npm run dev
```

The chat interface will be available at **http://localhost:8450**

### 5. Setup Merchant Portal

```bash
cd enhanced-app/frontend/merchant-portal

# Install dependencies
npm install

# Start development server (on different port temporarily for dev)
npm run dev
```

The merchant portal will be available at **http://localhost:8451** (note: in dev, you might need to adjust vite config)

## Production Build

### Backend

```bash
cd enhanced-app/backend
pip install -r requirements.txt
python main.py
```

### Frontend (Chat)

```bash
cd enhanced-app/frontend/chat
npm install
npm run build
npm run preview
```

### Frontend (Merchant Portal)

```bash
cd enhanced-app/frontend/merchant-portal
npm install
npm run build
npm run preview
```

## API Documentation

Once the backend is running, visit:
- **API Docs**: http://localhost:8451/docs
- **Health Check**: http://localhost:8451/health

### Key Endpoints

#### Chat API
- `POST /api/chat` - Send message to AI assistant
- `GET /api/checkout/{checkout_id}` - Get checkout details
- `GET /api/orders/{order_id}` - Get order details

#### Merchant Portal API
- `GET /api/merchant/products` - List all products
- `POST /api/merchant/products` - Create new product
- `PUT /api/merchant/products/{id}` - Update product
- `DELETE /api/merchant/products/{id}` - Delete product

## Configuration

### Backend

Edit `enhanced-app/backend/main.py` to configure:
- Ollama URL (default: `http://host.docker.internal:11434`)
- Model name (default: `qwen2.5:latest`)
- Port (default: 8451)

### Frontend

Edit `enhanced-app/frontend/chat/vite.config.ts` and `enhanced-app/frontend/merchant-portal/vite.config.ts` to configure:
- Port numbers
- API proxy settings

## Database

The application uses SQLite for data persistence:
- Location: `enhanced-app/backend/enhanced_app.db`
- Auto-initialized with sample products on first run

## Environment Variables

Create a `.env` file in `enhanced-app/backend/`:

```env
DATABASE_URL=sqlite+aiosqlite:///./enhanced_app.db
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:latest
```

## Project Structure

```
enhanced-app/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── database.py          # SQLAlchemy models
│   ├── ollama_agent.py      # Ollama LLM integration
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile          # (Optional) Docker configuration
│
├── frontend/
│   ├── chat/               # Chat interface
│   │   ├── src/
│   │   │   ├── App.tsx    # Main chat UI
│   │   │   ├── main.tsx
│   │   │   └── index.css
│   │   ├── package.json
│   │   └── vite.config.ts
│   │
│   └── merchant-portal/    # Admin portal
│       ├── src/
│       │   ├── App.tsx    # Product management UI
│       │   ├── main.tsx
│       │   └── index.css
│       ├── package.json
│       └── vite.config.ts
│
├── docker-compose.yml      # (Optional) Docker Compose
└── README.md              # This file
```

## Deployment

### Reverse Proxy Configuration (Nginx)

For production deployment with domain mapping:

```nginx
# Chat Interface - chat.abhinava.xyz
server {
    listen 443 ssl http2;
    server_name chat.abhinava.xyz;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8450;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}

# Merchant Portal & API - app.abhinava.xyz
server {
    listen 443 ssl http2;
    server_name app.abhinava.xyz;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8451;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## Usage Examples

### Chat Interface

1. Open http://localhost:8450
2. Type: "Show me some cookies"
3. The AI will search and display products
4. Use quick action buttons for common tasks
5. Add items to cart through conversation
6. Complete checkout with shipping info

### Merchant Portal

1. Open http://localhost:8451
2. View product statistics on dashboard
3. Click "Add New Product" to create products
4. Edit existing products with the edit icon
5. Delete products (soft delete by default)
6. All changes immediately available to chat agent

## Troubleshooting

### Ollama Connection Issues

If you see "Connection refused" errors:

```bash
# Check if Ollama is running
curl http://localhost:11434/api/version

# If using Docker, use host.docker.internal instead of localhost
# Update OLLAMA_URL in backend configuration
```

### Database Issues

```bash
# Reset database (delete and it will auto-recreate)
rm enhanced-app/backend/enhanced_app.db
python enhanced-app/backend/main.py
```

### Port Conflicts

If ports 8450 or 8451 are in use:

```bash
# Find and kill process using the port
lsof -ti:8450 | xargs kill -9
lsof -ti:8451 | xargs kill -9
```

## Development Notes

- The backend extends the original `business_agent` functionality
- Frontend builds upon the existing `chat-client` design patterns
- No redundant code - all features are additive
- Database is persistent across restarts
- Ollama provides offline AI capabilities

## License

Same as parent project (ucp-sample)

## Support

For issues and questions:
- Check API docs at http://localhost:8451/docs
- Review logs in terminal
- Ensure Ollama is running with correct model

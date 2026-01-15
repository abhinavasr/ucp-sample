# Enhanced Business Agent - Split Architecture with UCP

This is a production-ready implementation demonstrating **two separate systems** communicating over the **Universal Commerce Protocol (UCP)**.

## 🏗️ Architecture Overview

The application is split into two independent backends that communicate via UCP:

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend Layer                          │
├──────────────────────────────┬──────────────────────────────────┤
│  Chat Frontend (Port 3000)   │  Merchant Portal (Port 3001)     │
│  - React + TypeScript        │  - React + TypeScript            │
│  - Tailwind CSS              │  - Tailwind CSS                  │
│  - Vite Dev Server           │  - Vite Dev Server               │
└──────────────┬───────────────┴──────────────┬───────────────────┘
               │                              │
               │ HTTP                         │ HTTP
               │                              │
┌──────────────▼───────────────┐  ┌──────────▼───────────────────┐
│   Chat Backend (Port 8450)   │  │ Merchant Backend (Port 8451) │
│   ========================   │  │ ===========================  │
│   • UCP Client               │  │ • UCP Server                 │
│   • FastAPI                  │  │ • FastAPI                    │
│   • Ollama LLM Integration   │  │ • SQLite Database            │
│   • Shopping Assistant       │  │ • Product Catalog            │
│   • Session Management       │  │ • CRUD API                   │
└──────────────┬───────────────┘  └──────────▲───────────────────┘
               │                              │
               │    UCP REST Protocol         │
               └──────────────────────────────┘
                    /.well-known/ucp
                    /ucp/products/search
```

### Key Components

#### 1. **Chat Backend** (Port 8450) - UCP Client
- **Role**: Consumer/Client
- **Technology**: FastAPI + Ollama LLM + LangChain
- **Responsibilities**:
  - AI-powered chat interface
  - Natural language processing
  - Shopping cart management
  - Checkout session handling
  - **UCP Client**: Discovers and queries merchant backend

#### 2. **Merchant Backend** (Port 8451) - UCP Server
- **Role**: Provider/Server
- **Technology**: FastAPI + SQLAlchemy + SQLite
- **Responsibilities**:
  - Product catalog management
  - Database persistence
  - UCP-compliant REST API
  - **UCP Server**: Exposes discovery endpoint and product search

#### 3. **Frontend Applications**
- **Chat Frontend** (Port 3000): Customer-facing shopping interface
- **Merchant Portal** (Port 3001): Admin interface for product management

## 🔌 UCP Integration

### UCP Discovery Endpoint

The Merchant Backend exposes a standard UCP discovery endpoint:

```bash
GET http://localhost:8451/.well-known/ucp
```

**Response:**
```json
{
  "ucp": {
    "version": "2026-01-11",
    "services": {
      "dev.ucp.shopping": {
        "version": "2026-01-11",
        "spec": "https://ucp.dev/specs/shopping",
        "rest": {
          "schema": "https://ucp.dev/services/shopping/openapi.json",
          "endpoint": "http://localhost:8451"
        }
      }
    },
    "capabilities": [
      {
        "name": "dev.ucp.shopping.product_search",
        "version": "2026-01-11",
        "spec": "https://ucp.dev/specs/shopping/product_search",
        "schema": "https://ucp.dev/schemas/shopping/product_search.json"
      }
    ]
  },
  "merchant": {
    "id": "merchant-001",
    "name": "Enhanced Business Store",
    "url": "http://localhost:8451"
  }
}
```

### UCP Product Search

The Chat Backend uses the UCP client to search products:

```python
# In chat-backend/ucp_client.py
async def search_products(self, query: str = None, limit: int = 10):
    """Search products using UCP product search endpoint."""
    response = await self.client.get(
        f"{self.merchant_url}/ucp/products/search",
        params={"q": query, "limit": limit}
    )
    # Prices are in cents (UCP standard)
    data = response.json()
    return data["items"]
```

The Merchant Backend serves UCP-compliant product data:

```bash
GET http://localhost:8451/ucp/products/search?q=cookies&limit=5
```

**Response:**
```json
{
  "items": [
    {
      "id": "PROD-001",
      "title": "Chocochip Cookies",
      "price": 499,  // Price in cents
      "image_url": "...",
      "description": "Delicious chocolate chip cookies"
    }
  ],
  "total": 1
}
```

## 🚀 Quick Start

### Prerequisites

1. **Python 3.10+**
2. **Node.js 18+**
3. **Ollama** running with a model (e.g., qwen3:8b, qwen2.5:latest, gemma2:latest)

### Installation & Running

1. **Clone the repository**
   ```bash
   cd ucp-sample/enhanced-app
   ```

2. **Configure environment**
   ```bash
   # Edit chat-backend/.env
   OLLAMA_URL=http://192.168.86.41:11434
   OLLAMA_MODEL=qwen3:8b
   MERCHANT_BACKEND_URL=http://localhost:8451

   # Edit merchant-backend/.env
   DATABASE_URL=sqlite+aiosqlite:///./merchant.db
   PORT=8451
   ```

3. **Start all services**
   ```bash
   ./start-split.sh
   ```

   This will start:
   - Merchant Backend (8453) - UCP Server
   - Chat Backend (8452) - UCP Client
   - Chat Frontend (8450) - maps to chat.abhinava.xyz
   - Merchant Portal (8451) - maps to app.abhinava.xyz

4. **Access the applications**
   - **Chat Interface**: http://localhost:8450 (https://chat.abhinava.xyz)
   - **Merchant Portal**: http://localhost:8451 (https://app.abhinava.xyz)
   - **Chat Backend API**: http://localhost:8452/docs
   - **Merchant Backend API**: http://localhost:8453/docs

5. **Stop all services**
   ```bash
   ./stop-split.sh
   ```

## 📁 Project Structure

```
enhanced-app/
├── chat-backend/              # UCP Client Backend
│   ├── main.py               # FastAPI application
│   ├── ollama_agent.py       # LLM-powered agent
│   ├── ucp_client.py         # UCP REST client
│   ├── .env                  # Configuration
│   └── pyproject.toml        # Python dependencies
│
├── merchant-backend/          # UCP Server Backend
│   ├── main.py               # FastAPI application with UCP
│   ├── database.py           # SQLAlchemy models
│   ├── .env                  # Configuration
│   └── pyproject.toml        # Python dependencies
│
├── frontend/
│   ├── chat/                 # Chat Frontend (Port 3000)
│   │   ├── src/
│   │   │   └── App.tsx      # React application
│   │   └── vite.config.ts   # Proxy to chat-backend
│   │
│   └── merchant-portal/      # Admin Frontend (Port 3001)
│       ├── src/
│       │   └── App.tsx      # React application
│       └── vite.config.ts   # Proxy to merchant-backend
│
├── start-split.sh            # Start all services
├── stop-split.sh             # Stop all services
├── README-SPLIT-ARCHITECTURE.md
└── logs/                     # Application logs
```

## 🔍 Testing UCP Communication

### 1. Test UCP Discovery

```bash
# Discover merchant capabilities
curl http://localhost:8453/.well-known/ucp | jq
```

### 2. Test UCP Product Search

```bash
# Search for cookies
curl "http://localhost:8453/ucp/products/search?q=cookies&limit=5" | jq
```

### 3. Test Chat Backend UCP Client

```bash
# The chat backend automatically uses UCP to fetch products
curl -X POST http://localhost:8452/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me cookies available",
    "session_id": "test-session"
  }' | jq
```

The chat backend will:
1. Detect product search intent
2. Call merchant backend via UCP: `GET /ucp/products/search?q=cookies`
3. Convert UCP format (cents) to dollars
4. Send product context to LLM
5. Return AI-generated response with product recommendations

## 🎯 Key Features

### UCP Communication
- ✅ **Discovery**: Chat backend discovers merchant capabilities
- ✅ **Standard Protocol**: Uses UCP-compliant REST endpoints
- ✅ **Price Format**: Handles prices in cents (UCP standard)
- ✅ **Independent Systems**: Both backends can run separately
- ✅ **Extensible**: Easy to add more UCP capabilities

### Chat Backend Features
- 🤖 AI-powered conversation with Ollama
- 🔍 Automatic product search via UCP
- 🛒 Shopping cart management
- 💳 Checkout session handling

### Merchant Backend Features
- 📦 Full CRUD product management
- 🗄️ SQLite database persistence
- 🔌 UCP-compliant REST API
- 📊 Product search and filtering

### Frontend Features
- ⚛️ React + TypeScript + Tailwind CSS
- 🎨 Modern, responsive UI
- 🔄 Real-time updates
- 📱 Mobile-friendly design

## 🔧 Configuration

### Chat Backend (.env)
```env
OLLAMA_URL=http://192.168.86.41:11434
OLLAMA_MODEL=qwen3:8b
HOST=0.0.0.0
PORT=8452
MERCHANT_BACKEND_URL=http://localhost:8453
```

### Merchant Backend (.env)
```env
DATABASE_URL=sqlite+aiosqlite:///./merchant.db
HOST=0.0.0.0
PORT=8453
MERCHANT_NAME=Enhanced Business Store
MERCHANT_ID=merchant-001
MERCHANT_URL=http://localhost:8453
```

## 📊 Port Allocation

| Service            | Port | Type         | Purpose                    |
|--------------------|------|--------------|----------------------------|
| Chat Frontend      | 8450 | Vite Dev     | Customer interface (chat.abhinava.xyz) |
| Merchant Portal    | 8451 | Vite Dev     | Admin interface (app.abhinava.xyz)     |
| Chat Backend       | 8452 | FastAPI      | UCP Client + AI Agent      |
| Merchant Backend   | 8453 | FastAPI      | UCP Server + Product DB    |

## 🔐 Production Deployment

For production use:

1. **Set specific CORS origins** in both backends
2. **Use production databases** (PostgreSQL recommended)
3. **Enable HTTPS** with reverse proxy (nginx/Caddy)
4. **Secure API authentication** (JWT, API keys)
5. **Configure Ollama** for production workloads
6. **Monitor UCP endpoints** for performance
7. **Implement rate limiting** on UCP endpoints

## 📝 Logs

View real-time logs:

```bash
# Merchant Backend
tail -f logs/merchant-backend.log

# Chat Backend
tail -f logs/chat-backend.log

# Chat Frontend
tail -f logs/chat-frontend.log

# Merchant Portal
tail -f logs/merchant-portal.log
```

## 🐛 Troubleshooting

### Port Conflicts
```bash
# Check what's using a port
lsof -i :8450
lsof -i :8453

# Kill process on port
kill -9 $(lsof -ti:8450)
```

### UCP Discovery Fails
```bash
# Verify merchant backend is running
curl http://localhost:8453/health

# Check UCP endpoint
curl http://localhost:8453/.well-known/ucp
```

### Ollama Connection Issues
```bash
# Test Ollama connection
curl http://192.168.86.41:11434/api/tags

# Update OLLAMA_URL in chat-backend/.env
```

## 🎓 Learning Resources

- [UCP Specification](https://github.com/Universal-Commerce-Protocol)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Ollama Documentation](https://ollama.ai/docs)
- [LangChain Documentation](https://python.langchain.com/)

## 📄 License

Apache License 2.0

---

**Built with UCP** - Demonstrating how two independent systems can communicate seamlessly over a universal commerce protocol.

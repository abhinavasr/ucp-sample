# Configuration Guide

This guide explains how to configure the Enhanced Business Agent application using environment variables.

## Quick Setup

1. **Copy the example environment file:**
   ```bash
   cd enhanced-app/backend
   cp .env.example .env
   ```

2. **Edit the `.env` file** with your preferred settings

3. **Restart the backend** to apply changes

## Environment Variables Reference

### Ollama Configuration

#### `OLLAMA_URL`
The URL where your Ollama instance is running.

**Options:**
- `http://localhost:11434` - Local Ollama installation (default for non-Docker)
- `http://host.docker.internal:11434` - When running backend in Docker (default)
- `http://192.168.1.100:11434` - Remote Ollama server

**Default:** `http://host.docker.internal:11434`

**Example:**
```env
OLLAMA_URL=http://localhost:11434
```

#### `OLLAMA_MODEL`
The LLM model to use for the chat agent.

**Supported Models:**
- `qwen2.5:latest` - Qwen 2.5 (recommended, default)
- `gemma2:latest` - Google Gemma 2
- `llama2:latest` - Meta Llama 2
- `mistral:latest` - Mistral AI
- `phi3:latest` - Microsoft Phi-3

**Default:** `qwen2.5:latest`

**Example:**
```env
OLLAMA_MODEL=gemma2:latest
```

**Note:** You must pull the model first:
```bash
ollama pull qwen2.5:latest
```

### Database Configuration

#### `DATABASE_URL`
SQLite database connection string.

**Format:** `sqlite+aiosqlite:///<path>`

**Options:**
- `sqlite+aiosqlite:///./enhanced_app.db` - Local file in backend directory (default)
- `sqlite+aiosqlite:///./data/enhanced_app.db` - Separate data directory
- `sqlite+aiosqlite:////absolute/path/to/db.db` - Absolute path

**Default:** `sqlite+aiosqlite:///./enhanced_app.db`

**Example:**
```env
DATABASE_URL=sqlite+aiosqlite:///./data/shopping.db
```

**Note:** For production, consider PostgreSQL:
```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/dbname
```

### Server Configuration

#### `HOST`
The host address the server binds to.

**Options:**
- `0.0.0.0` - Listen on all network interfaces (default)
- `127.0.0.1` - Localhost only
- Specific IP address

**Default:** `0.0.0.0`

#### `PORT`
The port number the server listens on.

**Default:** `8451`

**Example:**
```env
PORT=9000
```

### Application URLs (Frontend Configuration)

#### `CHAT_URL`
The URL where the chat interface is accessible.

**Default:** `https://chat.abhinava.xyz`

**Examples:**
```env
CHAT_URL=http://localhost:8450  # Development
CHAT_URL=https://chat.example.com  # Production
```

#### `MERCHANT_URL`
The URL where the merchant portal is accessible.

**Default:** `https://app.abhinava.xyz`

**Examples:**
```env
MERCHANT_URL=http://localhost:8451  # Development
MERCHANT_URL=https://admin.example.com  # Production
```

## Common Configuration Scenarios

### Local Development (No Docker)

```env
# .env
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:latest
DATABASE_URL=sqlite+aiosqlite:///./enhanced_app.db
HOST=0.0.0.0
PORT=8451
CHAT_URL=http://localhost:8450
MERCHANT_URL=http://localhost:8451
```

### Docker Deployment

```env
# .env
OLLAMA_URL=http://host.docker.internal:11434
OLLAMA_MODEL=qwen2.5:latest
DATABASE_URL=sqlite+aiosqlite:///./data/enhanced_app.db
HOST=0.0.0.0
PORT=8451
CHAT_URL=https://chat.yourdomain.com
MERCHANT_URL=https://app.yourdomain.com
```

### Production with Remote Ollama

```env
# .env
OLLAMA_URL=http://ollama-server.internal:11434
OLLAMA_MODEL=qwen2.5:latest
DATABASE_URL=postgresql+asyncpg://user:password@db-server:5432/shopping
HOST=0.0.0.0
PORT=8451
CHAT_URL=https://chat.yourdomain.com
MERCHANT_URL=https://app.yourdomain.com
```

### Testing Different Models

```env
# .env - Testing with Gemma
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=gemma2:latest
DATABASE_URL=sqlite+aiosqlite:///./enhanced_app.db
HOST=0.0.0.0
PORT=8451
```

## Troubleshooting

### Issue: "Connection refused" to Ollama

**Solution 1:** Check if Ollama is running
```bash
curl http://localhost:11434/api/version
```

**Solution 2:** Update OLLAMA_URL in .env
```env
# If using Docker, use:
OLLAMA_URL=http://host.docker.internal:11434

# If running locally, use:
OLLAMA_URL=http://localhost:11434
```

**Solution 3:** Start Ollama
```bash
ollama serve
```

### Issue: Model not found

**Error:** `model 'qwen2.5:latest' not found`

**Solution:** Pull the model first
```bash
ollama pull qwen2.5:latest
```

Or change to a model you have:
```env
OLLAMA_MODEL=llama2:latest
```

### Issue: Database locked

**Solution:** Change database location
```env
DATABASE_URL=sqlite+aiosqlite:///./data/enhanced_app.db
```

Create the data directory:
```bash
mkdir -p enhanced-app/backend/data
```

### Issue: Port already in use

**Error:** `Address already in use: 8451`

**Solution 1:** Change port in .env
```env
PORT=9000
```

**Solution 2:** Kill process using the port
```bash
lsof -ti:8451 | xargs kill -9
```

## Environment Variables Priority

The application uses the following priority order:

1. **Environment variables** set in shell
2. **`.env` file** in backend directory
3. **Default values** in code

Example:
```bash
# Override .env temporarily
OLLAMA_MODEL=gemma2:latest python main.py
```

## Security Best Practices

1. **Never commit `.env` files** to Git
   - Already in `.gitignore`

2. **Use different `.env` for production**
   ```bash
   cp .env.example .env.production
   # Edit .env.production
   ```

3. **Protect sensitive credentials**
   ```env
   # Bad - hardcoded password
   DATABASE_URL=postgresql://user:password123@host/db

   # Good - use secrets management
   DATABASE_URL=${DATABASE_URL}
   ```

4. **Restrict file permissions**
   ```bash
   chmod 600 .env
   ```

## Verification

After configuring, verify your settings:

```bash
# Check Ollama connection
curl $OLLAMA_URL/api/version

# Check database
ls -lh enhanced_app.db

# Check server starts
python main.py
# Should see: "Application startup complete"
```

## Getting Help

If you encounter issues:

1. Check backend logs for errors
2. Verify all environment variables are set correctly
3. Ensure Ollama is running and accessible
4. Check the DEPLOYMENT.md for production setup
5. Review API documentation at http://localhost:8451/docs

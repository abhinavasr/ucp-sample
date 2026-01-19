#!/bin/bash
# Stop all UCP sample services

echo "Stopping UCP Sample Services..."

# Stop chat backend
echo "  Stopping chat backend..."
pkill -f "chat-backend.*main.py" || true
pkill -f "python3 main.py" 2>/dev/null || true

# Stop merchant backend
echo "  Stopping merchant backend..."
pkill -f "merchant-backend.*main.py" || true

# Stop frontend services
echo "  Stopping frontend services..."
pkill -f "vite" || true
pkill -f "node.*vite" || true
pkill -f "npm.*dev" || true

# Give processes time to terminate
sleep 2

echo "✓ All services stopped"

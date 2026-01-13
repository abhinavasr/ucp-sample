#!/bin/bash

# Enhanced Business Agent - Stop Script

echo "🛑 Stopping Enhanced Business Agent..."

# Read PIDs and kill processes
if [ -f "pids/backend.pid" ]; then
    kill $(cat pids/backend.pid) 2>/dev/null && echo "✓ Backend stopped"
    rm pids/backend.pid
fi

if [ -f "pids/chat.pid" ]; then
    kill $(cat pids/chat.pid) 2>/dev/null && echo "✓ Chat interface stopped"
    rm pids/chat.pid
fi

if [ -f "pids/merchant.pid" ]; then
    kill $(cat pids/merchant.pid) 2>/dev/null && echo "✓ Merchant portal stopped"
    rm pids/merchant.pid
fi

# Also kill by port (backup method)
lsof -ti:8450 | xargs kill -9 2>/dev/null || true
lsof -ti:8451 | xargs kill -9 2>/dev/null || true

echo "✓ All services stopped"

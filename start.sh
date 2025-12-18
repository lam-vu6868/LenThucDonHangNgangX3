#!/bin/bash

set -e

# Lấy thư mục hiện tại của file script (tự động đúng dù bạn chạy ở đâu)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "📦 Đang khởi động BACKEND..."
cd "$SCRIPT_DIR/be"
source venv/bin/activate
uvicorn main:app --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!
echo "✅ Backend chạy ở port 8000 (PID: $BACKEND_PID)"

echo "🌐 Đang khởi động FRONTEND..."
cd "$SCRIPT_DIR/fe"
python3 -m http.server 3000

echo "🛑 Đang tắt backend..."
kill "$BACKEND_PID" || true
echo "✅ Đã tắt backend."
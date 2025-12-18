#!/bin/bash

set -e

# Lấy thư mục hiện tại của file script (tự động đúng dù bạn chạy ở đâu)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Kill process cũ nếu có
echo "🔍 Đang kiểm tra và dừng process cũ..."
# Thử dùng lsof trước
if command -v lsof &> /dev/null; then
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
else
    # Nếu không có lsof, dùng fuser hoặc netstat
    if command -v fuser &> /dev/null; then
        fuser -k 8000/tcp 2>/dev/null || true
    else
        # Dùng netstat và awk
        netstat -tlnp 2>/dev/null | grep :8000 | awk '{print $7}' | cut -d'/' -f1 | xargs kill -9 2>/dev/null || true
    fi
fi
sleep 1

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
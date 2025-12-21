#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Hàm dọn dẹp khi nhấn Ctrl+C
cleanup() {
    echo -e "\n🛑 Đang tắt các tiến trình..."
    kill $BACKEND_PID 2>/dev/null || true
    exit
}
trap cleanup SIGINT

echo "🔍 Đang giải phóng port 8000 và 3000..."
fuser -k 8000/tcp 2>/dev/null || true
fuser -k 3000/tcp 2>/dev/null || true
sleep 1

echo "📦 Đang khởi động BACKEND..."
cd "$SCRIPT_DIR/be"
# Kiểm tra nếu venv tồn tại
if [ -d "venv" ]; then
    source venv/bin/activate
    # Dùng 0.0.0.0 để Windows dễ truy cập
    uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    echo "✅ Backend PID: $BACKEND_PID"
else
    echo "❌ Không tìm thấy venv tại $SCRIPT_DIR/be"
    exit 1
fi

echo "🌐 Đang khởi động FRONTEND tại http://localhost:3000"
cd "$SCRIPT_DIR/fe"
python3 -m http.server 3000
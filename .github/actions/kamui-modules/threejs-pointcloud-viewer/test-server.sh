#!/bin/bash
# Test server script for Point Cloud Viewer testing
# HTTPサーバーパス問題解決用テストスクリプト

echo "🚀 Starting HTTP server for Point Cloud Viewer testing..."
echo "📁 Server directory: $(pwd)"
echo "🌐 Test URLs will be available at:"
echo "   - Refactored Viewer: http://localhost:8000/test-refactored-viewer.html"
echo "   - Simple Test: http://localhost:8000/test-simple-load.html"
echo ""
echo "⏹️  Press Ctrl+C to stop the server"
echo ""

# Start Python HTTP server
python3 -m http.server 8000
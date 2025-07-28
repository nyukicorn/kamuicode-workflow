#!/bin/bash
# Test server script for 360° Panorama Viewer testing
# パノラマビューアーテスト用サーバー起動スクリプト

echo "🌐 Starting HTTP server for 360° Panorama Viewer testing..."
echo "📁 Server directory: $(pwd)"
echo "🎯 Test URLs will be available at:"
echo "   - Panorama Test: http://localhost:8001/test-panorama-viewer.html"
echo ""
echo "📝 Test Instructions:"
echo "   1. Open http://localhost:8001/test-panorama-viewer.html in your browser"
echo "   2. Wait for the spherical test pattern to load"
echo "   3. Test mouse orbit, zoom, and keyboard controls"
echo "   4. Verify shared components integration (gravity, audio, UI)"
echo "   5. Check auto-rotation and particle effects"
echo ""
echo "🎮 Available Controls:"
echo "   - Mouse: Orbit camera (360° panoramic view)"
echo "   - Scroll: Zoom in/out (stay inside sphere)"
echo "   - Space: Toggle auto-rotation"
echo "   - WASD: Alternative navigation"
echo "   - UI Panel: Hover top-left for controls"
echo ""
echo "⏹️  Press Ctrl+C to stop the server"
echo ""

# Start Python HTTP server on port 8001 (different from point cloud viewer)
python3 -m http.server 8001
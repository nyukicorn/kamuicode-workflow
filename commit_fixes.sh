#!/bin/bash

echo "Starting commit process for video and music merge fixes..."

# Add the specific workflow file
git add .github/workflows/create-music-video-orchestrated-improved.yml

# Create the commit with the detailed message
git commit -m "Fix video and music merge issue in original workflow

🔧 Fixes:
- Add FFmpeg installation for audio processing
- Add Node.js/SDK setup for Claude Code execution
- Improve FFmpeg commands with specific parameters
- Simplify prompt for better success rate
- Use -stream_loop -1 and -shortest for proper audio sync

🎯 This should resolve the issue where videos and music were not merging properly and not appearing on GitHub Pages.

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to remote
git push origin main

echo "Commit and push completed!"
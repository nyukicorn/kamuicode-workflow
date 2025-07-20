#!/usr/bin/env python3

# 分析スクリプトを直接実行
try:
    exec(open("/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250720-16398936614/analysis/direct_analysis.py").read())
except Exception as e:
    print(f"実行エラー: {e}")
    import traceback
    traceback.print_exc()
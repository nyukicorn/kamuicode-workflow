#!/usr/bin/env python3
import subprocess
import sys
import os

# 分析スクリプトを実行
script_path = "/home/runner/work/kamuicode-workflow/kamuicode-workflow/music-video-20250720-16398936614/analysis/music_analysis_report.py"

try:
    result = subprocess.run([sys.executable, script_path], 
                          capture_output=True, 
                          text=True, 
                          cwd=os.path.dirname(script_path))
    
    print("STDOUT:")
    print(result.stdout)
    
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    print(f"Return code: {result.returncode}")
    
except Exception as e:
    print(f"Execution error: {e}")
    
    # 直接実行を試行
    print("\nTrying direct execution...")
    try:
        exec(open(script_path).read())
    except Exception as e2:
        print(f"Direct execution error: {e2}")
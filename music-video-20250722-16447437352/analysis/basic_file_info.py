#!/usr/bin/env python3
"""
基本的なファイル情報取得ツール
"""

import os
import sys

def get_file_info(file_path):
    """ファイルの基本情報を取得"""
    if not os.path.exists(file_path):
        return f"エラー: ファイルが見つかりません - {file_path}"
    
    try:
        file_size = os.path.getsize(file_path)
        file_stat = os.stat(file_path)
        
        return {
            'ファイル名': os.path.basename(file_path),
            'フルパス': os.path.abspath(file_path),
            'ファイルサイズ': f"{file_size:,} bytes ({file_size / 1024:.2f} KB)",
            '作成日時': file_stat.st_ctime,
            '更新日時': file_stat.st_mtime,
            'ファイル拡張子': os.path.splitext(file_path)[1]
        }
    except Exception as e:
        return f"エラー: {e}"

def main():
    if len(sys.argv) != 2:
        print("使用方法: python basic_file_info.py <ファイルパス>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    info = get_file_info(file_path)
    
    if isinstance(info, dict):
        print("📁 ファイル基本情報")
        print("=" * 30)
        for key, value in info.items():
            print(f"{key}: {value}")
    else:
        print(info)

if __name__ == "__main__":
    main()
"""
Main entry point for the recommendation system
"""

import argparse
import webbrowser
import threading
import time
from recommender.web_app import app

def open_browser():
    """在默认浏览器中打开应用"""
    time.sleep(1)  # 等待服务器启动
    webbrowser.open('http://127.0.0.1:5000/')

def main():
    parser = argparse.ArgumentParser(description='推荐系统')
    parser.add_argument('--cli', action='store_true', help='使用命令行界面')
    parser.add_argument('--no-browser', action='store_true', help='不自动打开浏览器')
    args = parser.parse_args()
    
    if not args.no_browser:
        threading.Thread(target=open_browser).start()
    
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    main()
else:
    # 当作为服务运行时，禁用debug模式
    application = app 
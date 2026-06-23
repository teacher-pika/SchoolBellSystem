import sys
import os

# 將專案根目錄加入 Python 路徑
# 這樣才能正確 import app 裡面的模組
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import logging
from logging.handlers import RotatingFileHandler

# 取得專案根目錄 (pybell)
# __file__ -> pybell/app/logger.py
# os.path.dirname(__file__) -> pybell/app
# os.path.dirname(...) -> pybell
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOG_DIR = os.path.join(PROJECT_ROOT, 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'app.log')

def setup_logger():
    """設定日誌系統"""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    # 建立 logger
    logger = logging.getLogger('SchoolBell')
    logger.setLevel(logging.INFO)

    # 建立 formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # 建立 handler，設定滾動策略
    # 每個檔案最大 1MB，保留 5 個備份
    handler = RotatingFileHandler(LOG_FILE, maxBytes=1024*1024, backupCount=5, encoding='utf-8')
    handler.setFormatter(formatter)

    # 將 handler 加入 logger
    if not logger.handlers:
        logger.addHandler(handler)
        
    # 同時也輸出到 console，方便開發時查看
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
         logger.addHandler(console_handler)

    return logger

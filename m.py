import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from urllib.parse import urljoin
import os
import time
import urllib3
import re

# 禁用 SSL 安全警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- 从系统变量读取配置 (更安全) ---
SMTP_SERVER = 'smtp.qq.com'
SMTP_PORT = 465
SENDER_EMAIL = '610712212@qq.com' 
# 从 GitHub Secrets 中读取授权码
SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD') 
RECEIVER_EMAIL = 'liulu_sch@163.com'
TARGET_URL = 'https://www.ief.ac.cn/zptext/'

def send_email(subject, body):
    # ... (保持你原有的 send_email 函数逻辑不变) ...
    pass

def fetch_latest_job():
    # ... (保持你原有的 fetch_latest_job 函数逻辑不变) ...
    pass

def run_once():
    """执行单次检查"""
    record_file = 'last_job_record.txt'
    last_record = ''
    if os.path.exists(record_file):
        with open(record_file, 'r', encoding='utf-8') as f:
            last_record = f.read().strip()
            
    current_title, current_link, current_date = fetch_latest_job()
    if not current_title:
        return

    current_record = f"{current_title}|{current_date}"
    
    if current_record != last_record:
        print(f"🎉 发现更新！正在发送邮件...")
        # ... (执行发送邮件逻辑) ...
        
        # 更新本地记录文件
        with open(record_file, 'w', encoding='utf-8') as f:
            f.write(current_record)
        return True # 表示有更新
    else:
        print("✅ 无需更新。")
        return False

if __name__ == '__main__':
    run_once()

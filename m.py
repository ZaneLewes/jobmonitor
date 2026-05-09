import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from urllib.parse import urljoin
import os
import time
import urllib3
import re

# 1. 禁用 SSL 安全警告（针对部分政府网站证书问题）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- 2. 配置信息 ---
SMTP_SERVER = 'smtp.qq.com'
SMTP_PORT = 465
SENDER_EMAIL = '610712212@qq.com' 
# 从 GitHub Secrets 中读取名为 SENDER_PASSWORD 的环境变量
SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD') 
RECEIVER_EMAIL = 'liulu_sch@163.com'
TARGET_URL = 'https://www.ief.ac.cn/zptext/'

def send_email(subject, body):
    """发送邮件的函数"""
    if not SENDER_PASSWORD:
        print("❌ 错误：未检测到 SENDER_PASSWORD 环境变量，请检查 GitHub Secrets 配置。")
        return

    try:
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL

        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        print(f"[{time.strftime('%H:%M:%S')}] 📧 邮件通知发送成功！")
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")

def fetch_latest_job():
    """抓取网页并提取最新的招聘标题、链接和发布时间"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    try:
        # 增加超时设置，防止 GitHub Actions 卡死
        response = requests.get(TARGET_URL, headers=headers, timeout=30, verify=False)
        response.raise_for_status()
        response.encoding = response.apparent_encoding 
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 寻找包含招聘路径的链接
        all_links = soup.find_all('a', href=True)
        job_links = [a for a in all_links if '/zptext/info/' in a.get('href')]
        
        if job_links:
            latest_item = job_links[0]
            title = latest_item.get_text(strip=True) or latest_item.get('title', '未知标题')
            link = urljoin(TARGET_URL, latest_item.get('href'))
            
            # 提取发布时间
            pub_date = "未知时间"
            parent = latest_item.parent
            date_match = re.search(r'\d{4}-\d{2}-\d{2}', parent.get_text())
            if date_match:
                pub_date = date_match.group()
            
            print(f"🔍 检测到最新公告: {title} [{pub_date}]")
            return title, link, pub_date
        else:
            print("⚠️ 未匹配到招聘链接，请检查网页结构。")
            return None, None, None
            
    except Exception as e:
        print(f"❌ 网页抓取失败: {e}")
        return None, None, None

def run_once():
    """主逻辑：运行单次检查（适合 GitHub Actions 定时任务）"""
    print(f"🚀 监控检查启动：{time.strftime('%Y-%m-%d %H:%M:%S')}")
    record_file = 'last_job_record.txt'
    
    # 加载本地记录
    last_record = ''
    if os.path.exists(record_file):
        with open(record_file, 'r', encoding='utf-8') as f:
            last_record = f.read().strip()
            
    # 执行抓取
    result = fetch_latest_job()
    
    # 检查返回结果是否有效，防止解包 NoneType 错误
    if result[0] is None:
        print("停止检查：未能成功获取网页内容。")
        return

    current_title, current_link, current_date = result
    current_record = f"{current_title}|{current_date}"
    
    # 对比记录
    if current_record != last_record:
        print(f"🎉 发现更新！正在发送邮件...")
        
        subject = f"📢 招聘更新：{current_title}"
        email_body = (
            f"您关注的招聘网有新动态：\n"
            f"------------------------------\n"
            f"【通知题目】：{current_title}\n"
            f"【发布时间】：{current_date}\n"
            f"【详情链接】：{current_link}\n"
            f"------------------------------\n"
            f"检测时间：{time.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        send_email(subject, email_body)
        
        # 更新本地记录文件
        with open(record_file, 'w', encoding='utf-8') as f:
            f.write(current_record)
        print("✅ 记录已更新。")
    else:
        print(f"✅ 暂无新公告。")

if __name__ == '__main__':
    run_once()

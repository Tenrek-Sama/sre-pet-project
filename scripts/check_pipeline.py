#!/usr/bin/env python3
"""Проверка статуса GitHub Actions пайплайна."""
import os
import sys
import argparse
import requests
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(subject: str, message: str):
    """Отправить email через SMTP Yandex"""
    smtp_server = 'smtp.yandex.ru'
    smtp_port = 587
    sender_email = 'jozheg9@yandex.ru'
    sender_password = os.getenv('MAIL_PASSWORD')  # пароль из .env
    receiver_email = 'd_war_f@mail.ru'  # себе же
    
    if not sender_password:
        print("⚠️ Set MAIL_PASSWORD in .env")
        return
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))
    
    try:
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("📧 Email notification sent")
    except Exception as e:
        print(f"⚠️ Email error: {e}")
load_dotenv()

def send_telegram(token: str, chat_id: str, message: str):
    """Отправить сообщение в Telegram."""
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML',
    }
    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            print("📱 Telegram notification sent")
        else:
            print(f"⚠️ Telegram returned {response.status_code}: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Telegram error: {e}")

def check_pipeline(owner: str, repo: str, token: str) -> int:
    """Проверить последний пайплайн. Вернуть exit code."""
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github+json',
    }
    
    url = f'https://api.github.com/repos/{owner}/{repo}/actions/runs'
    print(f"🔍 Checking {owner}/{repo}...")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
    except requests.exceptions.Timeout:
        print("❌ API timeout", file=sys.stderr)
        return 2
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to GitHub API", file=sys.stderr)
        return 2
    
    if response.status_code != 200:
        print(f"❌ API returned {response.status_code}", file=sys.stderr)
        if response.status_code == 401:
            print("   Check GITHUB_TOKEN", file=sys.stderr)
        elif response.status_code == 404:
            print("   Check repo name and owner", file=sys.stderr)
        return 2
    
    data = response.json()
    runs = data.get('workflow_runs', [])
    
    if not runs:
        print("❌ No runs found")
        return 2
    
    latest = runs[0]
    run_name = latest.get('name', 'Unknown')
    status = latest.get('status', 'Unknown')
    conclusion = latest.get('conclusion', 'Unknown')
    
    print(f"  Workflow: {run_name}")
    print(f"  Status: {status}")
    print(f"  Conclusion: {conclusion}")
    
    if status == 'completed' and conclusion == 'success':
        print("✅ Pipeline green")
        return 0

    elif status == 'completed' and conclusion == 'failure':
        print("❌ Pipeline failed")
        
        # Telegram
        tg_token = os.getenv('TG_BOT_TOKEN')
        tg_chat_id = os.getenv('TG_CHAT_ID')
        if tg_token and tg_chat_id:
            message = f"❌ CI/CD failed in {owner}/{repo}\n\nWorkflow: {run_name}"
            send_telegram(tg_token, tg_chat_id, message)
        
        # Email (резервный канал)
        subject = f"❌ CI/CD failed: {owner}/{repo}"
        message = f"Workflow: {run_name}\nStatus: {status}\nConclusion: {conclusion}"
        send_email(subject, message)
        
        return 1

    else:
        print(f"⏳ Pipeline {status}")
        return 2

def main():
    parser = argparse.ArgumentParser(description='Check GitHub Actions pipeline status')
    parser.add_argument('-o', '--owner', help='GitHub username/org')
    parser.add_argument('-r', '--repo', help='Repository name')
    args = parser.parse_args()
    
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("❌ Set GITHUB_TOKEN", file=sys.stderr)
        sys.exit(2)
    
    owner = args.owner or os.getenv('REPO_OWNER', 'your-username')
    repo = args.repo or os.getenv('REPO_NAME', 'sre-pet-project')
    
    sys.exit(check_pipeline(owner, repo, token))

if __name__ == '__main__':
    main()

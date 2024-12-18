import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests

from .utils.config_parser import config

def serverchan(title, desp='', options=None):
    """
    照抄自 https://github.com/easychen/serverchan-demo
    """
    sendkey = config.server_chan()
    options = options if options else {}
    # 判断 sendkey 是否以 'sctp' 开头，并提取数字构造 URL
    if sendkey.startswith('sctp'):
        match = re.match(r'sctp(\d+)t', sendkey)
        if match:
            num = match.group(1)
            url = f'https://{num}.push.ft07.com/send/{sendkey}.send'
        else:
            raise ValueError('Invalid sendkey format for sctp')
    else:
        url = f'https://sctapi.ftqq.com/{sendkey}.send'
    data = {
        'title': title,
        'desp': desp,
        **options
    }
    response = requests.post(url, json=data)
    result = response.json()
    return result


def send_email(subject, body):
    email_account = config.mail()
    try:
        # 创建邮件内容
        msg = MIMEMultipart()
        msg['From'] = email_account.get('account')
        msg['To'] = email_account.get('mail_to')
        msg['Subject'] = subject

        # 邮件正文内容
        msg.attach(MIMEText(body, 'plain'))

        # 创建 SMTP 会话
        server = smtplib.SMTP(email_account.get('smtp_server'), email_account.get('smtp_port'))

        if email_account.get('tls'):
            server.starttls()  # 启用 TLS 加密

        # 登录到 SMTP 服务器
        server.login(email_account.get('account'), email_account.get('password'))

        # 发送邮件
        server.sendmail(email_account.get('account'), email_account.get('mail_to'), msg.as_string())

        # 退出 SMTP 会话
        server.quit()

        print(f"邮件发送成功到 {email_account.get('mail_to')}")
    except Exception as e:
        print(f"邮件发送失败: {str(e)}")
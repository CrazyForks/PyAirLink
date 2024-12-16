import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests


def serverchan(sendkey, title, desp='', options=None):
    """
    照抄自 https://github.com/easychen/serverchan-demo
    """

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


def send_email(smtp_server, smtp_port, sender_email, sender_password, recipient_email, subject, body, use_tls=False):
    try:
        # 创建邮件内容
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        # 邮件正文内容
        msg.attach(MIMEText(body, 'plain'))

        # 创建 SMTP 会话
        server = smtplib.SMTP(smtp_server, smtp_port)

        if use_tls:
            server.starttls()  # 启用 TLS 加密

        # 登录到 SMTP 服务器
        server.login(sender_email, sender_password)

        # 发送邮件
        server.sendmail(sender_email, recipient_email, msg.as_string())

        # 退出 SMTP 会话
        server.quit()

        print(f"邮件发送成功到 {recipient_email}")
    except Exception as e:
        print(f"邮件发送失败: {str(e)}")
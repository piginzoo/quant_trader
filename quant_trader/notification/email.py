# !/usr/bin/env python
# -*- coding:utf-8 -*-
import logging

from quant_trader import notification
from quant_trader.utils import CONF

logger = logging.getLogger(__name__)

import smtplib
from email.mime.text import MIMEText
from email.header import Header


def send_msg(name, email, level, msg):
    uid = CONF['email']['uid']
    pwd = CONF['email']['pwd']
    host = CONF['email']['host']

    subject = f'量化投资通知 - {notification.C_NAME[level]}'
    receivers = [email]  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

    # 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码
    message = MIMEText(msg, 'plain', 'utf-8')
    message['From'] = Header("量化机器人", 'utf-8')  # 发送者
    message['To'] = Header("量化机器人", 'utf-8')  # 接收者
    message['Subject'] = Header(subject, 'utf-8')

    try:
        # logger.info("发送邮件[%s]:[%s:%s]", host,uid,pwd)
        smtp = smtplib.SMTP_SSL(host)
        smtp.login(uid, pwd)
        smtp.sendmail(uid, receivers, message.as_string())
        logger.info("发往[%s]的邮件[%s]通知完成", name, email)
        return True
    except smtplib.SMTPException:
        logger.exception("发往[%s]的邮件[%s]出现异常", name, email)
        return False

# !/usr/bin/env python
# -*- coding:utf-8 -*-
import requests
import logging

from quant_trader.utils import CONF

logger = logging.getLogger(__name__)


def send_msg(name, url, level, msg):
    """
    给企业微信群推送消息
    接口文档：https://developer.work.weixin.qq.com/document/path/91770?version=4.0.6.90540
    :param msg: 消息内容
    :return:
    """
    logger.info("开始推送微信消息：%r", msg)

    post_data = {
        "msgtype": "text",
        "text": {
            "content": msg[:2040] # content	是	文本内容，最长不超过2048个字节，必须是utf8编码
        }
    }
    headers = {'Content-Type': 'application/json'}
    try:
        requests.post(url, json=post_data, headers=headers)
        logger.info("发往企业微信机器人[%s]的通知完成", name)
        return True
    except Exception:
        logger.exception("发往企业微信机器人[%s]的消息，发生异常", name)
        return False

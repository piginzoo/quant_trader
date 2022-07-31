#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
import logging
from json import JSONDecodeError

from flask import Blueprint

from quant_trader.notification import weixin_api

logger = logging.getLogger(__name__)

app = Blueprint('callback', __name__, url_prefix="/")

"""
企业微信机器人的回调接口，未实现完，暂时废弃
"""

def request2json(request):
    logger.debug("Got json data:%d bytes", len(request))
    try:
        data = request.decode('utf-8')
        data = data.replace('\r\n', '')
        data = data.replace('\n', '')
        data = json.loads(data)
        return data
    except JSONDecodeError as e:
        logger.exception("JSon数据格式错误")
        raise Exception("JSon数据格式错误:" + str(e))


@app.route('callback', methods=["GET"])
def callback():
    return weixin_api.verify(), 200
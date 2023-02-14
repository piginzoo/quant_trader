#!/usr/bin/python
# -*- coding: UTF-8 -*-
import logging

from flask import Blueprint, request, render_template

from quant_trader.utils import CONF
from quant_trader.server import broker

logger = logging.getLogger(__name__)

app = Blueprint('query', __name__, url_prefix="/")

"""
此controller仅用于html页面导航，真正的各种action操作，都转移到controller_api里面去了（json api）
"""

@app.route('query', methods=["GET"])
def query():

    token = request.args.get('token', None)
    action = request.args.get('action', None)
    broker_name = request.args.get('broker', None)

    # 加一个安全限制
    # if token is None or token != CONF['broker_server']['token']:
    #     logger.error("客户端的toke[%r]!=配置的[%s]，无效的访问", token, CONF['broker_server']['token'])
    #     return "无效的访问", 400

    query_url = f"/api?action={action}&token={token}&broker={broker_name}"

    if action:
        return render_template('table.html', query_url=query_url,token=token)
    else:
        return render_template('index.html',token=token)
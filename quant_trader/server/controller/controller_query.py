#!/usr/bin/python
# -*- coding: UTF-8 -*-
import logging
import os
import subprocess
import time

from bs4 import BeautifulSoup
from flask import Blueprint, request, render_template
from flask import Markup

from quant_trader.server.etf import generator
from quant_trader.utils import CONF

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


    if action == 'etf':
        jpg_urls = generator.generate(CONF)
        stat = os.stat(f'web_root{jpg_urls[0]}')
        file_timestamp = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(stat.st_ctime))
        return render_template('jpg.html', images=jpg_urls, time=file_timestamp)

    # 为了可以方便地重置warp ip
    if action == 'chatgpt':
        logger.debug("刷新了Warp地址")
        # warp-cli disconnect && sleep 3 &&warp-cli connect
        # os.popen('/usr/bin/warp-cli disconnect && sleep 3 &&/usr/bin/warp-cli connect')
        process = subprocess.Popen(['/usr/bin/warp-cli disconnect && sleep 3 &&/usr/bin/warp-cli connect'], stdout=subprocess.PIPE, shell=True)
        output, error = process.communicate()
        output = output.decode('utf-8')
        if 'Success' in output:
            return "已成功重置IP，请返回chatgpt重试，如仍然429错误，继续运行此url"
        else:
            return f"尝试重置IP失败，原因：{output}"

    # 加一个安全限制
    if token is None or token != CONF['broker_server']['token']:
        logger.error("客户端的toke[%r]!=配置的[%s]，无效的访问", token, CONF['broker_server']['token'])
        return "无效的访问", 400

    if action == 'chart':
        query_url = f"/api?token={token}&broker={broker_name}"
        return render_template('chart.html', query_url=query_url, token=token)

    if action:
        query_url = f"/api?action={action}&token={token}&broker={broker_name}"
        return render_template('table.html', query_url=query_url, token=token)

    return render_template('index.html', token=token)

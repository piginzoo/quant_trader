#!/usr/bin/python
# -*- coding: UTF-8 -*-
import datetime
import json
import logging
import os.path
from json import JSONDecodeError

import pandas as pd
from flask import Blueprint, jsonify, request

from quant_trader.server import broker
from quant_trader.server.const import *
from quant_trader.server.etf import trades
from quant_trader.utils import CONF, utils

logger = logging.getLogger(__name__)

app = Blueprint('api', __name__, url_prefix="/")
qmt_broker = broker.get("qmt")


def request2json(request):
    try:
        json_data = request.get_data()

        if request.headers.get('content-type') == 'application/json' and len(json_data) > 0:
            logger.debug("接收到Json数据，长度：%d", len(json_data))
            data = json_data.decode('utf-8')
            data = data.replace('\r\n', '')
            data = data.replace('\n', '')
            if data.strip() == "": return {}
            data = json.loads(data)
            return data
        if len(request.form) > 0:
            logger.debug("接收到表单Form数据，长度：%d", len(request.form))
            return request.form
        return None
    except JSONDecodeError as e:
        logger.exception("JSon数据格式错误")
        raise Exception("JSon数据格式错误:" + str(e))


@app.route('api', methods=["GET", "POST"])
def api():
    try:
        token = request.args.get('token', None)
        # 加一个安全限制
        if token is None or token != CONF['broker_server']['token']:
            logger.error("客户端的toke[%r]!=配置的[%s]，无效的访问", token, CONF['broker_server']['token'])
            return "无效的访问1", 400

        params = request2json(request)

        # 取得action
        action = request.args.get('action', None)
        if action is None:
            action = params.get('action', None)  # 如果get里面没有，去post的json的'action'中获得
        if action is None:
            logger.warning("请求不合法:未包含action，不知道你要干啥？")
            return jsonify({'code': -1, 'msg': f'action is not set, invalid call'}), 200

        broker_name = request.args.get('broker', None)
        logger.debug("获得请求的Action：%s,Broker: %r", action, broker_name)

        if action == QERUY_QMT:
            accounts = utils.unserialize("data/accounts.json")
            # 加工一下accounts
            accounts[0]['盈亏比'] = str(round(100 * accounts[0]['总盈亏'] / accounts[0]['总市值'], 2)) + "%"
            accounts[0]['总盈亏'] = round(accounts[0]['总盈亏'], 2)
            accounts[0]['总市值'] = round(accounts[0]['总市值'], 2)

            positions = utils.unserialize("data/positions.json")
            deals = utils.unserialize("data/deals.json")
            return jsonify(
                {'code': 0,
                 'msg': 'ok',
                 'title': 'QMT信息',
                 'data': [
                     {'title': '账户信息', 'type': 'table', 'data': accounts if accounts else {}},
                     {'title': '持仓信息', 'type': 'table', 'data': positions if positions else []},
                     {'title': '今日成交', 'type': 'table', 'data': deals if deals else []}
                 ]
                 }), 200
            # [{'测试1':11,'测试2':12},{'测试1':21,'测试2':22}]}]

        if action == QERUY_SERVER:
            """
            把服务器上的信息返回给刻度爱你
            """
            data = []
            logger.info("处理请求[%s]", action)
            if os.path.exists("data/last_grid_position.json"):
                data.append({
                    'title': 'ETF定投网格位置',
                    'type': 'dict',
                    'data': utils.unserialize("data/last_grid_position.json")}
                )
                logger.debug("返回data/last_grid_position.json")
            if os.path.exists("data/transaction.csv"):
                data.append({
                    'title': '交易记录',
                    'type': 'table',
                    'data': utils.dataframe_to_dict_list(pd.read_csv("data/transaction.csv", encoding='gb2312'))}
                )
                logger.debug("返回data/transaction.csv")
            return jsonify(
                {'code': 0,
                 'msg': 'ok',
                 'title': 'QMT信息',
                 'data': data
                 }), 200
            # [{'测试1':11,'测试2':12},{'测试1':21,'测试2':22}]}]

        # heartbeat ，2023.2.8
        """
        做一个心跳，逻辑是，每次发送心跳过来，
        如果没有心跳时间超过配置时间（半小时），就要报警了，
        这个用于监控家里的机器是不是好的。
        但是，不是所有的都会检测，所以需要一个配置表
        """
        if action == HEARTBEAT:
            # 先更新一下心跳
            qmt_broker.heartbeat(params['name'])
            qmt_broker.set_status(params['name'], 'online')
            logger.debug("接收到心跳包：%s", params['name'])

            # 这个是接受来自qmt的心跳数据
            if params['name'] == 'qmt':
                """
                {'action': 'heartbeat',
                 'name': 'qmt',
                 'info': [
                     {'name':'accounts', 'data':get_accounts()},
                     {'name':'positions', 'data':get_positions()},
                     {'name':'deals', 'data':get_deals()}
                ]}                
                """
                for i in params['info']:

                    if not os.path.exists("data"):
                        os.mkdir("data")

                    # 这个是为了查询当日的
                    file_name = f"data/{i['name']}.json"
                    utils.serialize(i['data'], file_name)

                    # 这个是为了保存历史用的
                    today = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d")
                    file_name = f"data/{i['name']}.{today}.json"
                    utils.serialize(i['data'], file_name)
                    logger.debug("数据保存到：%s", file_name)

                return jsonify({'code': 0, 'msg': 'ok'}), 200

            # 这个是接受来server的心跳数据
            if params['name'] == 'server':
                files = request.files
                logger.debug("接受服务器的心跳包，包含%d个文件附件", len(files))
                for name, file in files.items():
                    file_name = f"data/{name}"
                    if not os.path.exists("data"):
                        os.mkdir("data")
                    file.save(file_name)
                    logger.debug("数据保存到：%s", file_name)

                return jsonify({'code': 0, 'msg': 'ok'}), 200

        """
        查询用，用于返回给index.hml网页上信息信息
        """
        if action == HEARTBEAT_QUERY:
            name = request.args.get('name')
            lastime = qmt_broker.last_active_datetime.get(name, None)
            status = qmt_broker.server_status.get(name, None)
            s_lastime = 'N/A'
            s_status = 'N/A'
            if lastime: s_lastime = datetime.datetime.strftime(lastime, "%Y-%m-%d %H:%M:%S")
            if status: s_status = status
            logger.debug("查询[%s]心跳结果：最后更新时间：%s，状态：%r", name, s_lastime, status)
            return jsonify({'code': 0, 'name': name, 'lastime': s_lastime, 'status': s_status}), 200

        if action == MARKET_VALUE:
            df = trades.market_values(CONF['etf']['dir'])
            return jsonify(
                {'code': 0, 'name': 'market value', 'data': utils.dataframe_to_dict_list(df)}), 200

        logger.error("无效的访问参数：%r", request.args.get)
        return jsonify({'code': -1, 'msg': f'Invalid request:{request.args}'}), 200

    except Exception as e:
        logger.exception("处理过程中出现问题：%r", e)
        return jsonify({'code': -1, 'msg': f'Exception happened: {str(e)}'}), 200

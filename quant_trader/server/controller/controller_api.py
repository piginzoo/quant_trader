#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
import logging
from json import JSONDecodeError

from flask import Blueprint, jsonify, request

from quant_trader.notification import INFO, notifier
from quant_trader.utils import CONF
from quant_trader.server import broker
from quant_trader.server.const import *
from quant_trader.server.db import sqlite

logger = logging.getLogger(__name__)

app = Blueprint('api', __name__, url_prefix="/")


def request2json(request):
    logger.debug("Got json data:%d bytes", len(request))
    try:
        data = request.decode('utf-8')
        data = data.replace('\r\n', '')
        data = data.replace('\n', '')
        if data.strip() == "": return {}
        data = json.loads(data)
        return data
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

        params = request2json(request.get_data())

        # 取得action
        action = request.args.get('action', None)
        if action is None:
            action = params.get('action', None)  # 如果get里面没有，去post的json的'action'中获得

        if action is None:
            logger.warning("请求不合法:未包含action，不知道你要干啥？")
            return jsonify({'code': -1, 'msg': f'action is not set, invalid call'}), 200

        broker_name = request.args.get('broker', None)
        logger.debug("获得请求的Action：%s,Broker: %r", action, broker_name)

        # 查询未完成任务
        if action == "task":
            return jsonify(
                {'code': 0, 'title': '未完成交易', 'msg': 'ok',
                 'data': [t.to_dict() for t in sqlite.query_task(broker_name)]}), 200
        # 查询交易日志
        if action == "log":
            return jsonify(
                {'code': 0, 'title': '交易日志', 'msg': 'ok',
                 'data': [t.to_dict() for t in sqlite.query_logbroker_name()]}), 200
        # 查询逻辑仓位
        if action == TRADE_POSITION:
            return jsonify(
                {'code': 0, 'title': '记录仓位', 'msg': 'ok',
                 'data': [t.to_dict() for t in sqlite.query_position(broker_name)]}), 200

        # 删除僵尸任务（就是怎么执行都执行不了，用于错误恢复）
        if action == "del_task":
            id = request.args.get('id')
            sqlite.task_archieve(id, TRADE_STATUS_DELETE, '删除归档任务')
            return jsonify({'code': 0, 'msg': 'ok'}), 200

        # 手工完成任务（用于完成僵尸任务，就是怎么完成也完成不了，用于恢复错误）TODO: 价格呢？应该去同花顺的持仓中[成本价]尝试读一下，未来改进吧
        if action == "complete_task":
            id = request.args.get('id')
            task = sqlite.query_task(id=id)
            sqlite.task_done(task, message='手工完成任务')
            return jsonify({'code': 0, 'msg': 'ok'}), 200

        # 提交买卖请求，保存到数据库，等着调度器调度
        if action == TRADE_BUY or action == TRADE_SELL:
            code = params['code']
            share = params['share']
            signal_date = params['signal_date']

            # 卖的时候，price和策略都未定义
            price = params.get('price', -1)  # 卖出没有价格字段，赋值为-1
            strategy = params.get('strategy', '')  # 卖出没有策略字段，赋值为''
            broker_name = params.get('broker_name', '')  # 卖出没有券商字段，赋值为''

            if len(sqlite.query_task(code)) > 0:
                logger.warning("股票[%s]的买卖请求[%s]已经存在", code, action)
                return jsonify(
                    {'code': -1, 'msg': f'{code}\'s {action} save action fail, for it already existed in db'}), 200

            # 买入/卖出信号通知
            msg = "股票[%s]的[%s]信号：股数[%d]，信号日期[%s]" % (code, action, share, signal_date)
            logger.info(msg)
            notifier.notify(msg, INFO)

            # 将买卖任务，插入到任务表中
            sqlite.task(code, action, price, share, signal_date, strategy, broker_name)
            return jsonify({'code': 0, 'msg': f'{action} data save to server'}), 200

        # 立刻买入，主要用于测试用
        if action == TRADE_BUY_NOW:
            code = params['code']
            share = params['share']

            # 创建交易代理
            __broker = broker.get("easytrader")
            entrust_no = __broker.buy(code, share)

            msg = "买股票[%s]请求，股数[%d]" % (code, share)
            logger.info(msg)
            notifier.notify(msg, INFO)

            return jsonify({'code': 0, 'msg': f'buy stock[{code}] , amount:{share}, entrust_no:{entrust_no} '}), 200

        # 立刻卖出，用于测试
        if action == TRADE_SELL_NOW:
            code = params['code']
            share = params('share', None)
            if share is None: share = 100
            __broker = broker.get("easytrader")
            entrust_no = __broker.sell(code, share)

            msg = "卖股票[%s]请求，股数[%d]" % (code, share)
            logger.info(msg)
            notifier.notify(msg, INFO)

            return jsonify({'code': 0, 'msg': f'sell stock[{code}] , amount:{share},  entrust_no:{entrust_no}  '}), 200

        # 立刻撤单，主要用于测试用
        if action == TRADE_CANCEL:
            entrust_no = request.args.get('entrust_no')

            __broker = broker.get("easytrader")
            __broker.connect(broker_name)
            msg = __broker.cancel(entrust_no)
            logger.info("撤单返回结果：%s", msg)
            return jsonify({'code': 0, 'msg': f'cancel entrust_no[{entrust_no}] finished， message:{msg}'}), 200

        # 查询真实仓位
        if action == TRADE_TRUE_POSITION:
            __broker = broker.get("easytrader")
            __broker.connect(broker_name)
            return jsonify({'code': 0, 'title': '真实仓位', 'msg': 'ok', 'data': __broker.position()}), 200

        # 查询头寸
        if action == TRADE_BALANCE:
            __broker = broker.get("easytrader")
            __broker.connect(broker_name)
            return jsonify({'code': 0, 'title': '真实头寸', 'msg': 'ok', 'data': __broker.balance()}), 200

        # 查询当日委托
        if action == TRADE_TODAY_ENTRUSTS:
            __broker = broker.get("easytrader")
            __broker.connect(broker_name)
            return jsonify({'code': 0, 'title': '当日委托', 'msg': 'ok', 'data': __broker.today_entrusts()}), 200

        # 查询当日成交
        if action == TRADE_TODAY_TRADES:
            __broker = broker.get("easytrader")
            __broker.connect(broker_name)
            return jsonify({'code': 0, 'title': '当日成交', 'msg': 'ok', 'data': __broker.today_trades()}), 200

        # heartbeat ，2023.2.8
        """
        做一个心跳，逻辑是，每次发送心跳过来，
        如果没有心跳时间超过配置时间（半小时），就要报警了，
        这个用于监控家里的机器是不是好的。
        但是，不是所有的都会检测，所以需要一个配置表
        """
        if action == HEARTBEAT:
            __broker = broker.get("qmt")
            __broker.heartbeat(params['name'])
            logger.debug("接收到心跳包：%s",params['name'])
            return jsonify({'code': 0,'msg': 'ok'}),200

        logger.error("无效的访问参数：%r", request.args.get)
        return jsonify({'code': -1, 'msg': f'Invalid request:{request.args}'}), 200

    except Exception as e:
        logger.exception("处理过程中出现问题：%r", e)
        return jsonify({'code': -1, 'msg': f'Exception happened: {str(e)}'}), 200

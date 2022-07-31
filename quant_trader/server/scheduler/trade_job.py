import logging
import os
import time

from quant_trader.server.const import TRADE_BUY, TRADE_SELL, TRADE_BALANCE
from quant_trader.server.db.sqlite import query_task
from quant_trader.server.scheduler.trade_buy_action import TradeBuyAction
from quant_trader.server.scheduler.trade_sell_action import TradeSellAction
from quant_trader.utils import utils

logger = logging.getLogger(__name__)


class TradeJob():

    def __init__(self):
        self.buy_action = TradeBuyAction()
        self.sell_action = TradeSellAction()

    def __call__(self, broker):

        # 不在交易日和交易时间，就返回
        try:
            if not utils.is_trade_day(): return
        except:  # 防止tushare调用异常
            pass
        if not utils.is_trade_time(): return

        logger.info("任务进程：%d", os.getpid())
        try:
            tasks = query_task()
            logger.info("检索出%d条买卖任务", len(tasks))
        except:
            logger.exception('检索任务失败')
            return

        # 要对任务排序，先执行卖的任务

        for task in tasks:

            try:
                start_time = time.time()
                logger.info("执行任务开始：%r，进程：%d", task, os.getpid())

                if task.trade_type == TRADE_BUY:
                    self.buy_action.do_action(task, broker)

                # 如果是卖的话，要尽快卖出去，所以要多尝试几次
                if task.trade_type == TRADE_SELL:
                    self.sell_action.do_action(task, broker)

                if task.trade_type == TRADE_BALANCE:
                    result = broker.balance()
                    logger.debug("测试用，返回资金情况：%r", result)

                logger.debug("执行任务结束：%r，耗时：%d 秒", task, time.time() - start_time)
            except:
                logger.exception('Broker客户端执行任务[%r]失败', task)

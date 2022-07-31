import logging
import time

from quant_trader.notification import INFO, WARN, ERROR
from quant_trader.utils import CONF
from quant_trader.server.const import TRADE_STATUS_FAIL
from quant_trader.server.db import sqlite
from quant_trader.server.scheduler.trade_action import TradeAction

logger = logging.getLogger(__name__)


class TradeBuyAction(TradeAction):
    """
    买和卖不一样，买不成，我就不买了，避免追涨
    之前考虑过超过5%+就不买了，由于Easytrader没有查询即时价格的接口，做不到了
    买单有个坑：
        如果我挂买单没成交，我去撤单有没撤掉，我调度器下次再买，重复买，可能会导致超买（卖不会超卖，有仓位自动控制），
        所以保险起见，我就挂一个买单，不成交，我就死等，等到调度到最大尝试次数，然后就彻底不买了（删除任务）
    """

    def do_action(self, task, broker):
        """
        买的话，就买一次，买不进来，就算了，等待下次尝试，
        （不像卖，要反复尝试多次，尽快买入去）
        """
        # 预检查，如果股票在仓位里，不让买了
        if not self.precheck(task, broker): return

        # 1.委托单号非空，说明是之前挂过买单了，可能未确认、可能是一直没成功
        if task.entrust_no != '':
            # 没撤掉的买单，再调度器重试的间歇期，居然买出去了，成交啦
            time.sleep(1)
            record = broker.find_stock_in_today_trade_by_entrust_no(task.entrust_no, retry_num=1)  # 只查一次
            if record is not None:
                price = record['成交均价']
                self.notify("股票[%s]的买入成功，委托单号[%s]（第%d次重试后）买入价格[%.2f]：%r" %
                            (task.code, task.entrust_no, task.retry, price, task),
                            INFO)
                # 1.1 成功后，将数据库更新
                sqlite.task_done(task, price)
                return True

            max_retry = CONF['scheduler']['client']['buy_retry']
            interval = CONF['scheduler']['client']['interval']
            # 1.2 更新一下retry+1
            if task.retry < max_retry:
                sqlite.update_task_entrust_no_retry_lastime(task.code, task.entrust_no)
                self.notify("股票[%s]的买单不成功，委托单合同编号[%s]，时间[%s]，%d分钟后尝试第%d次"
                            % (task.code, task.entrust_no, task.last_datetime, interval, task.retry), WARN)
                return False
            # 1.3 到达最大重试次数，需要撤掉买单了
            else:
                # 撤买单
                time.sleep(1)
                broker.cancel(task.entrust_no)

                # 如果不能确认撤单成功，就返回，等待下次调度重试
                time.sleep(1)
                if not broker.confirm_cancel(task.entrust_no): return False

                # 撤单成功，彻底从任务表中删除任务 ！！！
                sqlite.task_archieve(task.id, TRADE_STATUS_FAIL, '交易失败，任务被删除')
                msg = "已经超过最大重试次数[%d]，撤销了股票[%s]的买委托单[%s]，并删除了任务：%r" % \
                      (max_retry, task.code, task.entrust_no, task)
                self.notify(msg, WARN)
                return False

        # 2022.7.5 大量出现，已经挂了买单，但是由于没有获得合同单号，导致的认为没有买的情况，会导致重复买
        # 整理增加一个检查，如果发现当天已经有这只股票的买单，就认为，这个买成功了，并且获得单号，填入entrust_no字段，
        # 并将此任务移动到日志表
        time.sleep(1)
        today_trade = broker.find_stock_in_today_trade_by_code(task.code, 'buy')
        if today_trade is not None:
            task.entrust_no = today_trade['合同编号']
            task.share = today_trade['成交数量']
            msg = "股票[%s]的买交易成功，委托单号[%s]（查询当日成交，补齐合同单号），细节：%r" % (task.code, task.entrust_no, task)
            self.notify(msg, INFO)
            # 成功后，将数据库更新
            sqlite.task_done(task, today_trade['成交均价'])
            return True

        # 同上，做一次当日委托的检查，如果发现了，就回填entrust_no
        time.sleep(1)
        today_trade = broker.find_stock_in_today_entrust_by_code(task.code, 'buy')
        if today_trade is not None:
            task.entrust_no = today_trade['合同编号']
            task.share = today_trade['成交数量']
            sqlite.update_task_entrust_no_retry_lastime(task.code, task.entrust_no)
            msg = "在'当日委托'找到股票[%s]的合同编号[%s]，回填任务并重试" % (task.code, task.entrust_no)
            self.notify(msg, WARN)
            return False

        time.sleep(1)
        # !!! 真正买入（挂买单），这里做个强假设，一定可以获得entrust_no合同单号，如果获得不了，就认为出现了软件异常，要人工排查
        entrust_no = broker.buy(task.code, task.share)  # {'entrust_no': 'xxxxxxxx'}
        if entrust_no is None:
            self.notify("严重问题：EasyTrader交易后，无法获得entrust合同单号，股票[%s]卖交易失败:%r" % (task.code, task.code, task), ERROR)
            return False

        # 如果未成交，确认了委托单号（在'当日成交'中），说明买入成功了
        time.sleep(1)
        record = broker.confirm(entrust_no)
        if record is not None:
            self.notify("股票[%s]的买交易成功，委托单号[%s]，细节：%r" %
                        (task.code, entrust_no, task), INFO)
            # 成功后，将数据库更新
            sqlite.task_done(task, record['成交均价'])
            return True

        # 虽然没确认成功，但是，也更新委托单号，和，最后更新时间，记录它的目的是为了防止撤单撤不掉，好再次尝试的时候
        sqlite.update_task_entrust_no_retry_lastime(task.code, entrust_no=entrust_no)

        """
        这里和卖不同，卖的话，会撤掉当前的卖点，再次尝试卖出，
        而买不会撤单，而是等待买单成交，超过最大等待次数，就不买了
        """
        return False

    def precheck(self, task, broker):
        """
        看看是否在仓位内，如果在仓位内，就不允许再买了（目前我是这样，不再补仓）
        :param task:
        :param broker:
        :return:
        """
        record = broker.find_stock_in_postion(task.code)

        # 先查看仓位：买的话应该不在仓位内，卖的话应该在仓位内
        if record is not None:
            msg = "股票[%s]已经在仓位中，无法再次购买" % task.code
            self.notify(msg, WARN)
            return False
        return True

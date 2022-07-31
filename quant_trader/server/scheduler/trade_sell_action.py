import logging
import time

from quant_trader.notification import INFO, WARN, ERROR
from quant_trader.utils import CONF
from quant_trader.server.db import sqlite
from quant_trader.server.scheduler.trade_action import TradeAction

logger = logging.getLogger(__name__)

INTERVAL_IN_ONCE = 10  # 一次调度中，重试的间隔


class TradeSellAction(TradeAction):
    """
    卖出动作，反复尝试几次[sell_retry_once]，失败的话，等待下一次调度，再试
    """

    def do_action(self, task, broker):
        """
        卖的话，要反复尝试，调用sell()是一次卖，如果不成，就要撤单，再试
        """
        # 预检查，如果股票不在仓位里，还卖个屁啊
        if not self.precheck(task, broker): return

        # 准备参数：一次调度，尝试卖出几次
        retry_times_once = CONF['scheduler']['client']['sell_retry_once']
        # 准备参数：调度器间隔，这里不用，只是为了报警提示用
        interval = CONF['scheduler']['client']['interval']

        # 一次调度过程中，尝试多次
        for i in range(retry_times_once):
            # 如果卖成功，立刻就返回了
            logger.debug("第%d次尝试卖出股票[%s]", i + 1, task.code)
            if self.sell_once(task, broker): return
            logger.warning("卖出股票[%s]的第%d次尝试失败，[%s]秒后再试...", task.code, i + 1, INTERVAL_IN_ONCE)
            time.sleep(INTERVAL_IN_ONCE)

        # N次都失败了，只好通知主人了
        self.notify("卖出股票[%s]连续[%d]次失败，尝试[%d]分钟后，再尝试: %r" % \
                    (task.code, retry_times_once, interval, task), WARN)

    def precheck(self, task, broker):
        """
        看看是否在仓位内，如果不在仓位内，就不允许卖出
        :param task:
        :param broker:
        :return:
        """
        record = broker.find_stock_in_postion(task.code)

        # 先查看仓位：买的话应该不在仓位内，卖的话应该在仓位内
        if record is None:
            msg = "股票[%s]已经不在仓位中，无法卖出" % task.code
            self.notify(msg, WARN)
            return False
        return True

    def sell_once(self, task, broker):
        """
        过程清晰明了简化为：
        1、broker.sell()
        2、broker.sell_confirm()
        3、post sell:
            3.1、return if confirm()==True
            3.2、broker.cancel() if confirm()==False
                repeat 1 until > retry_times_once
        """

        try:
            # 委托单号非空，说明是之前尝试过卖出，失败了，且，这个卖单还挂着呢，这样的话，得先掉这个卖单
            if task.entrust_no is not None and task.entrust_no != '':

                logger.debug("股票[%s]卖出任务关联了委托单[%s]，检查其是否成交？", task.code, task.entrust_no)
                # 没撤掉的卖单，再调度器重试的间歇期，居然卖出去了
                record = broker.confirm(task.entrust_no)
                if record is not None:
                    self.notify("股票[%s]的卖交易成功，委托单号[%s]，细节：%r" %
                                (task.code, task.entrust_no, task),
                                INFO)
                    # 成功后，将数据库更新
                    sqlite.task_done(task, record['成交均价'])
                    return True

                # 如果没有撤单成功，就无法继续下面的卖出动作了，返回，尝试下一次
                if not self.cancel(task, broker): return False

            # 2022.7.5 大量出现，已经挂了卖单，但是由于没有获得合同单号，导致的认为没有卖的情况，会导致重复卖
            # 整理增加一个检查，如果发现当天已经有这只股票的卖单，就认为，这个卖成功了，并且获得单号，填入entrust_no字段，
            # 并将此任务移动到日志表
            today_trade = broker.find_stock_in_today_trade_by_code(task.code, 'sell')
            if today_trade is not None:
                task.entrust_no = today_trade['合同编号']
                task.share = today_trade['成交数量']
                logger.debug("找到股票[%s]的交易记录，认为就是当前股票的今日遗漏的卖单（未获得合同标号的卖单）")
                self.notify("股票[%s]的卖交易成功，委托单号[%s]（查询当日成交，补齐合同单号），细节：%r" %
                            (task.code, task.entrust_no, task), INFO)
                # 成功后，将数据库更新
                sqlite.task_done(task, today_trade['成交均价'])
                return True

            # !!! 真正卖出（挂卖单），这里做个强假设，一定可以获得entrust_no合同单号，如果获得不了，就认为出现了软件异常，要人工排查
            task.entrust_no = broker.sell(task.code, task.share)  # {'entrust_no': 'xxxxxxxx'}
            if task.entrust_no is None:
                self.notify("严重问题：EasyTrader交易后，无法获得entrust合同单号，股票[%s]卖交易失败:%r" % (task.code, task.code, task), ERROR)
                return False

            # 如果未成交，确认了委托单号（在'当日成交'中），说明卖出成功了
            record = broker.confirm(task.entrust_no)
            if record is not None:
                self.notify("股票[%s]的卖交易成功，委托单号[%s]，细节：%r" % (task.code, task.entrust_no, task), INFO)
                # 成功后，将数据库更新
                sqlite.task_done(task, record['成交均价'])
                return True

            # 虽然没确认成功，但是，也更新委托单号，和，最后更新时间，记录它的目的是为了防止撤单撤不掉，好再次尝试的时候
            sqlite.update_task_entrust_no_retry_lastime(task.code, task.entrust_no)

            """
            没有卖出去，就需要撤单了，
            TODO：如何撤单失败咋办？回答：不判断，交给后续的鲁棒处理
                 考虑：如果不成功，后续会发生：
                 1、再卖失败（股票被锁定了，所以卖不出去）
                 2、卖单在取消动作一刹那之前成交了，这个正是我们想要的，但是我们还会尝试卖，但是会失败掉
                 所以上述2种情况，都需要手工干预了，未来考虑做一个一键取消所有委托的功能，彻底清除所有的失败委托单
                 其实也可以自动化反复check哪些卖单失败，但是过于复杂，没必要，设计上还是要简单些好
            结论：所以不判断cancel失败与否了，就认为成功了
            """
            self.cancel(task, broker)
            return False
        except Exception as e:
            logger.exception("[%s]股票[%r]失败", task.trade_type, task)
            self.notify("股票[%s]交易任务[%r]执行发生异常：%s" % (task.code, task, str(e)), ERROR)
            return False

    def cancel(self, task, broker):
        broker.cancel(task.entrust_no)

        # 如果不能确认撤单成功，就返回，等待下次重试
        if not broker.confirm_cancel(task.entrust_no): return False

        # 撤单后，把任务的合同单号清空
        cancelled_entrust_no = task.entrust_no
        task.entrust_no = ''

        # 如果撤单成功，需要重置'entrust_no'，来触发新的卖单
        sqlite.update_task_entrust_no_retry_lastime(task.code, entrust_no=task.entrust_no)

        # 撤单成功
        msg = "股票[%s]卖单[%s]撤单成功，可以尝试再次卖出了：%r" % \
              (task.code, cancelled_entrust_no, task)
        self.notify(msg, WARN)

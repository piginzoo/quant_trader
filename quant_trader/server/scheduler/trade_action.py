import logging

from quant_trader.notification import notifier
from quant_trader.utils import utils

logger = logging.getLogger(__name__)
url = utils.get_url()

"""
这事一个工具类，用于查找股票是不是在服务期端的持仓、当日成交、当日委托中
"""

logger = logging.getLogger(__name__)


class TradeAction():

    def do_action(self, task, broker):
        pass

    def notify(self, msg, msg_type):
        notifier.notify(msg, msg_type)

import logging
from urllib.error import HTTPError

from strategyease_sdk import Client

from quant_trader.server.broker.broker import Broker
from quant_trader.utils import CONF

logger = logging.getLogger(__name__)


class StrategyEaseBroker(Broker):
    """
    活动易的实现
    """

    def __init__(self):
        print(CONF)
        self.client = Client(logger, **dict(CONF['broker']))

    def buy(self, code, share):
        try:
            order = self.client.buy(self.client_param, symbol=code, type='MARKET', priceType=4, amount=share)
        except HTTPError as e:
            result = e.response.json()
            logger.exception("策略易买失败：%s:%.0f股",code,share)

    def sell(self, code, share):
        pass

    def position(self):
        """
        返回：
        list<code,buy_date,share,price>
        """
        pass

    def cancel_all(self):
        """
        撤单(所有)
        """
        pass

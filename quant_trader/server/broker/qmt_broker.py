import datetime
import logging

from quant_trader.server.broker.broker import Broker
from quant_trader.server.heartbeat.monitor import beijing_time

RETRY_INTERVAL = 3

logger = logging.getLogger(__name__)


class QMTBroker(Broker):
    """
    QMT的实现
    """

    def __init__(self):
        self.last_active_datetime = {} # 最后更新时间
        self.server_status = {}  # online | offline 在线还是离线

    def heartbeat(self, name):
        now = beijing_time()
        # 更新最后更新时间
        self.last_active_datetime[name] = now
        s_lastime =  'None' if name is None else datetime.datetime.strftime(now, "%Y-%m-%d %H:%M:%S")
        logger.debug("更新了[%s]的最后活动时间为：%s",name,s_lastime)

    def set_status(self, name, status):
        self.server_status[name] = status
        logger.debug("更新了[%s]的最后状态为：%s", name, status)

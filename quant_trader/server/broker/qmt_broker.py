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
        self.last_active_datetime = {}
        self.server_status = {}  # online | offline

    def heartbeat(self, name):
        now = beijing_time()
        # 更新最后更新时间
        self.last_active_datetime[name] = now

    def set_status(self, name, status):
        self.server_status[name] = status

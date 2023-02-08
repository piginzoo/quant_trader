import logging

from quant_trader.server.heartbeat import monitor

logger = logging.getLogger(__name__)


class HeartbeatJob():

    def __init__(self):
        pass

    def __call__(self, broker):

        # 不在交易日和交易时间，就返回
        try:
            monitor.handle(broker.last_active_datetime)
        except:  # 防止tushare调用异常
            logger.exception('心跳调度异常')
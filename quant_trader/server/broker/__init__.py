from quant_trader.server.broker.easytrader_broker import EaseTraderBroker
from quant_trader.server.broker.qmt_broker import QMTBroker


def get(name):
    if name == "easytrader":
        return EaseTraderBroker()
    if name == "qmt":
        return QMTBroker()

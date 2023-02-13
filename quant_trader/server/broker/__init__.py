from quant_trader.server.broker.qmt_broker import QMTBroker


def get(name):
    if name == "qmt":
        return QMTBroker()

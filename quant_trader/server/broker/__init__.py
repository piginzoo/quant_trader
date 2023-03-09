from quant_trader.server.broker.qmt_broker import QMTBroker

qmt_broker = QMTBroker()
def get(name):
    if name == "qmt":
        return qmt_broker

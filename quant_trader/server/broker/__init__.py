from quant_trader.server.broker.easytrader_broker import EaseTraderBroker


def get(name):
    if name == "easytrader":
        return EaseTraderBroker()

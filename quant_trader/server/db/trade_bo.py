import logging

from sqlalchemy import Column, Integer, String, Float, UniqueConstraint
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from quant_trader.utils import utils, conf

Base = declarative_base()

logger = logging.getLogger(__name__)


class DBInfoMixin():

    def get_field_values(self):
        class_name = self.__class__.__name__
        f_names = dir(self)

        results = []
        for f_name in f_names:

            if f_name == "metadata": continue
            if f_name == "id": continue
            if f_name.startswith("_"): continue
            if f_name == "get_field_values": continue

            c_type = type(getattr(self, f_name))
            if c_type not in [str, dict, float, int]:
                continue
            results.append("{}={}".format(f_name, getattr(self, f_name)))

        return f"{class_name}({','.join(results)})"

    def to_dict(self):
        f_names = dir(self)

        result = {}
        for f_name in f_names:

            if f_name == "metadata": continue
            if f_name.startswith("_"): continue
            if f_name == "get_field_values": continue

            c_type = type(getattr(self, f_name))
            if c_type not in [str, dict, float, int]:
                continue
            result[f_name] = getattr(self, f_name)

        return result


class TradeTask(Base, DBInfoMixin):
    __tablename__ = 'trade_task'

    def __init__(self, code, trade_type, price, share, signal_date, strategy,broker_name):
        self.code = code
        self.trade_type = trade_type
        self.signal_date = signal_date
        self.price = price  # 这个是头天的价格
        self.share = share
        self.strategy = strategy
        self.broker_name = broker_name
        self.retry = 0
        self.last_datetime = utils.now()
        self.entrust_no = ''  # 开始的时候没有，会被更新

    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键
    code = Column(String(9))
    price = Column(Float())  # 头天的价格
    share = Column(Float())  # 股
    strategy = Column(String)  # 对应的策略名
    broker_name = Column(String)  # 券商名字：通用(mock)、银河(yinhe)、国金....
    trade_type = Column(String(9))
    signal_date = Column(String(8))  # 20220202
    entrust_no = Column(String(8))  # 委托单合同编号，需要被更新
    last_datetime = Column(String(14))  # 20220202190133
    retry = Column(Integer)

    __table_args__ = (
        UniqueConstraint('code'),
    )

    # __repr__方法用于输出该类的对象被print()时输出的字符串，如果不想写可以不写
    def __repr__(self):
        return self.get_field_values()


class TradeLog(Base, DBInfoMixin):
    """
    日志表，对任务进行日志记录：
    - 买日志
    - 卖日志
    - 失败日志
    """

    __tablename__ = 'trade_log'

    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键
    code = Column(String(9))
    trade_type = Column(String(9))
    signal_date = Column(String(8))  #
    strategy = Column(String)  # 对应的策略名
    broker_name = Column(String)  # 券商名字：通用(mock)、银河(yinhe)、国金....
    trade_datetime = Column(String(14))  # 20220202190133
    price = Column(Float())  # 价格
    share = Column(Float())  # 股
    status = Column(String)  # 状态: success, fail
    message = Column(String)

    def __init__(self, task, status, message):
        self.code = task.code
        self.trade_type = task.trade_type
        self.signal_date = task.signal_date
        self.strategy = task.strategy
        self.broker_name = task.broker_name
        self.share = task.share
        self.price = task.price
        self.broker_name = task.broker_name

        self.trade_datetime = utils.now(),
        self.status = status
        self.message = message

    # __repr__方法用于输出该类的对象被print()时输出的字符串，如果不想写可以不写
    def __repr__(self):
        return self.get_field_values()


class TradePosition(Base, DBInfoMixin):
    __tablename__ = 'trade_position'

    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键
    code = Column(String(9))
    signal_date = Column(String(8))  #
    strategy = Column(String)  # 对应的策略名,好知道这个持仓是由哪个策略买入的
    trade_datetime = Column(String(14))  # 20220202190133
    price = Column(Float())  # 价格
    share = Column(Float())  # 股
    broker_name = Column(String)  # 券商名字：通用(mock)、银河(yinhe)、国金....

    def __init__(self, code, price, share, signal_date, trade_datetime, strategy,broker_name):
        self.code = code
        self.signal_date = signal_date
        self.price = price
        self.share = share
        self.trade_datetime = trade_datetime
        self.strategy = strategy
        self.broker_name = broker_name

    __table_args__ = (
        UniqueConstraint('code'),  # 持仓只能有一只股票
    )

    # __repr__方法用于输出该类的对象被print()时输出的字符串，如果不想写可以不写
    def __repr__(self):
        return self.get_field_values()


def create_db():
    # 查看映射对应的表
    TradeTask.__table__
    TradeLog.__table__
    TradePosition.__table__
    engine = create_engine(f'sqlite:///{conf.SQLITE_DB_FILE}?check_same_thread=False', echo=True)
    Base.metadata.create_all(engine, checkfirst=True)
    logger.info("所有的表已经创建...:", Base.metadata.tables)

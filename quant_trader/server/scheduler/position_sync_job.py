import logging

from quant_trader.server.const import UNKNOWN
from quant_trader.utils import utils
from quant_trader.notification import notifier, WARN, INFO
from quant_trader.server import broker
from quant_trader.server.db import sqlite
from quant_trader.server.db.trade_bo import TradePosition

logger = logging.getLogger(__name__)


class PositionSyncJob():
    """
    同步真实持仓====>逻辑持仓
    1、如果所有信息都一致，do nothing
    2、如果真实持仓不等于逻辑仓，更新股份数或者价格
    3、如果真实持仓在逻辑持仓中没有，那需要同步下来这个持仓，买入价格时间以昨天开盘为准
    4、如果是逻辑持仓中在真实持仓中没有，那需要删除这个持仓到归档表，注释写'sync delete'
    """

    def __call__(self, broker):
        true_positions = broker.position()
        logic_positions = sqlite.query_position()
        logger.debug("获得真实持仓[%d]条，获得逻辑持仓[%d]条", len(true_positions), len(logic_positions))

        # 遍历每一个真实持仓，如果不一致，或者不在逻辑持仓，处理之
        for true_position in true_positions:

            # 如果在逻辑持仓里
            if check_logic_positions(true_position, logic_positions): continue

            # 如果这个真实持仓股票，不在逻辑持仓里，需要把逻辑持仓里放入真实持仓，
            # 另外，买入日就是今天或离今天最近的交易日（原因是我都要跑着批次的）
            position = TradePosition(code=true_position['证券代码'],
                                     price=float(true_position['成本价']),
                                     share=float(true_position['股票余额']),
                                     signal_date=utils.today(),  # 信号日，本来应该是头一天的交易日，犯懒了，暂时用今天 TODO
                                     trade_datetime=utils.now(),
                                     strategy=UNKNOWN,
                                     broker_name=broker.get_current_broker_name()) # 发现这种实盘有，逻辑盘没有的情况，你就不知道这个是从哪个策略来的了
            if sqlite.create_position(position):
                msg = f"股票[%s]持仓修正：根据真实持仓创建逻辑持仓：%r" % (true_position['证券代码'], position)
                notifier.notify(msg, INFO)

        # 遍历每一个真实持仓，如果不一致，或者不在逻辑持仓，处理之
        for logic_position in logic_positions:

            # 如果，这个逻辑持仓股票，已经在真实持仓中，忽略
            if check_true_positions(logic_position, true_positions): continue

            if sqlite.del_position(logic_position):
                msg = f"股票[%s]持仓修正：逻辑持仓[%r]不在真实持仓中，删除它" % (logic_position.code, logic_position)
                notifier.notify(msg, WARN)


def check_true_positions(logic_position, true_positions):
    for true_position in true_positions:
        # 虽然说逻辑持仓在真实持仓中，忽略
        if true_position['证券代码'] == logic_position.code[:6]: return True
    return False


def check_logic_positions(true_position, logic_positions):
    """用真实仓位===去同步===>逻辑持仓（sqlite中的）"""

    for logic_position in logic_positions:
        # 遍历每一个逻辑持仓股票

        # 虽然说逻辑持仓中，代码也要统成了6位，但是为了鲁棒，还是保留截取六位吧
        if true_position['证券代码'] != logic_position.code[:6]: continue

        correct_share = None
        correct_price = None

        # 股票代码一样
        # 检查：数量、价格、
        true_price = float(true_position['成本价'])
        true_share = float(true_position['股票余额'])
        if true_price != float(logic_position.price):
            logger.warning("股票[%s]的真实价格[%.2f]!=逻辑价格[%.2f]",
                           true_position['证券代码'],
                           true_price,
                           logic_position.price)
            correct_price = true_price

        if true_share != float(logic_position.share):
            logger.warning("股票[%s]的真实股数[%.2f]!=逻辑股数[%.2f]",
                           true_position['证券代码'],
                           true_share,
                           logic_position.share)
            correct_share = true_share

        if correct_price is None and correct_share is None:
            return True  # 找到了持仓，信息一致，但是无需更新啥

        # 把真实持仓的价格和股份数，同步到逻辑仓位中
        sqlite.update_position(logic_position.code, correct_price, correct_share)
        msg1 = msg2 = ""
        if correct_price: msg1 = f"价格[{logic_position.price}=>{true_price}]"
        if correct_price: msg2 = f"股数[{logic_position.share}=>{true_share}]"
        msg = f"股票[{logic_position.code}]持仓修正：{msg1},{msg2}"
        notifier.notify(msg, INFO)
        return True
    return False


# python -m server.scheduer.position_check_job
if __name__ == '__main__':
    utils.init_logger(file=True)
    PositionSyncJob()(broker.get("easytrader"))

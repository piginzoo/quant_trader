import logging
import math
import pandas as pd
from quant_trader.notification import notifier, WARN, INFO
from quant_trader.utils import utils, CONF, db_utils
from quant_trader.utils.utils import uncomply_code

logger = logging.getLogger(__name__)
url = utils.get_url()

"""
这个，是远端服务器的broker（交易商）的本地代理。
"""


def balance():
    data = {"action": "balance"}
    url = utils.get_url()
    result = utils.http_json_post(url, data)
    if result.get('code', None) and result['code'] != 0:
        logger.error(f"查询头寸失败: {result.get('msg', '原因不详')}")
        return None, None
    data = result['data']
    logger.debug("查询到账户总资产 [%.2f] 元,现金 [%.2f] 元", data['总资产'], data['可用金额'])
    return data['总资产'], data['可用金额']


def position():
    """
    向服务器逻辑仓位，逻辑仓位包含买入日期，
    而，真实仓位（同花顺"资金股票")没有买入日期，就无法计算最大回撤
    """
    return utils.http_json_post(url, {"action": "position"})


def true_position():
    """
    向服务器真实仓位,同花顺"资金股票"返回的真实持仓列表
    """
    return utils.http_json_post(url, {"action": "true_position"})


def today_entrusts(entrust_no):
    """
    向服务器真实仓位,同花顺"资金股票"返回的真实持仓列表
    """
    return utils.http_json_post(url, {"action": "today_entrusts", "entrust_no": entrust_no})


@uncomply_code
def get_stock_price_from_tushuare(code, signal_date):
    # 获得这只股票的当日价格(不能直接调用database，那个后复权数据，得要市价）
    # 从tushare获得？还是读easy_trader呢？还是从tushare获得靠谱点
    df = utils.tushare_api().daily(stock_code=code,
                                  start_date=signal_date,
                                  end_date=signal_date,
                                  adjust=None)
    if len(df) == 1:
        logger.warning("从tushare，获得股票[%s]目标日[%s]的收盘价：%.2f", code, signal_date, df.iloc[0]['close'])
        return df.iloc[0]['close']

    if len(df) == 0:
        df = utils.tushare_api().daily(stock_code=utils.compile_stock_code(code),
                                      start_date=utils.last_week(signal_date),
                                      end_date=signal_date,
                                      adjust=None)
        assert len(df) > 0
        df = df.sort_values(by='datetime')
        s = df.iloc[-1]
        logger.warning("从tushare，无法股票[%s]获得目标[%s]的收盘价，只好获得最近[%s]的收盘价：%.2f",
                       code, signal_date, s['datetime'], s['close'])
        return s['close']


@uncomply_code
def __buy(code, action, signal_date, strategy):
    """
    仅仅需要股票代码，买多少是自动计算出来：当日的价格+仓位控制
    :param code:
    :param action:
    :return:
    """

    market_value, current_cash = balance()
    if market_value is None:
        logger.error("无法获得服务器端的总资产和可用金额，推送终止")
        return None

    # 询问服务器，是否再逻辑和真实仓位中，如果是，不再推送了
    if is_in_position(code):
        logger.error("股票[%s]已经在仓位中，无法购买", code)
        return None

    # 不能超过配置中的资金上限
    total_value = min(CONF['strategy']['max_value'], market_value)
    logger.info("总体仓位控制限制的总体资金（持仓+现金）配置上限为：%.2f", total_value)

    ideal_cash = CONF['strategy']['max_value'] / CONF['strategy']['position']
    cash = min(ideal_cash, current_cash)
    logger.info("这只股票配置（根据仓位控制）现金为：%.2f", cash)

    price = get_stock_price_from_tushuare(code, signal_date)
    logger.info("股票[%s]目标价格为：%.2f", code, price)

    # 按照一个保守价格来买入，且是100的整数倍
    _size = math.ceil(cash / price)
    size = _size // 100 * 100
    if size == 0:
        notifier.notify(f"没有足够现金购买股票[{code}]了，可购买股数{_size}股", WARN)
        return None

    logger.debug("股票[%s]购买股数%.0f股，规整到整手：%.0f股", code, _size, size)

    buy_data = {"action": action,
                "code": code,
                "price": price,
                "share": size,
                "signal_date": signal_date,
                "strategy": strategy}
    result = utils.http_json_post(url, buy_data)
    logger.debug("股票[%s]的[%s]动作提交到服务器返回：code:%d,msg:%s", code, action, result['code'], result['msg'])
    return result


@uncomply_code
def buy_now(code):
    """
    立即购买，不会放到服务器的数据库中等待调度
    :param code:
    :return:
    """

    result = __buy(code, action='buy_now', signal_date=utils.today())
    if result is None:
        logger.error("股票[%s]买单失败", code)
        return False
    if result['code'] != 0:
        logger.error("股票[%s]买单失败，原因：%s", code, result['msg'])
        return False

    __check_trade_succeed(code, result)


@uncomply_code
def __check_trade_succeed(code, result):
    msg = result['msg']
    # {'code': 0, 'msg': 'buy stock[300300] , amount:100, entrust_no:2889563043 '}
    # 解析其中的entrust_no
    if "entrust_no" not in msg:
        logger.error("买单交易返回结果不包含委托单号entrust_no：%r", result)
        return False

    logger.debug("-" * 80)

    entrust_no = msg[msg.find("entrust_no") + 11:].strip()
    logger.debug("委托合同编号：%s", entrust_no)

    # 2022.7.31 确实应该去查一下，但是懒得改了，buy_now/sell_now不用了
    # if find_stock_in_today_trades(entrust_no):
    #     logger.debug("股票[%s]+交合同单号[%s]，在'当日成交'中找到，交易成功", code, entrust_no)
    #     return True
    # else:
    #     logger.debug("股票[%s]+交合同单号[%s]，无法在'当日成交'中被找到，需要撤掉刚才的订单", code, entrust_no)
    #     buy_data = {"action": "cancel", "entrust_no": entrust_no}
    #     result = utils.http_json_post(url, buy_data)
    #     logger.debug("股票[%s]+交合同单号[%s]，撤单返回结果:%r", code, entrust_no, result)
    #     return False


@uncomply_code
def buy(code, signal_date, strategy):
    """
    不会立即购买，把请求发送到服务器的数据库中等待调度
    :param code:
    :return:
    """
    result = __buy(code, action='buy', signal_date=signal_date, strategy=strategy)
    if result and result['code'] == 0:
        logger.info("股票[%s]买入请求已经提交到服务器", code)
        return True
    else:
        logger.error("股票[%s]买入请求提交到服务器失败", code)
        return False


@uncomply_code
def sell_now(code):
    """
    直接调用服务器的软件，卖掉
    :param code:
    :return:
    """
    if not is_in_position(code):
        logger.error("无法在服务器找到持仓股票[%s]，卖出终止", code)
        return False

    data = {"action": 'sell_now', "code": code}
    result = utils.http_json_post(url, data)
    logger.debug("股票[%s]的卖出动作提交到服务器返回：code:%d,msg:%s", code, result['code'], result['msg'])
    if result.get('code', None) and result['code'] != 0:
        logger.error("股票[%s]卖单失败，原因：%s", code, result['msg'])
        return False

    __check_trade_succeed(code, result)


@uncomply_code
def sell(code, share):
    """
    只发卖出指令，服务器会放到数据库中，等待调度卖掉
    """
    share = int(share)  # 强转整型
    if not is_in_position(code):
        logger.error("股票[%s]已经不在仓位中，无法卖出", code)
        return False

    buy_data = {"action": "sell", "code": code, "share": share, "signal_date": utils.today()}
    result = utils.http_json_post(url, buy_data)
    logger.debug("股票[%s]的卖出动作提交到服务器，返回：code:%d,msg:%s", code, result['code'], result['msg'])
    if result and result['code'] == 0:
        logger.info("股票卖出请求，正确提交到服务器了")
        return True
    else:
        logger.error("股票卖出请求，提交到服务器过程中出现错误:%s", result['msg'])
        return False


@uncomply_code
def is_in_position(code):
    """
    检查是否持仓
    :return:
    """
    result = position()
    if result['code'] == 0:
        data = result['data']
        for row in data:
            if row['code'] in code:
                logger.debug("股票[%s]在逻辑持仓中", code)
                return True
    result = true_position()
    if result['code'] == 0:
        data = result['data']
        for row in data:
            if row['证券代码'] in code:  # 用in，原因是证券代码是600001，而不是600001.SH
                logger.debug("股票[%s]在真实持仓中", code)
                return True
    return False
import logging
import os.path
import time
import easytrader

from quant_trader.server.const import UNKNOWN
from quant_trader.utils import CONF, utils
from quant_trader.server.broker.broker import Broker

RETRY_INTERVAL = 3

logger = logging.getLogger(__name__)


class EaseTraderBroker(Broker):
    """
    活动易的实现，未使用，有问题 
    """

    def connect(self, current_broker_name):
        """
        重新连接到exe的进程上，如果此时已经登录了，就只会把它放置到前台；如果未登录，会先登录，然后放置到前台
        :return:
        """
        logger.info("切换至券商：%s", current_broker_name)
        if CONF['brokers'].get(current_broker_name, None) is None:
            msg = "股票执行任务提供的券商[%s]在配置文件中不存在，请检查配置，或者券商名" % current_broker_name
            logger.error(msg)
            raise ValueError(msg)

        uid = CONF['brokers'][current_broker_name]['uid']
        pwd = CONF['brokers'][current_broker_name]['pwd']
        exe_path = CONF['brokers'][current_broker_name]['exe_path']
        client_type = CONF['brokers'][current_broker_name]['client_type']
        # logger.info("券商使用的账户：uid=%s, pwd=%s, client_type=%s, exe_path=%s", uid, pwd[:2] + "****", client_type, exe_path)

        self.client = easytrader.use(client_type)

        # 登录客户端，输入用户名和密码
        self.client.prepare(user=uid, password=pwd, exe_path=exe_path)

        self.client.enable_type_keys_for_editor()
        logger.info("登录了%s的%s类型客户端", current_broker_name, client_type)

        # 保存一下当前的券商名，为了是，可以查询到当前的券商是谁
        self.save_current_broker_name(current_broker_name)

    def save_current_broker_name(self, current_broker_name):
        if not os.path.exists("./data"):
            os.mkdir("./data")
        with open("./data/broker.name","w") as f:
            f.write(current_broker_name)

    def get_current_broker_name(self):
        if not os.path.exists("./data/broker.name"): return UNKNOWN
        with open("./data/broker.name") as f:
            broker_name = f.read()
            return broker_name

    def __format_code(self, code):
        """
        如果是 600001.SH => 600001
        :param code:
        :return:
        """
        if "." in code:
            return code[:code.find(".")]
        return code

    def buy(self, code, share):
        """
        执行买动作，买其实是挂买单，还要等待确认
        :param code:
        :param share:
        :return:
        """

        self.connect()
        code = self.__format_code(code)
        result = self.client.market_buy(code, share)
        # 一定不要勾选掉买完后的对话框，里面包含着委托单号，这个非常重要，用于撤单和查询
        # 如果勾选掉，就重装一遍软件
        # 成交回报{'entrust_no': 'xxxxxxxx'}

        if type(result) == dict and 'entrust_no' in result.keys():
            logger.info("已经买入股票[%s] %d 份，委托单号：%r", code, share, result['entrust_no'])
            return result['entrust_no']
        else:
            # 这个可能不是错误，但是我们必须要单号，如果没有，计算购买失败，方便排错
            msg = "买入股票[%s] %d 份，失败：无法获得entrust_no委托单号，交易结果：%r" % (code, share, result)
            raise ValueError(msg)

    def sell(self, code, share):
        self.connect()
        code = self.__format_code(code)
        result = self.client.market_sell(code, share)
        if type(result) == dict and 'entrust_no' in result.keys():
            logger.info("已经卖出股票[%s] %d 份，委托单号：%r", code, share, result['entrust_no'])
            return result['entrust_no']
        else:
            # 这个可能不是错误，但是我们必须要单号，如果没有，计算购买失败，方便排错
            msg = "卖出股票[%s] %d 份，失败：无法获得entrust_no委托单号，交易结果：%r" % (code, share.result)
            raise ValueError(msg)

    def position(self):
        postion = self.client.position
        # logger.debug("仓位：\n%r", [f"{p['证券代码']}/{p['证券名称']}:{p['股票余额']}\n" for p in postion])
        return postion

    def balance(self):
        balance = self.client.balance
        logger.info("头寸：%r", balance)
        return balance

    def today_entrusts(self):
        entrusts = self.client.today_entrusts
        logger.debug("委托：\n%r", [f"{p['证券代码']}/{p['证券名称']}/{p['操作']}:{p['委托数量']},  " for p in entrusts])
        return entrusts

    def today_trades(self):
        trades = self.client.today_trades
        logger.debug("委托：\n%r", [f"{p['证券代码']}/{p['证券名称']}/{p['操作']}:{p['成交数量']},  " for p in trades])
        return trades

    def balance(self):
        balance = self.client.balance

        # 银河证券会返回一个数组，她的balance不在是用静态标签表示了，而是用grid，但是只有一行
        if type(balance)==list:
            logger.debug("返回的balance头寸数据为数组：%d 行",len(balance))
            if len(balance)>0:
                balance = balance[0]

        logger.info("头寸：%r", balance)
        return balance

    def cancel(self, entrust_no):
        """
        撤单：entrust_no，委托单号
        """
        msg = self.client.cancel_entrust(entrust_no)  # 返回：{'message': '撤单申报成功'}
        return msg['message']

    def confirm(self, entrust_no):
        """
        确认是否 委托单 成功
        按理说应该返回True|False，但是为了读取返回的确认价格，返回交易成功对象
        """

        # 卖完，不断去'当日成交'里面查，查15秒后，如果查到说明卖出成功
        record = self.find_stock_in_today_trade_by_entrust_no(entrust_no, retry_num=3)
        # 如果查到了"当日成交"中，有这条单据，那么就更新数据库
        if record is not None:
            return record
        return None

    def confirm_cancel(self, entrust_no):
        """
        确认是否 撤单 成功
        """
        # 去查看，是否撤单成功
        record = self.find_stock_in_entrust(entrust_no)
        if record is None:
            logger.warning("未在当日委托中找到委托单[%s]，等待调度重试")
            return False
        elif record['备注'] != "全部撤单":
            logger.warning("'当日委托'的委托单[%s]，状态为[%s]，不是'全部撤单'，等待调度重试", entrust_no, record['备注'])
            return False
        return True

    def find_stock_in_today_trade_by_code(self, code, action):
        # 买卖成功，应该在'当日成交'中，按照entrust合同单号，可以查到，表明交易成功了
        # 因为成交需要一段撮合时间，所以可能立刻查询不到，所以这里要retry 5次，合计15秒
        record = self.find_stock_in(query_func=self.today_trades,
                                    target_column='证券代码',
                                    target_value=code,
                                    retry_num=1)
        if record is None: return None
        # 再做个买卖的校验
        if action == "buy" and record['操作'] == '买入': return record
        if action == "sell" and record['操作'] == '卖出': return record
        logger.warning("在'当日成交'中找到股票，但是操作方向相反[%s : %s]，视为未找到", record['操作'], action)
        return None

    def find_stock_in_today_trade_by_entrust_no(self, entrust_no, retry_num=5):
        # 买卖成功，应该在'当日成交'中，按照entrust合同单号，可以查到，表明交易成功了
        # 因为成交需要一段撮合时间，所以可能立刻查询不到，所以这里要retry 5次，合计15秒
        return self.find_stock_in(query_func=self.today_trades,
                                  target_column='合同编号',
                                  target_value=entrust_no,
                                  retry_num=retry_num)

    def find_stock_in_postion(self, code):
        record = self.find_stock_in(query_func=self.position,
                                    target_column='证券代码',
                                    target_value=code,
                                    retry_num=1)
        if record is None: return None

        # 2022.7.29，注释掉，解决bug：已经卖出后，仓位是0，
        # 但是，卖出时候未获得entrust_no，但是会被这个未在仓位内过滤掉，不会做二次的补救尝试
        # if record['股票余额'] == 0:
        #     logger.debug("股票[%s/%s]在仓位中，但是'股票余额'为0，视为不在仓位", record['证券代码'], record['证券名称'])
        #     return None

        return record

    def find_stock_in_entrust(self, entrust_no):
        return self.find_stock_in(query_func=self.today_entrusts,
                                  target_column='合同编号',
                                  target_value=entrust_no,
                                  retry_num=3)

    def find_stock_in_today_entrust_by_code(self, code, action):
        record = self.find_stock_in(query_func=self.today_entrusts,
                                    target_column='证券代码',
                                    target_value=code,
                                    retry_num=1)
        if record is None: return None
        # 再做个买卖的校验
        if action == "buy" and record['操作'] == '买入': return record
        if action == "sell" and record['操作'] == '卖出': return record
        logger.warning("在'当日委托'中找到股票，但是操作方向相反[%s : %s]，视为未找到", record['操作'], action)
        return None

    def find_stock_in(self, query_func, target_column, target_value, retry_num, retry_interval=RETRY_INTERVAL):
        """
        一个函数，查3种信息：持仓、当日成交、当日委托
        results: [<dict>] , dict数组
        """

        def __found():
            for d in query_func():
                assert type(d) == dict
                # 如果没有这个列，返回空
                if target_column not in d.keys(): return None

                if d[target_column] != target_value: continue
                return d

            return None

        if retry_num == 1: return __found()
        for i in range(retry_num):
            __found_record = __found()
            if __found_record is not None: return __found_record
            logger.debug("等待%d秒再次尝试grid的[%s]列对应的值[%r]的记录", retry_interval, target_column, target_value)
            time.sleep(retry_interval)
        return None


# python -m quant_trader.server.broker.easytrader_broker
if __name__ == '__main__':
    utils.init_logger(simple=True)
    print("测试模拟炒股")
    broker = EaseTraderBroker()
    broker.connect('mock')
    broker.balance()
    time.sleep(2)
    broker.position()
    time.sleep(2)
    broker.today_entrusts()
    time.sleep(2)
    broker.today_trades()
    time.sleep(2)
    print("="*40)
    print("测试银河证券")
    broker.connect('yinhe')
    broker.balance()
    time.sleep(2)
    broker.position()
    time.sleep(2)
    broker.today_entrusts()
    time.sleep(2)
    broker.today_trades()

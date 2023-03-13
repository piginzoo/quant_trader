import logging
import datetime

import pytz
from chinese_calendar import is_workday
import time

from quant_trader import utils
from quant_trader.notification import ERROR, notifier
from quant_trader.utils.utils import date2str

logger = logging.getLogger(__name__)


def beijing_time(s_time=None):
    """
    返回当日的时间
    :param s_time: 时间，字符串：'21:31'
    :return:
    """
    cn_tz = pytz.timezone('Asia/Shanghai')
    if s_time:
        t = datetime.datetime.strptime(datetime.datetime.now(tz=cn_tz).strftime("%Y%m%d") + s_time, "%Y%m%d%H:%M")
        # 报错：TypeError: can't compare offset-naive and offset-aware datetimes
        # 原因是，这个t，是offset-naive，是不带时区的，所以要给他加上时区
        return t.replace(tzinfo=cn_tz)
    else:
        return datetime.datetime.now(tz=cn_tz)


# 得到当前日期是否为股票交易日
def is_trade_day(date):
    if is_workday(date):
        if date.isoweekday() < 6:
            return True
    return False


def get_heartbeat_conf(name):
    heartbeats = utils.CONF['heartbeat']
    for h in heartbeats:
        if h['name'] == name: return h
    return None


def handle(broker):

    # 非交易日不检查
    if not is_trade_day(datetime.datetime.now()):
        logger.debug("今日不是交易日")
        return

    # 现在的时间
    now = beijing_time()
    heartbeats = utils.CONF['scheduler']['heartbeat']['services']
    """
    scheduler:
            heartbeat: # 客户端配置
                interval: 30 # 多久检查一次，1分钟
                services:
                  -
                    name: 'server' # 服务器的心跳
                    timeout: 30 # 30分钟过期
                    check_time: 9:30~15:00 # 检测时间
                  -
                    name: 'qmt' # qmt软件的心跳
                    timeout: 30 # 30分钟过期
                    check_time: 9:30~15:00 # 检测时间    
    """

    for heartbeat in heartbeats:
        name = heartbeat['name']
        # 看看缓存的上次更新时间
        lastime = broker.last_active_datetime.get(name, None)
        # 如果是第一次，记录一个起始时间
        if lastime is None:
            # 先记录一下时间戳，用于下次算
            broker.last_active_datetime[name] = now
            logger.debug("开启[%s]心跳的监控",name)
            continue

        # check_time: 9:30~11:30,13:00~15:00  => QMT
        # check_time: 9:30~15:00 => Server
        for time_scope in heartbeat['check_time'].split(","): # 多个时间段
            # 处理一个时间段内，开始~结束中，发生超时

            check_time = time_scope.split("~")  # 9:30~15:00
            # 开市的时间
            begin_time = beijing_time(check_time[0])  # 9：30
            # 闭市的时间
            end_time = beijing_time(check_time[1])  # 15：:00

            # 如果目前是在这个checktime的交易时间（qmt和server不同，为何？qmt是由QMT软件发送的，server是我自己的程序发送的）
            if now > begin_time and now < end_time:

                # 读配置中的超时时间是多少，默认是30分钟
                timeout = heartbeat['timeout']

                s_lastime = datetime.datetime.strftime(lastime, "%Y-%m-%d %H:%M:%S")

                # 如果超时了
                if abs(now - lastime) > datetime.timedelta(minutes=timeout):
                    broker.server_status[name] = 'offline'
                    msg = f'服务[{name}]在交易时段[{date2str(begin_time,"%Y-%m-%d %H:%M:%S")}~{date2str(end_time,"%Y-%m-%d %H:%M:%S")}]超时：超时时间[{now - lastime}]分钟 大于 规定时间[{timeout}]分钟，上次更新时间为：{s_lastime}'
                    notifier.notify(msg, ERROR)
                    logger.warning(msg)
                    break # break是跳出当前的for，就是不查其他的时间段了，这个类型的超时就处理完了

        logger.debug("[%s]心跳正常，最后更新时间：%s", name,s_lastime)
    return True

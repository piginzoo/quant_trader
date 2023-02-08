import logging
import os
import time

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from quant_trader.server.heartbeat.heartbeat_job import HeartbeatJob
from quant_trader.utils import utils, CONF
from quant_trader.server import broker
from quant_trader.server.scheduler.position_sync_job import PositionSyncJob
from quant_trader.server.scheduler.trade_job import TradeJob

"""
为何扼要使用python的调度器，而不是用linux自带的contab呢？
1、不想依赖于外部配置，这样，代码就可以一键配置好了，不用再配置这配置那
2、逻辑上、阅读上更连贯，从代码中就可以获取一切，而不需要再读什么外部文档

参考：
 - https://www.cnblogs.com/leffss/p/11912364.html
 遇到一个坑：用进程池，死活报错：
     retval = job.func(*job.args, **job.kwargs)
    TypeError: object() takes no parameters
 都已经放弃了把client作为构造函数参数传入TaskJob的企图，而是用add_job(args=[clinet])了，还是报这个错，
 后来，去读了官网文档，首推trehadpool，靠，好吧，放弃了进程池了，以后线程有问题再说吧
 
 https://apscheduler.readthedocs.io/en/3.x/userguide.html?highlight=ProcessPoolExecutor#configuring-the-scheduler:
 "Likewise, the choice of executors is usually made for you if you use one of the frameworks above. 
 Otherwise, the default ThreadPoolExecutor should be good enough for most purposes. "
"""

logger = logging.getLogger(__name__)


def start_scheduler(broker):
    """
    目前有2个调度：
    - 每天 9:30 点运行，每隔10分钟，执行一次买卖
    - 每天 23:00 运行，执行一遍同步
    # https://tooltt.com/crontab/c/83.html
    """

    # 进程池搞不定，只好用线程池了
    scheduler = BackgroundScheduler(executors={
        'threadpool': ThreadPoolExecutor(max_workers=1, )
    })
    logger.debug("创建调度器完成")

    # # 启动买卖调度器
    # scheduler.add_job(
    #     func=TradeJob(),
    #     args=[broker],
    #     trigger='interval',
    #     minutes=CONF['scheduler']['trade']['interval'],
    #     max_instances=1,
    #     executor='threadpool',
    # )
    # logger.debug("调度任务启动，时间间隔为：%s 分", CONF['scheduler']['trade']['interval'])
    #
    # # 启动仓位同步调度器
    # scheduler.add_job(
    #     func=PositionSyncJob(),
    #     args=[broker],
    #     trigger=CronTrigger.from_crontab(CONF['scheduler']['position_sync']['cron']),
    #     max_instances=1,
    #     executor='threadpool',
    # )
    # logger.debug("调度任务启动，周期为（cron）：%s ", CONF['scheduler']['position_sync']['cron'])

    # 启动心跳调度器
    scheduler.add_job(
        func=HeartbeatJob(),
        args=[broker],
        trigger='interval',
        minutes=CONF['scheduler']['heartbeat']['interval'],
        max_instances=1,
        executor='threadpool',
    )
    logger.debug("心跳调度任务启动，时间间隔为：%s 分", CONF['scheduler']['heartbeat']['interval'])

    scheduler.start()
    logger.info("启动了任务！主进程：%d", os.getpid())
    return scheduler


# python -m server.scheduler.scheduler
if __name__ == '__main__':
    """
    测试代码
    """

    utils.init_logger(simple=True)

    __broker = broker.get("easytrader")
    logger.info("启动进程：%d", os.getpid())

    # 实际不测试用，插入一个查询资金的命令
    # sqlite.task("000001.SH", TRADE_BALANCE, 0, 0)
    # logger.debug("插入查询资金的任务")

    # 每一分钟启动一次测试
    s = start_scheduler(__broker, cron='0/1 * * * *')

    while True:
        time.sleep(10)

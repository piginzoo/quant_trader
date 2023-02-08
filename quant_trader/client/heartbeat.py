import datetime
import time

from quant_trader.utils import utils, CONF
import logging

logger = logging.getLogger(__name__)


def run():
    """
    将买、卖信号推送到服务器,间隔是60s，写死的，没必要灵活配置
    :return:
    """
    while True:
        try:
            full_url = utils.get_url()
            utils.http_json_post(full_url,{"action": "heartbeat","name": "etf"}) # name是为了标识系统
        except Exception:
            logger.exception("推送[ETF]心跳失败")

        logger.info("发送[ETF]心跳：%s",datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S"))
        time.sleep(60) # 写死了，懒得再写配置了

if __name__ == '__main__':
    utils.init_logger()
    run()
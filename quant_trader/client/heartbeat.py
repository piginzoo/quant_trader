import datetime
import time

from quant_trader.utils import utils
import logging

logger = logging.getLogger(__name__)

trade_log= 'c:\\workspace\\iquant\\history\\transaction.csv'  # 交易记录
last_grid_position= 'c:\\workspace\\iquant\\history\\last_grid_position.json'  # 最后的日期


def run():
    """
    将买、卖信号推送到服务器,间隔是60s，写死的，没必要灵活配置
    :return:
    """
    while True:
        try:
            full_url = utils.get_url()
            utils.http_json_post(
                full_url,
                {
                    "action": "heartbeat",
                    "name": "etf"},
                files = {
                  "field1" : ("transaction.csv", open(trade_log, "r")),
                  "field2" : ("last_grid_position.json", open(last_grid_position, "r")),
                }
            ) # name是为了标识系统

        except Exception:
            logger.exception("发送[ETF]心跳失败")

        # logger.info("发送[ETF]心跳完成：%s",datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S"))
        time.sleep(60) # 写死了，懒得再写配置了

if __name__ == '__main__':
    utils.init_logger()
    run()
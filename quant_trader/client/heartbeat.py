import datetime
import json
import os.path
import time
import requests

from quant_trader.utils import utils
import logging

logger = logging.getLogger(__name__)

conf = utils.load_config()

# 所有的要发送的文件
file_paths = conf['heartbeat']['files']

def run():
    """
    将买、卖信号推送到服务器,间隔是60s，写死的，没必要灵活配置
    :return:
    """
    while True:
        try:
            full_url = utils.get_url()

            files = {}
            for file_path in file_paths:
                if not os.path.exists(file_path):
                    logger.warning("文件不存在：%s",file_path)
                    continue
                file_name = os.path.split(file_path)[-1]
                files[file_name] = open(file_path, "rb")
                logger.debug("加载文件：%s",file_path)

            data = {
                    "action": "heartbeat",
                    "name": "server" # server，这个是用来回报服务器的心跳包，与之对应的是qmt软件心跳包
            }
            # 这里没用utils.http_post,单独写，必须这么写，用data发送，且，不能设置header，让自己去自动设
            response = requests.post(full_url, files=files, data=data)
            logger.info("发送心跳包到=>%s，附带文件%d个",full_url,len(files))
            data = response.json()
            logger.info('接口返回Json报文:%r', data)
            return data

        except Exception as e:
            #logger.exception("发送[ETF]心跳失败")
            logger.error("发送[ETF]心跳失败:"+str(e))

        # logger.info("发送[ETF]心跳完成：%s",datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S"))
        time.sleep(conf['heartbeat']['interval']) # 写死了，懒得再写配置了

if __name__ == '__main__':
    utils.init_logger("logs/heartbeat.log")
    run()
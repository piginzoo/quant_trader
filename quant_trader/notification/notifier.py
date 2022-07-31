from quant_trader.notification import wxbot, email, INFO, WARN, ERROR
from quant_trader.utils import CONF
import logging

logger = logging.getLogger(__name__)


def get_channel_notifier(type):
    if type == "weixin":
        return wxbot
    if type == "email":
        return email
    raise ValueError(type)


def notify(msg, msg_type):
    """
    目前是俩渠道：企业微信、邮件
    每次有问题，都发，
    有3个level，INFO\ERROR\WARN，不是包含关系，制定了就发
    还会自动记录日志，所以notify的时候，不用再额外记录日志了。

    notification: # level: ERROR,INFO是分开的，而不是传统意义上包含的关系，这样做是为了方便分开通知和报警
         - weixin:
           -
             name: '股票群1'
             url: 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=7b11e92a-c17c-4d8b-b9a8-2678ba1807da'
             level: 'INFO'
           -
             name: '股票群2'
             url: 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=13d1c305-90c0-4924-a692-b57a12ffd6be'
             level: 'ERROR,WARN'
        - email:
           -
             name: '我的邮箱'
             url: 'piginzoo@qq.com'
             level: 'INFO,ERROR,WARN'
    :param msg:
    :param msg_type:
    :return:
    """

    # 先记录个日志
    if msg_type == INFO:
        logger.info(msg)
    if msg_type == WARN:
        logger.warning(msg)
    if msg_type == ERROR:
        logger.error(msg)

    confs = CONF['notification']
    for channel_type in confs:
        # 处理每个类型，每个类型里可能多个消息通道
        # 比如微信，可能有多个微信通道
        assert type(channel_type) == dict, str(type(channel_type))
        assert len(channel_type.keys()) == 1
        channel_type_name = [*channel_type][0]  # 只可能有一个key
        channels = channel_type[channel_type_name]

        for channel in channels:
            """
             name: '我的邮箱'
             url: 'piginzoo@qq.com'
             level: 'INFO,ERROR'            
            """
            name = channel['name']
            url = channel['url']
            level = channel['level']
            levels = level.split(",")  # 可能多个级别，用逗号分割

            if msg_type not in levels: continue

            msg_notifier = get_channel_notifier(channel_type_name)
            r = msg_notifier.send_msg(name, url, msg_type, msg)
            if r:
                logger.debug("发送到[%s]，级别为[%s]的消息成功", name, level)
            else:
                logger.debug("发送到[%s]，级别为[%s]的消息失败", name, level)

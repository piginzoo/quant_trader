import logging
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


from quant_trader.utils import utils, conf
from quant_trader.server.const import TRADE_STATUS_DONE, TRADE_BUY
from quant_trader.server.db import trade_bo
from quant_trader.server.db.trade_bo import TradeTask, TradeLog, TradePosition

logger = logging.getLogger(__name__)


def connect_database(echo=False):
    if not os.path.exists(conf.SQLITE_DB_FILE):
        db_dir = os.path.split(conf.SQLITE_DB_FILE)[0]
        if not os.path.exists(db_dir): os.makedirs(db_dir)  # 创建目录
        trade_bo.create_db()

    engine = create_engine('sqlite:///' + conf.SQLITE_DB_FILE + '?check_same_thread=False',
                           echo=echo)  # 是否显示SQL：, echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def query_log():
    session = connect_database()
    return session.query(TradeLog).all()


def task(code, trade_type, price, share, signal_date, strategy,broker_name):
    session = connect_database()
    session.add(TradeTask(code, trade_type, price, share, signal_date, strategy,broker_name))
    session.commit()
    logger.info("保存交易任务到db：%s股票%s，%d股，信号日期：%s", trade_type, code, share, signal_date)


def del_task(code):
    session = connect_database()
    session.query(TradeTask).filter_by(code=code).delete()
    session.commit()
    logger.info("从数据库[TradeTask表]中删除了股票[%s]的交易任务", code)


def del_position(position):
    session = connect_database()
    session.query(TradePosition).filter_by(id=position.id).delete()
    session.commit()
    logger.info("从数据库[TradePostion表]中删除了股票[%s]的仓位", position.code)


def query_task(broker_name, code=None, id=None):
    session = connect_database()
    if code:
        return session.query(TradeTask).filter(TradeTask.code == code).first()
    if id:
        return session.query(TradeTask).filter(TradeTask.id == id).first()
    return session.query(TradeTask).filter(TradeTask.broker_name == broker_name).all()


def query_position(broker_name):
    session = connect_database()
    return session.query(TradePosition).filter(TradePosition.broker_name == broker_name).all()


def query_log(broker_name):
    session = connect_database()
    return session.query(TradeLog).filter(TradeLog.broker_name == broker_name).all()


def task_archieve(task_id, status, message):
    """任务失败后更新"""
    session = connect_database()
    try:
        task = session.query(TradeTask).filter(TradeTask.id == task_id).first()
        session.add(TradeLog(task=task,status=status,message=message))
        session.query(TradeTask).filter(TradeTask.id == task_id).delete()
        session.commit()
        logger.debug("股票买卖任务归档[%s]：task->log：%s", message, str(task))
        return True
    except:
        logger.exception("股票买卖任务归档异常：task->log, task->position, task_id=%d", task_id)
        session.rollback()
        return False


def task_done(task, price=None, message='交易完成'):
    """任务成功后更新"""
    session = connect_database()
    try:
        # 更新一下价格，主要是对卖而言
        if price is not None: task.price = price

        # 处理仓位信息（买）
        if task.trade_type == TRADE_BUY:
            trade_position = TradePosition(code=task.code,
                                           price=price,
                                           share=task.share,
                                           signal_date=task.signal_date,
                                           trade_datetime=utils.now(),
                                           strategy=task.strategy,
                                           broker_name=task.broker_name)
            session.add(trade_position)
            logger.debug("更新买入信息，插入仓位表：%r", trade_position)
        # 处理仓位信息（卖）
        else:
            # 删除持仓表，需要用股票代码
            trade_positoin = session.query(TradePosition).filter(TradePosition.code == task.code).first()
            # 要从仓位表中，取得这个股票对应的策略!!!
            task.strategy = trade_positoin.strategy
            # 卖出任务是没有券商信息的，要从仓位信息中获取!!!
            task.broker_name = trade_positoin.broker_name
            # 然后，就可以删掉他了
            session.query(TradePosition).filter(TradePosition.code == task.code).delete()
            logger.debug("更新卖出信息，删除仓位表，通过股票代码: %s", task.code)

        # 归档task => log（注意，卖出的时候，从仓位信息中获得之前的策略名，这个细节需要特别说明一下）
        trade_log = TradeLog(task=task,status=TRADE_STATUS_DONE,message=message)
        session.add(trade_log)
        logger.debug("插入日志表：%r", trade_log)

        # 删除task
        session.query(TradeTask).filter(TradeTask.id == task.id).delete()
        logger.debug("删除任务表：%r", task)

        session.commit()
        logger.debug("更新了股票买/卖任务：task->log, task->position：%r", task)
    except:
        logger.exception("股票买卖任务更新异常：task->log, task->position：%r", task)
        session.rollback()


def update_task_entrust_no_retry_lastime(code, entrust_no):
    session = connect_database()

    try:
        task = session.query(TradeTask).filter(TradeTask.code == code).limit(1).first()
        task.entrust_no = entrust_no
        task.last_datetime = utils.now()  # <---- 更新最后时间
        task.retry = task.retry + 1  # <---- 把重试次数加1
        session.flush()
        session.commit()
        logger.debug("股票[%s]的委托单号被更新=>%s，重试：%d，时间：%s", code, task.entrust_no, task.retry, task.last_datetime)
    except:
        logger.exception("股票[%s]的委托单号更新=>%s，发生异常", code, entrust_no)
        session.rollback()


def update_position(code, price, share):
    session = connect_database()

    try:
        task = session.query(TradePosition).filter(TradePosition.code == code).limit(1).first()
        if task is None:
            logger.warning("无法检索在逻辑持仓表中检索到股票[%s]信息", code)
            return False
        if price: task.price = price
        if share: task.share = share
        session.flush()
        session.commit()
        logger.debug("股票[%s]的逻辑持仓表被更新: price=%r, share=%r", code, price, share)
    except:
        logger.exception("股票[%s]的逻辑持仓表更新发生异常: price=%r, share=%r", code, price, share)
        session.rollback()


def create_position(position):
    try:
        session = connect_database()
        session.add(position)
        session.commit()
        logger.info("创建持仓到db：%r", position)
        return True
    except:
        logger.exception("股票[%s]的逻辑持仓表创建发生异常: %r", position)
        session.rollback()
        return False


# python -m server.db.sqlite
if __name__ == '__main__':
    pass

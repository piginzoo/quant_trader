import os
import time
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import logging
import gc

logger = logging.getLogger(__name__)
matplotlib.use('agg')


def generate(conf):
    """
    本来生成svg，太大,1.2m，导致我的api1-tokyo服务器总是导致内存溢出，
    所以改成了生成jpg文件，也不推送图片/svg内容回去了，
    而是改成推生成推片的服务器url，这样最节省资源。
    :param conf:
    :return:
    """

    # 加载各个etf,存放目录里面还有别的文件，所以要过滤下
    # 为何不单独放一个目录，是因为就不通用了，那个目录里放着所有需要upload服务器的文件
    etf_dir = conf['etf']['dir']
    jpg_url = conf["etf"]["jpg_path"]
    jpg_fullpath = f'web_root{jpg_url}'

    if not is_need_regenerate(jpg_fullpath):
        today_date = time.strftime('%Y%m%d', time.localtime(time.time()))
        logger.debug("今日[%s]图片已经生成，直接返回：%s", today_date, jpg_fullpath)
        return jpg_url

    dfs = []
    # 510330.SH.csv
    for f in os.listdir(etf_dir):
        # 必须是包含：csv和SH、SZ的文件
        if "csv" not in f: continue
        if "SH" not in f and "SZ" not in f: continue
        file_path = os.path.join(etf_dir, f)
        df = load(file_path)
        code = df.iloc[0].code
        logger.debug("加载了[%s]文件:%s", code, file_path)
        df = calc(df)
        logger.debug("计算了[%s]数据:%s", code, file_path)
        dfs.append(df)
    generate_jpg(dfs, jpg_fullpath)
    logger.debug("生成了JPG图:%s", jpg_fullpath)
    return jpg_url


def is_need_regenerate(full_path):
    """
    为了防止内存溢出，每天只生成1次，
    :param full_path:
    :return:
    """
    if not os.path.exists(full_path):
        return True
    stat = os.stat(full_path)
    file_date = time.strftime('%Y%m%d', time.localtime(stat.st_ctime))
    today_date = time.strftime('%Y%m%d', time.localtime(time.time()))
    logger.debug("文件%s vs 今日%s",file_date,today_date)
    return not file_date == today_date


def load(file_path):
    code = os.path.split(file_path)[-1][:6]
    df = pd.read_csv(file_path)
    df = df.rename(columns={"Unnamed: 0": "date"})
    df['date'] = df.date.apply(str)
    df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
    df['code'] = code
    return df


def calc(df):
    df['ma'] = df.close.rolling(window=850, min_periods=1).mean()
    df['ma'] = df['ma'].shift(1) # 把昨天的ma，当做今天需要计算用的ma，这个是因为我盘中算的时候，用的ma，肯定是昨天的ma
    df['diff_percent_close2ma'] = (df.close - df.ma) / df.ma
    p = df[df.diff_percent_close2ma > 0].diff_percent_close2ma.quantile(0.8)
    n = df[df.diff_percent_close2ma < 0].diff_percent_close2ma.quantile(1 - 0.4)
    df['ma_upper'] = df.ma * (1 + p)
    df['ma_lower'] = df.ma * (1 + n)
    df['p'] = p
    df['n'] = n
    return df


def generate_jpg(dfs, jpg_path):
    fig = plt.figure(figsize=(20, 5 * len(dfs)))
    for i, df in enumerate(dfs):
        ax = fig.add_subplot(len(dfs), 1, i + 1)  # , rasterized=True) # rasterized 栅格化，把svg矢量变图片
        ax.set_title(df.iloc[0].code)
        ax.plot(df.date, df.close)
        ax.plot(df.date, df.ma, color='#6495ED', linestyle='--', linewidth=1)
        ax.fill_between(df.date, df.ma_upper, df.ma_lower, alpha=0.2)
        ax.set_ylabel('etf基金价格')

        x = df.iloc[-1].date
        y = df.iloc[-1].close + 0.1
        x_text = df.iloc[-200].date
        y_text = df.iloc[-1].close + 0.2
        positive = df.iloc[-1].p
        negative = df.iloc[-1].n
        ax.text(df.iloc[0].date, df.close.max(), '正收益80%分位数：{:.2f}%'.format(positive * 100))
        ax.text(df.iloc[0].date, df.close.max() - 0.2, '负收益40%分位数：{:.2f}%'.format(negative * 100), color='r')
        last_date = datetime.strftime(x,"%Y-%m-%d")
        label = \
f"""日期:{last_date}
收盘:{df.iloc[-1].close}
850均值:{round(df.iloc[-1].ma,2)}
距离均值:{round(df.iloc[-1].diff_percent_close2ma * 100, 2)}%"""
        ax.annotate(label,
                    color='r',
                    xy=(x, y),
                    xytext=(x_text, y_text),
                    arrowprops=dict(facecolor='black', shrink=0.05))
    fig.tight_layout()
    # 输出成svg，不过太了，即使用 rasterized 栅格化，也900K
    # 改为jpg，并且，每日只生成1次
    # fig.savefig(jpg_path, format='svg') #, dpi=100)
    fig.savefig(jpg_path, format='jpg')

    # 2023.2.16,bugfix for 内存泄露 https://stackoverflow.com/questions/7101404/how-can-i-release-memory-after-creating-matplotlib-figures
    fig.clf()
    plt.close()
    del dfs
    gc.collect

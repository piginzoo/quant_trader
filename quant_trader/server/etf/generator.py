import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import logging

logger = logging.getLogger(__name__)
matplotlib.use('agg')


def generate(conf):
    # 加载各个etf,存放目录里面还有别的文件，所以要过滤下
    # 为何不单独放一个目录，是因为就不通用了，那个目录里放着所有需要upload服务器的文件
    etf_dir = conf['etf']['dir']
    svg_path = conf['etf']['svg_path']
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
    generate_svg(dfs, svg_path)
    logger.debug("生成了SVG图")
    return svg_path


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
    df['diff_percent_close2ma'] = (df.close - df.ma) / df.ma
    p = df[df.diff_percent_close2ma > 0].diff_percent_close2ma.quantile(0.8)
    n = df[df.diff_percent_close2ma < 0].diff_percent_close2ma.quantile(1 - 0.4)
    df['ma_upper'] = df.ma * (1 + p)
    df['ma_lower'] = df.ma * (1 + n)
    df['p'] = p
    df['n'] = n
    return df


def generate_svg(dfs, svg_path):
    fig = plt.figure(figsize=(20, 10 * len(dfs)))
    for i, df in enumerate(dfs):
        ax = fig.add_subplot(len(dfs), 1, i + 1)
        ax.set_title(df.iloc[0].code)
        ax.plot(df.date, df.close)
        ax.plot(df.date, df.ma, color='#6495ED', linestyle='--', linewidth=1)
        ax.fill_between(df.date, df.ma_upper, df.ma_lower, alpha=0.2)
        ax.set_ylabel('etf基金价格')

        x = df.iloc[-1].date
        y = df.iloc[-1].close
        x_text = df.iloc[-100].date
        y_text = df.iloc[-1].close + 0.2
        positive = df.iloc[-1].p
        negative = df.iloc[-1].n
        ax.text(df.iloc[0].date, df.close.max(), '正收益80%分位数：{:.2f}%'.format(positive * 100))
        ax.text(df.iloc[0].date, df.close.max() - 0.2, '负收益20%分位数：{:.2f}%'.format(negative * 100), color='r')
        label = str(round(df.iloc[-1].diff_percent_close2ma * 100, 2)) + "%"
        ax.annotate(label, xy=(x, y),
                    xytext=(x_text, y_text),
                    arrowprops=dict(facecolor='black', shrink=0.05))
    fig.tight_layout()
    fig.savefig(svg_path, format='svg', dpi=30)

    # 2023.2.16,bugfix for 内存泄露 https://stackoverflow.com/questions/7101404/how-can-i-release-memory-after-creating-matplotlib-figures
    fig.clf()
    plt.close()
    del dfs


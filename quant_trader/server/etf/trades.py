import os

from pandas import DataFrame

from quant_trader.utils import utils



def market_values(home_dir):

    files = os.listdir(home_dir)

    df = DataFrame(columns=['date', 'value'])
    for f in files:
        # print(f) ， positions.20230304.json
        if not "positions" in f: continue
        if f == 'positions.json': continue
        positions = utils.unserialize(os.path.join(home_dir, f))
        market_value = 0
        date = f[10:18]
        for p in positions:
            market_value += p['市值']
        df = df.append({'date': utils.str2date(date), 'value': market_value}, ignore_index=True)

    df.sort_values(by='date', inplace=True)
    return df

# python -m quant_trader.server.etf.trades

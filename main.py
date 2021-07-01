from pycoingecko import CoinGeckoAPI
import pandas as pd
import numpy as np
import time
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
cg = CoinGeckoAPI()

coins = [
    'tether'
    ,'usd-coin'
    ,'binance-usd'
    ,'dai'
    ,'terrausd'
    ,'true-usd'
    ,'paxos-standard'
    ,'liquity-usd'
    ,'husd'
    ,'neutrino'
    ,'fei-protocol'
    ,'alchemix-usd'
    ,'gemini-dollar'
    ,'frax'
    ,'nusd'
]
coins_df = pd.DataFrame(coins)
coins_df.columns = ['symbol']

coins_df['type'] = np.where(coins_df['symbol'].isin(['tether','usd-coin'
    ,'binance-usd','true-usd','paxos-standard'
    ,'husd','gemini-dollar']),'Fiat collateralized', 'Algo-stable')


# x = cg.get_coin_market_chart_range_by_id(id='ust',vs_currency='usd',from_timestamp='1624968752',to_timestamp='1625055153')

df = pd.DataFrame()
for i in range(0,len(coins)):
    coin = coins[i]
    x = cg.get_coin_market_chart_range_by_id(id=coin,vs_currency='usd',from_timestamp='1609459200',to_timestamp='1625072479')
    xmcap = x['market_caps']
    xdf = pd.DataFrame(xmcap)
    xdf['symbol'] = coins[i]
    df = df.append(xdf)
    print(f'Data pulled for {coins[i]}, waiting for 3 secs')
    time.sleep(3)

df.columns = ['timestamp', 'mcap', 'symbol']
df.to_csv('raw_data_pull.csv')

df = pd.read_csv('raw_data_pull.csv')[['timestamp', 'mcap', 'symbol']]

df['date'] = pd.to_datetime(df['timestamp'],unit='ms')
df['week'] = df['date'].dt.week
df = df[df['week'] < 53]
df = df.merge(coins_df, left_on = ['symbol'], right_on = ['symbol'], how = 'inner')

df['time_rank'] = df.groupby(['week', 'symbol'])['timestamp'].rank(method = 'first', ascending = False)
df = df[df['time_rank'] == 1]



df_grp = df.groupby(['type', 'week'], as_index = False)['mcap'].sum()
df_grp_1 = df_grp[df_grp['week'] == 1]
df_grp = df_grp.merge(df_grp_1, left_on = ['type'], right_on = ['type'], how='inner')

df_grp['YTD growth'] = ((df_grp['mcap_x'] - df_grp['mcap_y'])/df_grp['mcap_y'])
df_grp = df_grp.rename(columns = {'type':'Type'})
df_grp = df_grp.pivot(index = 'week_x', columns = 'Type', values = 'YTD growth')

ax = df_grp.plot()
plt.title("YTD market capitalization growth %")
plt.xlabel('Weeks since 2021-01-01')
plt.ylabel('Market cap growth')
ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1, decimals=None, symbol='%', is_latex=False))
plt.savefig('plot.pdf')

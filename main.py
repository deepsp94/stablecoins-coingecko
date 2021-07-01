from pycoingecko import CoinGeckoAPI
import pandas as pd
import numpy as np
import time
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn
cg = CoinGeckoAPI()

# List of stables to analyse - these are the top 15 stables by market cap on 1st July 2021. Source: coingecko
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


################################################# Algo vs Fiat chart ################################################# 

# Classification
coins_df['type'] = np.where(coins_df['symbol'].isin(['tether','usd-coin'
    ,'binance-usd','true-usd','paxos-standard'
    ,'husd','gemini-dollar']),'Fiat collateralized', 'Algo-stables')


df = pd.DataFrame()
for i in range(0,len(coins)):
    coin = coins[i]
    x = cg.get_coin_market_chart_range_by_id(id=coin,vs_currency='usd',from_timestamp='1609459200',to_timestamp='1625072479') # from 2021-01-01 to now
    xmcap = x['market_caps']
    xdf = pd.DataFrame(xmcap)
    xdf['symbol'] = coins[i]
    df = df.append(xdf)
    print(f'Data pulled for {coins[i]}, waiting for 3 secs')
    time.sleep(3) # to not stress the API

df.columns = ['timestamp', 'mcap', 'symbol']
df.to_csv('raw_data_pull.csv') # Checkpoint. So no need to hit the API again and again while iterating on data

df = pd.read_csv('raw_data_pull.csv')[['timestamp', 'mcap', 'symbol']]

df['date'] = pd.to_datetime(df['timestamp'],unit='ms')
df['week'] = df['date'].dt.week
df = df[df['week'] < 53] # Removing a timestamp from Dec 2020
df = df.merge(coins_df, left_on = ['symbol'], right_on = ['symbol'], how = 'inner')


# Getting the last mcap value for a week. Kind of like weekly close on a candle
df['time_rank'] = df.groupby(['week', 'symbol'])['timestamp'].rank(method = 'first', ascending = False)
df = df[df['time_rank'] == 1]
df.to_csv('final_data.csv')


df_grp = df.groupby(['type', 'week'], as_index = False)['mcap'].sum() # Aggregate to "type" level
df_grp_1 = df_grp[df_grp['week'] == 1] # Every week will be compared to the first week of the year
df_grp = df_grp.merge(df_grp_1, left_on = ['type'], right_on = ['type'], how='inner')

df_grp['YTD growth'] = ((df_grp['mcap_x'] - df_grp['mcap_y'])/df_grp['mcap_y']) 
df_grp = df_grp.rename(columns = {'type':'Type'})
df_grp = df_grp.pivot(index = 'week_x', columns = 'Type', values = 'YTD growth')


# Plot
ax = df_grp.plot()
plt.style.use('seaborn')
plt.title("YTD market capitalization growth %")
plt.xlabel('# Weeks since 2021-01-01')
plt.ylabel('Market cap growth')
ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1, decimals=None, symbol='%', is_latex=False))
plt.legend(loc='lower right', prop={'size': 10})

ax.annotate(
    text='Crypto market crash on 19th May',
    xy=(19,4.113689),
    xycoords='data',
    fontsize=10,
    xytext=(-125, 0),
    textcoords='offset points',
    arrowprops=dict(arrowstyle='->', color='black'),  # Use color black
    horizontalalignment='center',  # Center horizontally
    verticalalignment='center')

ax.annotate(
    text='Growth trends\n decouple post Jan',
    xy=(5,0.246803),
    xycoords='data',
    fontsize=10,
    xytext=(85, 0),
    textcoords='offset points',
    arrowprops=dict(arrowstyle='->', color='black'),  # Use color black
    horizontalalignment='center',  # Center horizontally
    verticalalignment='center')

# plt.show()
plt.savefig('plot.jpeg')



################################################# Market cap chart #################################################

# df = pd.read_csv('raw_data_pull.csv')[['timestamp', 'mcap', 'symbol']] # read YTD data

coins = ['tether','usd-coin','binance-usd','dai','terrausd']

df = pd.DataFrame()
for i in range(0,len(coins)):
    coin = coins[i]
    x = cg.get_coin_market_chart_range_by_id(id=coin,vs_currency='usd',from_timestamp='1593541800',to_timestamp='1625072479') # last 1 year
    xmcap = x['market_caps']
    xdf = pd.DataFrame(xmcap)
    xdf['symbol'] = coins[i]
    df = df.append(xdf)
    print(f'Data pulled for {coins[i]}, waiting for 3 secs')
    time.sleep(3) # to not stress the API

df.columns = ['timestamp', 'mcap', 'symbol']

df['date'] = pd.to_datetime(df['timestamp'],unit='ms')
df = df[df['symbol'].isin(['tether','usd-coin','binance-usd','dai','terrausd'])] # Filter to top 5 by mcap
df['mcap'] = df['mcap']/1000000000

df = df.replace(to_replace ="tether",value ="USDT")
df = df.replace(to_replace ="usd-coin",value ="USDC")
df = df.replace(to_replace ="binance-usd",value ="BUSD")
df = df.replace(to_replace ="dai",value ="Dai")
df = df.replace(to_replace ="terrausd",value ="UST")

df = df.pivot(index = 'date', columns = 'symbol', values = 'mcap')

df.plot()
plt.xlabel("")
plt.ylabel("Market Capitalization (billions $)")
plt.legend(*(
    [ x[i] for i in [3,2,0,1,4] ]
    for x in plt.gca().get_legend_handles_labels()
), handletextpad=0.75, loc='best')
plt.legend(title = 'Stablecoin', fontsize = 8)
plt.show()


df.plot()
plt.style.use('seaborn')
plt.title("Market capitalization of top 5 stables")
plt.xlabel("")
plt.ylabel("Market Capitalization ($ billions)")
plt.legend(*(
    [ x[i] for i in [3,2,0,1,4] ]
    for x in plt.gca().get_legend_handles_labels()
), handletextpad=0.75, loc='best')
# plt.legend(title = 'Stablecoin', fontsize = 8)
plt.savefig('plot_mcap.jpeg')
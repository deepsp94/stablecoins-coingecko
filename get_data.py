from pycoingecko import CoinGeckoAPI
import pandas as pd
import numpy as np

coins = [
    'tether'
    ,'usd-coin'
    ,'binance-usd'
    ,'dai'
    ,'terra-usd'
    ,'true-usd'
    ,'paxos-standard'
    ,'liquity-usd'
    ,'husd'
    ,'neutrino-usd'
    ,'fei-protocol'
    ,'alchemix-usd'
    ,'gemini-dollar'
    ,'frax'
    ,'susd'
]
coins_df = pd.DataFrame(coins)
coins_df.columns = ['Symbol']

coins_df['Type'][coins_df['Symbol'].isin(['tether','usd-coin'
    ,'binance-usd','true-usd','paxos-standard'
    ,'husd','gemini-dollar'])]= 'Fiat collateralized'

coins_df['Type'][coins_df['Symbol'].isin(['terra-usd','neutrino-usd'
    ,'fei-protocol','alchemix-usd','frax'])]= 'Crypto (under)collateralized'

coins_df['Type'][coins_df['Symbol'].isin(['dai','liquity-usd','neutrino-usd'
    ,'fei-protocol','alchemix-usd','frax'])]= 'Crypto (over)collateralized'



cg = CoinGeckoAPI()

x = cg.get_coin_market_chart_range_by_id(id='liquity-usd',vs_currency='usd',from_timestamp='1624968752',to_timestamp='1625055153')


# for i in range(0,len(coins)):

pd.DataFrame(x['market_caps'][0:5])
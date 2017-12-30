#!/usr/bin/env python3
import requests as rq

# Coin market cap
API_URL = 'https://api.coinmarketcap.com/v1/{}/'
MARKET_CAP = 'total_market_cap_usd'

# API_URL = 'http://coincap.io/global'

def request_global_market():

    url = API_URL.format('global')
    res = rq.get(url, timeout=3)
    return res

def request_coin(ticker=None):

    url = API_URL.format('ticker')
    if ticker:
        url += '{}/'
        url  = url.format(ticker)

    res = rq.get(url, timeout=3)
    return res

def get_global_market():

    market = None
    resp = request_global_market()

    if resp.status_code == 200:
        market = resp.json()

    return market

def get_bitcoin_info():

    info = None
    resp = request_coin('bitcoin')

    if resp.status_code == 200:

        coins = resp.json()

        if not coins:
            return None

        info = coins[0]

        # Add change data
        current_market_cap = float(info['market_cap_usd'])
        percent_change = float(info['percent_change_24h'])

        old_market_cap = current_market_cap / (percent_change + 1)
        info['change_24h'] = current_market_cap - old_market_cap
    
    return info

class MarketChange:

    def __init__(self):

        self.reference = None
        self.current = None

    # Returns True if it detects a major change
    def compare_market(self):

        if self.reference is None:
            return False

        old_cap = float(self.reference[MARKET_CAP])
        new_cap = float(self.current[MARKET_CAP])

        diff = new_cap - old_cap
        percent_change = diff / old_cap

        print('Changed: {:+.2f}'.format(diff))
        print('24h change: {:+.2f}'.format(percent_change))

        if abs(diff) > 10000000000:
            print('changed by 10b!')
            return True

        return False

    def calculate_change(self):

        old_cap = float(self.reference[MARKET_CAP])
        new_cap = float(self.current[MARKET_CAP])

        diff = new_cap - old_cap
        percent_change = diff / old_cap

        return {
            'market_cap_change': diff,
            'percent_change_24h': percent_change
        }


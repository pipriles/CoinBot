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

        old_market_cap = current_market_cap / (percent_change/100 + 1)
        info['change_24h'] = current_market_cap - old_market_cap
    
    return info

def changes_text(market):

    total = market.calculate_change()
    coin = get_bitcoin_info()

    diff = total['market_cap_change']
    percent_change = market['percent_change_24h']

    news  = 'Total Market Cap:\n'
    news += 'Change: {:+.2f}\n'.format(diff)
    news += '24h Change: {:+.2f}%'.format(percent_change)

    diff = coin['change_24h']
    percent_change = coin['percent_change_24h']
    
    news += 'Bitcoin Market Cap:\n'
    news += 'Change: {:+.2f}\n'.format(diff)
    news += '24h Change: {:+.2f}%'.format(percent_change)
    
    return news

class MarketChange:

    def __init__(self):

        self.reference = None
        self.current = None

    # Returns True if it detects a major change
    def compare_market(self):

        if self.reference is None:
            return False

        change = self.calculate_change()

        diff = change['market_cap_change']
        percent_change = change['percent_change_24h']

        print('Changed: {:+.2f}'.format(diff))
        print('24h change: {:+.2f}'.format(percent_change))

        if abs(diff) > 10000000000:
            print('changed by 10b!')
            return True

        return False

    def calculate_change(self):

        diff = 0
        percent_change = 0

        if self.reference and self.current:

            old_cap = float(self.reference[MARKET_CAP])
            new_cap = float(self.current[MARKET_CAP])

            diff = new_cap - old_cap
            percent_change = diff / old_cap * 100

        return {
            'market_cap_change': diff,
            'percent_change_24h': percent_change
        }

    def changes_text(self):

        total = self.calculate_change()
        coin = get_bitcoin_info()

        diff = total['market_cap_change']
        percent_change = total['percent_change_24h']

        news  = 'Total Market Cap:\n'
        news += 'Change: {:+.2f}\n'.format(float(diff))
        news += '24h Change: {:+.2f}%'.format(float(percent_change))

        diff = coin['change_24h']
        percent_change = coin['percent_change_24h']
        
        news += '\n\n'
        news += 'Bitcoin Market Cap:\n'
        news += 'Change: {:+.2f}\n'.format(float(diff))
        news += '24h Change: {:+.2f}%'.format(float(percent_change))
        
        return news



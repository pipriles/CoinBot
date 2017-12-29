#!/usr/bin/env python3
import requests as rq

# Coin market cap
# API_URL = 'https://api.coinmarketcap.com/v1/{}/'

API_URL = 'http://coincap.io/global'
MARKET_CAP = 'totalCap'

def request_global_market():
    url = API_URL.format('global')
    res = rq.get(url, timeout=30)
    return res

def request_all_coins():
    url = API_URL.format('ticker')
    res = rq.get(url, timeout=30)
    return res

def get_global_market():

    market = None
    resp = request_global_market()

    if resp.status_code == 200:
        market = resp.json()

    return market

class MarketInfo:

    def __init__(self):

        self.reference = None
        self.current = None

    # Returns True if it detects a major change
    def compare_market(self):

        if self.reference is None:
            return False

        oldcap = self.reference[MARKET_CAP]
        newcap = self.current[MARKET_CAP]

        diff = newcap - oldcap
        percent_change = diff / oldcap

        print('Changed: {:+.2f}'.format(diff))
        print('24h change: {:+.2f}'.format(percent_change))

        if abs(diff) > 1:
            print('changed by 10b!')
            return True

        return False

    def market_change_text(self):

        oldcap = self.reference[MARKET_CAP]
        newcap = self.current[MARKET_CAP]

        diff = newcap - oldcap
        percent_change = diff / oldcap

        text  = 'Total Market Cap:\n'
        text += 'Change: {:+.2f}\n'.format(diff)
        text += '24h Change: {:+.2f}%'.format(percent_change)

        return text


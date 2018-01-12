#!/usr/bin/env python3.6
import requests as rq
import time

# Coin market cap
API_URL = 'https://api.coinmarketcap.com/v1/{}/'
MARKET_CAP = 'total_market_cap_usd'
BITCOIN_PART = 'bitcoin_percentage_of_market_cap'

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

class MarketInfo:

    def __init__(self):

        self.reference = None
        self.current = None
        
        self._market = None
        self._coin = None

        self._market_timestamp = 0
        self._coin_timestamp = 0

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

            old_part = float(self.reference[BITCOIN_PART]) / 100
            new_part = float(self.current[BITCOIN_PART]) / 100

            total_diff = new_cap - old_cap
            percent_change = total_diff / old_cap * 100

            old_bit = old_cap * old_part
            new_bit = new_cap * new_part
            bit_cap_diff = new_bit - old_bit

            old_exclude = old_cap - old_bit
            new_exclude = new_cap - new_bit
            exclude_bit_diff = new_exclude - old_exclude

        return {
            'market_cap_change': total_diff,
            'market_cap_change_no_bitcoin': exclude_bit_diff,
            'market_cap_change_bitcoin': bit_cap_diff,
            'percent_change_24h': percent_change,
            'bitcoin_market_cap': new_bit,
            'market_cap_no_bitcoin': new_exclude
        }

    def get_global_market(self):

        market = None
        now = time.time()

        if now - self._market_timestamp < 150:
            print('Returned cached Market info')
            return self._market

        resp = request_global_market()
        #print(resp.text)

        if resp.status_code == 200:
            market = resp.json()
            self._market = market

        self._market_timestamp = time.time()
        return market

    def get_bitcoin_info(self):

        info = None
        coins = []
        now = time.time()

        if now - self._coin_timestamp < 150:
            print('Returned cached Bitcoin info')
            return self._coin

        resp = request_coin('bitcoin')
        #print(resp.text)

        if resp.status_code == 200:
            coins = resp.json()

        if coins:
            # Add change info
            info = coins[0]
            current_market_cap = float(info['market_cap_usd'])
            percent_change = float(info['percent_change_24h'])

            percent_change = percent_change / 100 + 1
            old_market_cap = current_market_cap / percent_change
            info['change_24h'] = current_market_cap - old_market_cap

            self._coin = info

        self._coin_timestamp = time.time()
        return info

    def changes_text(self):

        market = self.get_global_market()
        change = self.calculate_change()
    
        news  = '*Automated Market Cap Alert:*\n'
        news += '------------------------------\n'

        cap = market['total_market_cap_usd']
        diff = change['market_cap_change']
        sign = "+$" if diff > 0 else "-$"

        news += '*Total Market Cap (Incl. Bitcoin):*\n'
        news += '${:,.2f}\n'.format(float(cap))
        news += '*Change from our last automated alert:*\n'
        news += '{}{:,.2f}\n'.format(sign, abs(float(diff)))
        news += '------------------------------\n'

        cap = change['market_cap_no_bitcoin']
        diff = change['market_cap_change_no_bitcoin']
        sign = "+$" if diff > 0 else "-$"

        news += '*Total Market Cap (Excl. Bitcoin):*\n'
        news += '${:,.2f}\n'.format(float(cap))
        news += '*Change from our last automated alert:*\n'
        news += '{}{:,.2f}\n'.format(sign, abs(float(diff)))
        news += '------------------------------\n'

        cap = change['bitcoin_market_cap']
        diff = change['market_cap_change_bitcoin']
        sign = "+$" if diff > 0 else "-$"

        news += '*Bitcoin Market Cap:*\n'
        news += '${:,.2f}\n'.format(float(cap))
        news += '*Change from our last automated alert:*\n'
        news += '{}{:,.2f}\n'.format(sign, abs(float(diff)))

       # cap = market['total_market_cap_usd']
       # diff = change['market_cap_change']
       # percent_change = change['percent_change_24h']
       # money = "+$" if diff > 0 else "-$"

       # news  = '*Total Market Cap:*\n'
       # news += '${:,.2f}\n'.format(float(cap))
       # news += '--------------------\n'
       # news += 'Change: {}{:,.2f}\n'.format(money, abs(float(diff)))
       # news += '24h Change: {:+.2f}%'.format(float(percent_change))

       # cap = coin['market_cap_usd']
       # diff = coin['change_24h']
       # percent_change = coin['percent_change_24h']
       # money = "+$" if diff > 0 else "-$"

       # news += '\n\n'
       # news += '*Bitcoin Market Cap:*\n'
       # news += '${:,.2f}\n'.format(float(cap))
       # news += '--------------------\n'
       # news += 'Change: {}{:,.2f}\n'.format(money, abs(float(diff)))
       # news += '24h Change: {:+.2f}%'.format(float(percent_change))

        return news

    def status_text(self):

        market = self.get_global_market()
        coin = self.get_bitcoin_info()

        total_cap = market['total_market_cap_usd']
        percent = market['bitcoin_percentage_of_market_cap']
        bitcoin_cap = total_cap * percent / 100
        ex_bitcoin = total_cap - bitcoin_cap

        stat  = '*Manual Market Cap Alert:*\n'
        stat += '------------------------------\n'

        stat += '*Total Market Cap (Incl. Bitcoin):*\n'
        stat += '${:,.2f}\n'.format(float(total_cap))
        stat += '------------------------------\n'

        stat += '*Total Market Cap (Excl. Bitcoin):*\n'
        stat += '${:,.2f}\n'.format(float(ex_bitcoin))
        stat += '------------------------------\n'

        stat += '*Bitcoin Market Cap:*\n'
        stat += '${:,.2f}\n'.format(float(bitcoin_cap))
        stat += '${:,.2f}\n'.format(float(coin['market_cap_usd']))

        return stat


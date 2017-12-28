#!/usr/bin/env python3
import requests as rq
import time
import json

# Coin market cap
# API_URL = 'https://api.coinmarketcap.com/v1/{}/'
API_URL = 'http://coincap.io/global'

def request_global_market():
    url = API_URL.format('global')
    res = rq.get(url, timeout=30)
    return res

def request_all_coins():
    url = API_URL.format('ticker')
    res = rq.get(url, timeout=30)
    return res

class MarketScraper:

    def __init__(self):

        self.ref_market = None
        self.new_market = None

    def scrape_global_market(self, timeout=30):

        attempt = 1
        delay = 60

        while True:

            try:
                self.new_market = get_global_market()

                if self.new_market is None:
                    raise Exception('The global market was None')

                ref_market = self.compare_market()

                print(json.dumps(self.ref_market, indent=2))
                print(json.dumps(self.new_market, indent=2))

                time.sleep(timeout)
                delay = 60

            except Exception as e:
                print(e)
                if attempt > 3:
                    break

                time.sleep(delay)
                attempt += 1
                delay *= 2

            except KeyboardInterrupt:
                break

    # Returns which will be the next reference
    # to the other comparisons
    def compare_market(self):

        if self.ref_market is None:
            return self.new_market

        # oldcap = old['total_market_cap_usd']
        # newcap = new['total_market_cap_usd']
        oldcap = self.ref_market['totalCap']
        newcap = self.new_market['totalCap']

        diff = newcap - oldcap
        percent_change = diff / oldcap

        print('Changed: {:+f}'.format(diff))
        print('24h Change: {:+.2f}'.format(percent_change))

        if abs(diff) > 10000000000:
            print('Changed by 10B!')
            return new_market

        return ref_market

def get_global_market():

    market = None
    resp = request_global_market()

    if resp.status_code == 200:
        market = resp.json()

    return market


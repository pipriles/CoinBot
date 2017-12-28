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

def scrape_global_market(timeout=30):

    ref_market = None
    attempt = 1
    delay = 60

    while True:
        try:
            new_market = get_global_market()

            if new_market is None:
                raise Exception('The global market was None')

            ref_market = compare_market(ref_market, new_market)
            print(json.dumps(ref_market, indent=2))
            print(json.dumps(new_market, indent=2))

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

# Returns what will be the next reference
# to the other comparisons
def compare_market(old, new):

    if old is None:
        return new

    # oldcap = old['total_market_cap_usd']
    # newcap = new['total_market_cap_usd']
    oldcap = old['totalCap']
    newcap = new['totalCap']

    diff = newcap - oldcap
    percent_change = diff / oldcap

    print('Changed: {:+f}'.format(diff))
    print('24h Change: {:+.2f}'.format(percent_change))

    if abs(diff) > 10000000000:
        print('Changed by 10B!')
        return new

    return old

def get_global_market():

    market = None
    resp = request_global_market()

    if resp.status_code == 200:
        market = resp.json()

    return market


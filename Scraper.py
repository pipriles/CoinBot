#!/usr/bin/env python3
import threading
import json

import Market as mkt

class MarketScraper(threading.Thread):

    def __init__(self, bot, timeout=30):

        threading.Thread.__init__(self)

        self.event = threading.Event()
        self.bot = bot
        self.timeout = timeout

    def run(self):

        attempt = 1
        delay = 60

        while not self.event.is_set():

            try:
                fetch_market_changes(self.bot)
                self.event.wait(self.timeout)
                delay = 60

            except Exception as e:
                print(e)
                if attempt > 3:
                    break

                self.event.wait(delay)
                attempt += 1
                delay *= 2

            # This is not needed...
            except KeyboardInterrupt:
                break

def fetch_market_changes(bot):

    bot.market.current = mkt.get_global_market()

    if bot.market.current is None:
        raise Exception('The current global market was None')

    if bot.market.reference is None:
        bot.market.reference = bot.market.current

    result = bot.market.compare_market()

    if result:
        print('News About Jesus!', bot.chats)
        news = changes_text(bot.market)
        bot.broadcast({ 'text': news })

        bot.market.reference = bot.market.current

def changes_text(market):

    total = market.calculate_change()
    coin = mkt.get_bitcoin_info()

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


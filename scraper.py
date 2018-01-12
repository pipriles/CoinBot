#!/usr/bin/env python3.6
import threading
import json

import market as mkt

class MarketScraper(threading.Thread):

    def __init__(self, bot, timeout=300):

        threading.Thread.__init__(self)

        self.event = threading.Event()
        self.bot = bot
        self.timeout = timeout

    def run(self):

        while not self.event.is_set():

            try:
                fetch_market_changes(self.bot)
                self.event.wait(self.timeout)

            except Exception as e:
                print(e)
                self.event.wait(600)

            # This is not needed...
            except KeyboardInterrupt:
                break

    def stop(self):
        # End thread
        self.event.set()
        self.join()


def fetch_market_changes(bot):

    bot.market.current = bot.market.get_global_market()

    if bot.market.current is None:
        raise Exception('The current global market was None')

    if bot.market.reference is None:
        bot.market.reference = bot.market.current

    result = bot.market.compare_market()

    if result:

        print('News About Jesus!')
        news = bot.market.changes_text()
        bot.broadcast({ 
            'text': news,
            'parse_mode': 'markdown'
        })

        bot.market.reference = bot.market.current


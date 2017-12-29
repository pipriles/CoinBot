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
                raise e
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

    # print(json.dumps(bot.market.reference, indent=2))
    # print(json.dumps(bot.market.current, indent=2))

    if result:
        # Notify change to coin bot
        # I don't like how this looks...
        print('News About Jesus!', bot.chats)
        msg = { 'text': bot.market.market_change_text() }
        bot.broadcast(msg)
        bot.market.reference = bot.market.current


#!/usr/bin/env python3

import requests as rq
import time
import json
import re
import os

import threading
import queue

import utils 
import scraper as sp
import market as mkt

API_URL = 'https://api.telegram.org/bot{}/{}'
JOKE_API = 'https://icanhazdadjoke.com/'

# This bot will save the state of the market to have
# a reference when comparing to the future values...
# This reference can be consulted.
# So the scrape script will only fetch the data to
# populate the market data which would be given by 
# the telegram bot.

# Read admins from somewhere
# Change _subscribed to chats

class TelegramBot:

    def __init__(self, token, admins=None, market=None):

        self.token = token
        self.admins = set() if admins is None else set(admins)

        self.offset  = 0
        self.timeout = 10
        self.read_latency = 2

        # Should be moved to other site
        if market is None:
            self.market = mkt.MarketInfo()

        self._broadcasters = {}
        self._peasants = {}
        self._subscribed = {}

        # Threading
        # Uncomment for multithreading
        # self.reply_thread = threading.Thread(
        #         target=self._reply_message)

        # self.updates = queue.Queue()

    def get_bot_info(self):

        url = API_URL.format(self.token, 'getMe')
        res = rq.get(url)
        return res

    def get_updates(self, offset=None, timeout=None):

        if not offset:
            offset = self.offset

        if not timeout:
            timeout = self.timeout

        url = API_URL.format(self.token, 'getUpdates')
        dat = { 'offset': offset, 'timeout': timeout }

        # Timeout + read_latency
        resp = rq.post(url, data=dat, 
                timeout=timeout+self.read_latency)

        if resp.status_code != 200:
            resp = { 'result': [] }

        return resp

    def send_message(self, msg):

        url = API_URL.format(self.token, 'sendMessage')
        res = rq.post(url, data=msg) # Send invitation
        return res

    def start_polling(self):

        # Uncomment for multithreading
        # self.reply_thread.start()

        while True: 
            # Long polling strategy
            try:
                self._knock_knock()

            # except rq.ReadTimeout:
            except Exception as e:
                print(e)
                time.sleep(10)

        # Add for multithreading
        # finally:
        #     self.end_polling()

    def _knock_knock(self):

        updates = []
        print('Fetching data...')

        resp = self.get_updates()
        updates = resp.json()['result']

        start = time.time()

        # How much does this takes?
        for msg in updates:
            # Put message in threading queue
            # Uncomment for multithreading
            # self.updates.put(msg)

            # It is now multithreading so this
            # was moved
            self._process_update(msg)

        if updates:
            self.offset = updates[-1]['update_id'] + 1 

        print(time.time() - start)

    def edit_message_reply_markup(self, msg):

        url = API_URL.format(self.token, 'editMessageReplyMarkup')
        res = rq.post(url, data=msg)
        return res

    def answer_callback_query(self, args):

        url = API_URL.format(self.token, 'answerCallbackQuery')
        res = rq.post(url, data=args)
        return res

    def store_chat(self, chat):

        # Add timestamp to chat
        chat['timestamp'] = int(time.time())

        _id = str(chat.get('id'))
        self._subscribed[_id] = chat

    def forget_chat(self, chat):

        try:
            _id = str(chat.get('id'))
            del self._subscribed[_id]
        except KeyError:
            pass

    def add_admin(self, user_id):

        user_id = str(user_id)
        self.admins.add(user_id)

    def broadcast(self, message):

        for chat in self._subscribed:
            result = { 'chat_id': chat }
            result.update(message)
            self.send_message(result)

    def get_chat(self, chat_id):

        url = API_URL.format(self.token, 'getChat')
        res = rq.post(url, data={ 'chat_id': chat_id })
        return res

    ##############################
    # Just for multithreading    #
    # This is not useful for now #
    ##############################

    def _reply_message(self):

        while True:
            msg = self.updates.get()
            if msg is None:
                break

            self._process_update(msg)
            self.updates.task_done()

    # Just for multithreading
    def end_polling(self):

        self.updates.join()
        self.updates.put(None)
        self.reply_thread.join()


    ##################################
    # From here can be another class #
    # for better scalability         #
    ##################################

    def _process_update(self, update):

        print(json.dumps(update, indent=2))

        if 'message' in update:
            self._process_message(update)

        elif 'callback_query' in update:
            self._process_callback_query(update)

    def _process_message(self, update):

        msg = update['message']
        exclude = []

        if 'text' not in msg \
        or 'from' not in msg:
            return

        text = msg['text']

        if re.fullmatch(r'/start(@\w+)?', text):
            resp = self._ask_for_nudes(msg)

        elif re.fullmatch(r'/market(@\w+)?', text):
            resp = self._reply_market_info(msg)

        elif re.fullmatch(r'/jellybeans(@\w+)?', text):
            resp = self._tell_bad_joke(msg)

        # Both these expect a user response
        elif re.fullmatch(r'/admin(@\w+)?', text):
            resp = self._ask_for_secret(msg)
            exclude.append('admin')

        elif re.fullmatch(r'/broadcast(@\w+)?', text):
            self._expect_broadcast(msg)
            exclude.append('broadcast')

        elif re.fullmatch(r'/users(@\w+)?', text):
            self._users_subscribed(msg)

        # elif re.fullmatch(r'/change(@\w+)?', text):
        #     self._reply_last_changes(msg)
        
        else:
            self._check_admin_secret(msg)
            self._check_broadcast_reply(msg)

        self._reset_state(msg['chat']['id'], exclude)
        
    def _process_callback_query(self, update):

        query = update['callback_query']
        message = query['message']

        reply = { 'callback_query_id': query['id'] }
        chat = message.get('chat')

        if query['data'] == 'True':
            self.store_chat(chat)
            reply['text'] = 'Now you will receive automated updates.'
            
        else:
            self.forget_chat(chat)
            reply['text'] = 'You will not receive more updates.'

        self.answer_callback_query(reply)
        # self.send_message(reply)

    def _reset_state(self, chat_id, exclude=[]):

        if 'admin' not in exclude:
            self._peasants.pop(chat_id, None)

        if 'broadcast' not in exclude:
            self._broadcasters.pop(chat_id, None)
        
    def _check_broadcast_reply(self, msg):

        chat = msg['chat']['id']
        user = msg['from']['id']
        text = msg['text']

        if chat not in self._broadcasters:
            return
        
        if user != self._broadcasters[chat]:
            return

        del self._broadcasters[chat]
        self.broadcast({ 'text': text })

    def _check_admin_secret(self, msg):

        chat = msg['chat']['id']
        user = msg['from']['id']

        if chat not in self._peasants:
            return
        
        if user != self._peasants[chat]:
            return

        # Validate if it is not str
        if msg['text'].lower() == 'yes i do boss':
            self.add_admin(user)
            reply = 'Now you are a superior being'
        else:
            reply = 'You are not ready'

        del self._peasants[chat]
        self.send_message({ 'chat_id': chat, 'text': reply })

    def _users_subscribed(self, msg):

        user = msg['from']['id']
        chat = msg['chat']['id']

        count = len(self._subscribed)
        reply = 'User subscribed: *{}*'
        reply = reply.format(count)

        utils.export_chats(self._subscribed)

        self.send_message({ 
            'chat_id': chat, 
            'text': reply,
            'parse_mode': 'markdown'
        })

    def _expect_broadcast(self, msg):

        user = msg['from']['id']
        chat = msg['chat']['id']

        # Validate if user is admin
        if str(user) in self.admins:
            self._broadcasters[chat] = user
            reply = 'What would you like to say to everyone?' 
        else:
            reply = "I can't let you do that"

        self.send_message({ 'chat_id': chat, 'text': reply })

    def _ask_for_secret(self, msg):

        user = msg['from']['id']
        chat = msg['chat']['id']

        if str(user) in self.admins:
            reply = 'You are already a superior being.'
        else:
            reply = 'Do you have what is needed?'
            self._peasants[chat] = user

        self.send_message({ 'chat_id': chat, 'text': reply })

    def _ask_for_nudes(self, msg):

        chat_id = msg['chat']['id']
        question  = 'Would you like to receive automated updates'
        question += ' when the cryptocurrency market cap changes?'

        accept = { 'text': 'Yes', 'callback_data': 'True'  }
        cancel = { 'text': 'No' , 'callback_data': 'False' }
        markup = { 'inline_keyboard': [[ accept, cancel ]] }

        return self.send_message({
            'chat_id': chat_id,
            'text': question,
            'reply_markup': json.dumps(markup)
        })

    def _reply_market_info(self, msg):
        
        try:
            text = self.market.status_text()
        except Exception as e:
            print(e)
            text = 'Ups... There was an error.'

        reply = {}
        reply['chat_id'] = msg['chat']['id']
        reply['parse_mode'] = 'Markdown'
        reply['text'] = text

        return self.send_message(reply)

    def _reply_last_changes(self, msg):

        reply = { 'chat_id': msg['chat']['id'] }

        try:
            reply['text'] = self.market.changes_text()

        except Exception as e:
            print(e)
            reply['text'] = 'Try again later...'

        self.send_message(reply)

    def _tell_bad_joke(self, msg):

        reply = { 'chat_id': msg['chat']['id'] }

        try:
            headers = { 'Accept': 'application/json' }
            resp = rq.get(JOKE_API, headers=headers)
            parsed = resp.json()
            reply['text'] = parsed['joke']

        except Exception as e:
            print(e)
            reply['text'] = 'Ups...'

        return self.send_message(reply)

    def export_chats(self):
        utils.export_chats(self._subscribed)

    def restore_chats(self):
        self._subscribed = utils.import_chats()

def bot_factory():

    token = os.environ.get('TOKEN')

    if token is None:
        raise Exception('You have to provide a token')

    bot = TelegramBot(token)
    bot.restore_chats()

    return bot

def main():

    bot = None
    scraper = None

    try:
        # Initiate telegram bot and scraper thread
        bot = bot_factory()
        scraper = sp.MarketScraper(bot)

        # Start scraper and bot
        scraper.start()
        bot.start_polling()

    except KeyboardInterrupt:
        pass

    finally:
        if bot: bot.export_chats()
        if scraper: scraper.stop()

if __name__ == '__main__':
    main()


#!/usr/bin/env python3
import requests as rq
import json

API_URL = 'https://api.telegram.org/bot{}/{}'
CHATS_PATH = 'chats.txt'

class TelegramBot:

    def __init__(self, token, chats=[]):

        self.token = token
        self.chats = []

        self.offset  = 0
        self.timeout = 10
        self.read_latency = 2

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

        return resp

    def send_message(self, msg):

        url = API_URL.format(self.token, 'sendMessage')
        res = rq.post(url, data=msg) # Send invitation
        return res

    def start_polling(self):

        # Long polling strategy
        while True: 
            self._knock_knock()

    def _knock_knock(self):

        print('Fetching data...')
        resp = self.get_updates()
        updates = resp.json()['result']

        # Pretty print
        print(json.dumps(updates, indent=2))

        for msg in updates:
            self._process_update(msg)

        if updates:
            self.offset = updates[-1]['update_id'] + 1 

    def _process_update(self, update):

        if 'message' in update:
            self._process_message(update)

        elif 'callback_query' in update:
            self._process_callback_query(update)

    def _process_message(self, update):

        msg = update['message']

        if msg['text'] != '/start': 
            return 
        
        reply = _prepare_notify_request(msg)
        resp = self.send_message(reply)

        parsed = resp.json()
        print(json.dumps(parsed, indent=2))

    def _process_callback_query(self, update):

        query = update['callback_query']
        message = query['message']

        reply = {}
        reply['chat_id'] = message['chat']['id']

        if query['data'] == 'True':
            self.store_chat(reply['chat_id'])
            reply['text'] = 'Now you will receive news about Jesus.' 
        else:
            self.forget_chat(reply['chat_id'])
            reply['text'] = 'Now Jesus will forget you.'

        self.send_message(reply)

        # reply['message_id'] = message['message_id']
        # self.edit_message_reply_markup(reply)

    def edit_message_reply_markup(self, msg):

        url = API_URL.format(self.token, 'editMessageReplyMarkup')
        res = rq.post(url, data=msg)
        return res

    def store_chat(self, chat_id):

        chat = str(chat_id)
        self.chats.append(chat)

    def forget_chat(self, chat_id):

        chat = str(chat_id)
        try:
            self.chats.remove(chat)
        except ValueError:
            pass

# Utils
def read_stored_chats():
    with open(CHATS_PATH, 'w+') as f:
        chats = f.read().splitlines()
    return chats

def write_stored_chats(chats):
    with open(CHATS_PATH, 'w') as f:
        f.writelines(chats)

# Prepare notify invitation
def _prepare_notify_request(msg):
    dat = {}
    dat['chat_id'] = msg['chat']['id'] 
    dat['text'] = 'Would you like to receive news about Jesus?' 
    dat['reply_markup'] = json.dumps({ 
        'inline_keyboard': [[
            { 'text': 'Yep' , 'callback_data': 'True' }, 
            { 'text': 'Nope', 'callback_data': 'False' }
        ]]
    })

    return dat

if __name__ == '__main__':

    # Enter some token from input
    token = input()
    print('Token entered:', token)

    chats = read_stored_chats()

    try:
        bot = TelegramBot(token, chats)
        bot.start_polling()

    except KeyboardInterrupt:
        pass

    finally:
        write_stored_chats(bot.chats)
    

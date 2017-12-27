#!/usr/bin/env python3
import requests as rq
import json

API_URL = 'https://api.telegram.org/bot{}/{}'

def get_bot_info(token):
    url = API_URL.format(token, 'getMe')
    res = rq.get(url)
    return res

def get_updates(token, offset=0, timeout=10):
    url = API_URL.format(token, 'getUpdates')
    dat = { 'offset': offset, 'timeout': timeout }

    # Timeout + read_latency
    resp = rq.post(url, data=dat, timeout=timeout+2)
    return resp

def long_poll(token):
    offset = 0
    timeout = 10

    while True: 
        print('Fetching data...')
        resp = get_updates(token, offset, timeout)
        updates = resp.json()['result']

        # Pretty print
        print(json.dumps(updates, indent=2))

        for msg in updates:
            process_update(token, msg)

        if updates:
            offset = updates[-1]['update_id'] + 1 

def process_update(token, update):
    if 'message' in update:
        process_message(token, update)

    elif 'callback_query' in update:
        process_callback_query(token, update)

def process_message(token, update):
    msg = update['message']

    if msg['text'] != '/start':
        return False
    
    url = API_URL.format(token, 'sendMessage')
    dat = prepare_notify_request(msg)
    res = rq.post(url, data=dat) # Send invitation

    parsed = res.json()
    print(json.dumps(parsed, indent=2))

def process_callback_query(token, update):
    query = update['callback_query']

    if query['data'] == 'True':
        print('Stored chat in txt') # Store chat in txt
    else:
        print('Bad boy')

def prepare_notify_request(msg):
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

    try:
        long_poll(token)
    except BaseException as e:
        print(e)


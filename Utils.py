#!/usr/bin/env python3

CHATS_PATH = 'chats.txt'

def read_stored_chats():
    with open(CHATS_PATH, 'w+') as f:
        chats = f.read().splitlines()
    return chats

def write_stored_chats(chats):
    with open(CHATS_PATH, 'w') as f:
        f.writelines(chats)

def input_token():
    # Enter some token from input
    token = input()
    print('Token entered:', token)
    return token


#!/usr/bin/env python3.6
import os

CHATS_PATH = 'chats.txt'

def read_stored_chats():

    if not os.path.exists(CHATS_PATH):
        write_stored_chats([])

    with open(CHATS_PATH, 'r') as f:
        chats = f.read().splitlines()

    return chats

def write_stored_chats(chats):

    with open(CHATS_PATH, 'w') as f:
        f.write("\n".join(chats))

def input_token():
    # Enter some token from input
    token = input()
    print('Token entered:', token)
    return token


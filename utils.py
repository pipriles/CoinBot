#!/usr/bin/env python3.6
import os
import csv

CHATS_PATH = 'chats.txt'
CHATS_CSV = 'chats.csv'

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

def export_chats(chats: dict):

    with open('chats.csv', 'w') as f:
        fields = ['id', 'type', 'title', 'first_name', 
                  'last_name', 'username' ]
        writer = csv.DictWriter(f, fieldnames=fields, 
                extrasaction='ignore')

        # writer.writeheader()
        writer.writerows(chats.values())

def import_chats():

    if not os.path.exists(CHATS_CSV):
        return {}

    chats = {}
    with open('chats.csv', 'r') as f:
        fields = ['id', 'type', 'title', 'first_name', 
                  'last_name', 'username']
        reader = csv.DictReader(f, fieldnames=fields)
        chats = { row['id']: row for row in reader }

    return chats


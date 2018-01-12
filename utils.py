#!/usr/bin/env python3.6
import os
import csv

CHATS_PATH = 'chats.csv'

def export_chats(chats: dict):

    with open(CHATS_PATH, 'w') as f:
        fields = ['id', 'type', 'title', 'first_name', 
                  'last_name', 'username', 'timestamp']
        writer = csv.DictWriter(f, fieldnames=fields, 
                extrasaction='ignore')

        # writer.writeheader()
        writer.writerows(chats.values())

def import_chats():

    if not os.path.exists(CHATS_PATH):
        return {}

    chats = {}
    with open('chats.csv', 'r') as f:
        fields = ['id', 'type', 'title', 'first_name', 
                  'last_name', 'username', 'timestamp']
        reader = csv.DictReader(f, fieldnames=fields)
        chats = { row['id']: row for row in reader }

    return chats


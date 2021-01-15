import socket
import base64
import time
import os
import json
from random import choice



def create_socket():
    server_domains = json.loads(os.getenv('server_choices'))
    domain = choice(server_domains)
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # game = choice(GAME2, GAME3)
            s.connect((domain,9310))
            return s
        except:
            continue


def encode(msg):
    encoded_msg = b"<m>" + base64.b64encode(msg) + b"</m>\x00"
    return encoded_msg

def find_btw(payload, before, after, start_skip=0, end_skip=0):
    i = payload.find(before) + len(before) + start_skip
    remain_payload = payload[i:]
    j = remain_payload.find(after) - end_skip
    return remain_payload[:j]

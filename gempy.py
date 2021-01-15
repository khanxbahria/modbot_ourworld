import requests
import re
import base64
from urllib.parse import unquote
import json
import time
import threading
import sys


class GemPY:
    def __init__(self, uid):
        self.uid = str(uid)
        self.gems = 0

    def each_round(self, trampoline, uid):
        if 'step_count' in trampoline:
                wait = trampoline['step_count'] * trampoline['visit_length'] + 2
        else:
            wait = trampoline['video_length'] + 2
        time.sleep(wait)

        requests.post("https://embed.jungroup.com/offer_completion/complete", data = {
                    'token':trampoline['token'],
                    'distributorid':'2777179',
                    'uid':uid,
                    'viewing_id':trampoline['viewing_id'],
                    'reward_token':trampoline['reward_token']
                    })
        self.gems += int(trampoline['reward_quantity'])


    def get_gems_each(self, uid):

        url='https://securityheaders.com/?q=http%3A%2F%2Fembed.jungroup.com%2Fembedded_videos%2Fcatalog_frame%3Fuid%3D' + uid + '%26site%3DOurWorld-Special%26pid%3D2777179&followRedirects=on'

        while True:
            response = requests.get(url)
            try:
                trampoline = re.search('trampoline=(.+?)&amp', str(response.text)).group(1)
                trampoline = json.loads(base64.b64decode(str(unquote(trampoline))).decode('utf-8'))
            except:
                break
            else:
                self.each_round(trampoline, uid=uid)


    def get_gems(self):
        p1 = threading.Thread(target=self.get_gems_each, args=(self.uid,))
        p1.start()
        time.sleep(2)
        uid2 = "0" + self.uid
        p2 = threading.Thread(target=self.get_gems_each, args=(uid2,))
        p2.start()
        p1.join()
        p2.join()

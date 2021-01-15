import time
import requests
import json
from hashlib import sha1
from random import randint



class Account:
    '''A class to manage account.'''

    def __init__(self, email, pwd):
        '''Initialise attributes.'''
        self.email = email
        self.pwd = pwd
        self.uid = None
        self.auth_id = None
        self.uid_hex = None


    def login(self):
        '''sends login request and returns uid and loginid.'''
        data = {
        'email': self.email,
        'locale': 'en',
        'platform': '0',
        'password': sha1(self.pwd.encode()).hexdigest(),
        'env': 'home'}

        headers = {'Cookie': f'evercookie={randint(1000000,99999999)};'}
        while True:
            try:
                r = requests.post('http://www.ourworld.com/ow/login', data=data, headers=headers)
                resp = r.json()
                self.uid = int(resp['userid'])
                self.auth_id = resp['loginid']
            except:
                print("Login retry attempt.", resp, self.email)
                time.sleep(10)
            else:
                break
        print(self.email, "logged in")
        self.uid_hex = self.uid.to_bytes(4, byteorder='big')

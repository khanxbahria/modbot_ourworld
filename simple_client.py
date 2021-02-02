import time
import re
import requests
import random

from base_client import BaseClient
from common import encode, find_btw


class SimpleClient(BaseClient):
    '''Manages payloads related to user lookup.'''

    def __init__(self, email, pwd):
        super().__init__(email, pwd)

        self.users_searched = {}
        self.uids_searched = []
        self.users_locations = []
        

    def restart(self):
        super().restart()
        self.users_searched = {}
        self.uids_searched = []
        self.users_locations = []



    def parse_msg(self, msg):
        # print(f"\n\n----------\n{msg}\n-------------\n\n")

        if len(msg) > 21 and msg[11:21] == b'\x00\x9a\x00\x03\x0cv\x00\x00\x00\x00':
            username_len = msg[30]
            username = msg[31:31+username_len].decode()
            self.users_searched[username] = None
        elif len(msg) > 17 and msg[8:17] == b'\xe7\x00\x00\x00\x9a\xff\xfd\x0cv':
            i = msg.find(b'\x00\x00\x00\x00\x19<\x00') + 7
            username_len = msg[i]
            username = msg[i+1:i+1+username_len].decode()
            uid_hex = msg[23:27]
            uid = int.from_bytes(uid_hex, 'big')
            self.users_searched[username] = uid

        # if len(msg) > 245 and msg[4:17] == b"\x01\x00\x00\x00X\x00\x08\x00\x96\xff\xfc\x0cv":
        elif len(msg) > 245 and b"\xc6\x00\x00" in msg:
            try:
                u = UserProfInfo(msg)
                self.uids_searched.append(u)
            except Exception as e:
                print("Error parsing userprofinfo", e)

        elif len(msg) > 42 and b'\x0cP\x00\x00\x00\x00\rP\x00\x00\x00\x00\x18\x15\x00\x00\x10G\x017\xb8' in msg or (b'game' in msg and b'\x0cP' in msg):
            loc_dict = {}
            located_uid_hex = find_btw(msg, b'\x0c[',b'\x11{')
            loc_dict['located_uid'] = int.from_bytes(located_uid_hex,'big')
            loc_dict['area'] = find_btw(msg, b'\x18\x8d',b'\x18\r', start_skip=2).decode()
            if b'condo' in msg:
                if not (b'game' in msg):
                    loc_dict['condo_owner_uid'] = int.from_bytes(msg[17:21],'big')
                else:
                    ownder_uid_hex = find_btw(msg, b'\x0c\x90',b'\x0cP')
                    loc_dict['condo_owner_uid'] = int.from_bytes(ownder_uid_hex,'big')

            self.users_locations.append(loc_dict)




        # if b"ooie" in msg or b"Ooie" in msg or b"doxed" in msg or b"Doxed" in msg:


    def get_uid(self, username):
        msg = b'\x01\x00\x00\x00\xe7\x00\x00\x00\x9a\x00\x01\x18\r' + (len(username)).to_bytes(2,"big") + username.encode()
        msg = (len(msg)).to_bytes(4,"big") + msg
        try:
            self.second_sock.sendall(encode(msg))
        except:
            return
        timeout = time.time() + 20
        while time.time() < timeout:
            for searched_user, uid in self.users_searched.items():
                if username.lower() == searched_user.lower():
                    del self.users_searched[searched_user]
                    return searched_user, uid
            time.sleep(0.1)
        # self.restart()

    def get_prof(self, uid):
        uid_hex = uid.to_bytes(4,"big")
        msg = b"\x01\x00\x00\x00X\x00\x08\x00\x96\x00\x03\x10\x08\x00\x0c[" + uid_hex + b"\x0c\x14\x00\x00\x00\x08"
        msg = (len(msg)).to_bytes(4,"big") + msg
        try:
            self.second_sock.sendall(encode(msg))
        except:
            print("error sending get_prof")
            return
        timeout = time.time() + 20
        while time.time() < timeout:
            for user_prof in self.uids_searched:
                if user_prof.uid == uid:
                    self.uids_searched.remove(user_prof)
                    return user_prof
            time.sleep(1)

    def get_location(self, uid):
        uid_hex = uid.to_bytes(4,"big")

        # TODO change to locate msg
        msg = b'\x00\x00\x00\x11\x01\x00\x00\x00\xd8\x00\x00\x00u\x00\x01\x0c[' + uid_hex
        try:
            self.second_sock.sendall(encode(msg))
        except:
            print("error sending get_location")
            return
        timeout = time.time() + 10
        while time.time() < timeout:
            for loc_dict in self.users_locations:
                if loc_dict['located_uid'] == uid:
                    self.users_locations.remove(loc_dict)
                    return loc_dict
            time.sleep(1)




class UserProfInfo:
    def __init__(self, payload):
        self.payload = payload
        # print(f"-------\n{payload}\n-------------\n\n")
        self.uid = self.get_uid()
        self.username = self.get_username()

    def coins(self):
        ident=b"\xc6\x00\x00"
        ident_i = self.payload.find(ident)
        coins = self.payload[ident_i+7:][:4]
        coins = int.from_bytes(coins, 'big')

        return coins

    def bio(self):
        try:
            bio = self.find_btw(b"\x19=", b">\x00\x00", start_skip=2)
            bio = bio.replace(b'\r', b'\n').decode().strip()
        except:
            bio = " "
        return bio

    def get_uid(self):
        uid = self.find_btw(b"user", b"\x00")[:-2]
        uid = int(uid.decode())
        return uid

    def get_username(self):
        username = self.find_btw(b"\x19<\x00", b"\x19=", start_skip=1).decode()
        return username

    def img_url(self, part='body.png'):
        path = re.search(b"\x00\x19L.+\x0eO\x00", self.payload).group(0)[5:-3].decode()
        url = f"http://s3e-main.ourworld.com/shared/{path}/{part}?v={random.randint(10000,99999)}"
        return url

    def last_active(self):
        url = self.img_url('head2.png')
        try:
            last_mod = requests.get(url).headers['Last-Modified']
        except:
            try:
                last_mod = requests.get(self.img_url('head.png')).headers['Last-Modified']
            except: return "Null"
        parts = last_mod.split()
        parts[3] = parts[3]+"\n"
        return " ".join(parts)

    def find_btw(self,*args, **kwargs):
        return find_btw(self.payload,*args,**kwargs)
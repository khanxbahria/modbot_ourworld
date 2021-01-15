import threading
import time
import re
import base64
import os


from account import Account
from common import create_socket, encode


class BaseClient:
    '''Logs in to game and keeps the connection alive.
       Subclass this. '''

    def __init__(self, email, pwd):
        '''Log in and send initial payloads.'''

        self.email = email
        self.pwd = pwd
        self.account = Account(email, pwd)
        self.account.login()

        self.second_sock = None
        self.throw_sock = None
        self._initialise()
        threading.Thread(target=self.keep_alive, daemon=True).start()




    def _initialise(self):
        while True:
            try:
                policy_sock = create_socket()
                policy_sock.sendall(b'<policy-file-request/>\x00')
                policy_sock.close()

                second_sock = create_socket()
                msgs = [encode(b'\x00\x00\x00\x89\x01\x00\x00\x00\x02\x00\x00\x00=\x00\x0c\x1a\xe1\x00\x12game2.ourworld.com\x0cB\x00\x00\x00\x05\x18E\x00\x04info\x18\xc6\x00\x04home\x0e\xe2\x00\x00$^\x0fk\x00\x00\x00\x006\x8c\x15f9a\x00\x00\x01q\x10N\x01\x18Z\x00 '+self.account.auth_id.encode()+b'\x18<\x00\x04info\x18]\x00\x03xyz\x0c>\xff\xff\xff\xff'), b"<m>AAAAEQEAAAADAAAA6AABGhEAAmVu</m>\x00", b"<m>AAAAEQEAAAAEAAgA9wABDBQAAAAI</m>\x00", b"<m>AAAADQEAAAAFAAAA4AAAAAA=</m>\x00", encode(b'\x00\x00\x00\x17\x01\x00\x00\x00\x06\x00\x08\x00U\x00\x02\x0c\x14\x00\x00\x00\x08\x0c['+self.account.uid_hex),b'<m>AAAAFwEAAAAHAAABJgACDgAAAAABDNIAAAAC</m>\x00']
                for msg in msgs:
                    second_sock.sendall(msg)
                threading.Thread(target=self.receiver, args=(second_sock,), daemon=True).start()

                throw_sock = create_socket()
                throw_sock.sendall(encode(b'\x00\x00\x00\xbb\x01\x00\x00\x00\t\x00\x00\x00=\xff\xf5\x1a\xe1\x00\x12game2.ourworld.com\x0cB\x00\x00\x00\x04\x0e\xe2\x00\x00$^\x18<\x00\x04town\x18E\x00\x1aarcadia-boardwalk-exterior\x18\xc6\x00\x04home\x18Z\x00 '+self.account.auth_id.encode()+b'\x0fk\x00\x00\x00\x006\x8c\x15f9a\x00\x00\x01q\x18\xcd\x00\x1aarcadia-boardwalk-exterior\x0c\x1e\x00\x00\x00\x00\x00\x01\x00C\x00\x00\x00\x00'))
                threading.Thread(target=self.receiver, args=(throw_sock,), daemon=True).start()
                msgs = [(b"<m>AAAAEQEAAAAKAAwBGwABDBQAAAAM</m>\x00", 2), (b"<m>AAAAMwEAAAALAAAABgADDEAAAAI2GDwADGNvbm5lY3QgdGltZRgVAA5Xb3JsZDogQ29ubmVjdA==</m>\x00", 1), (b"<m>AAAAIwEAAAANAAgAD//+DBQAAAAIDGEAAAACAAEAZAABDD4ALcyf</m>\x00", 2), (b"<m>AAAAFwEAAAAMAAAAegADCBgAAAgWAPsIFwN6</m>\x00", 1), (b"<m>AAAADQEAAAAOAAAAugAAAAA=</m>\x00", 2), (b"<m>AAAADQEAAAAPAAAAlwAAAAA=</m>\x00", 1), (b"<m>AAAADQEAAAAQAAAA9wAAAAA=</m>\x00", 1), (b"<m>AAAAHQEAAAARAAAAUgACGGEACGxvY2F0aW9uDFsAAXcB</m>\x00", 1), (encode(b'\x00\x00\x00\x1d\x01\x00\x00\x00\x13\x00\x00\x00R\x00\x02\x18a\x00\x08location\x0c[' + self.account.uid_hex), 1), (b"<m>AAAAEQEAAAAWAAgABQABDBQAAAAI</m>\x00", 2), (encode(b'\x00\x00\x00\x1e\x01\x00\x00\x00\x14\x00\x00\x00\x04\x00\x03\x0c['+self.account.uid_hex+b'\x18\x15\x00\x06helper\x10v\x00'), 1), (b'<m>AAAAIwEAAAAXAAgAD//+DBQAAAAIDGEAAAACAAEAZAABDD4AHvYq</m>\x00', 2), (b"<m>AAAADQEAAAAVAAAAnwAAAAA=</m>\x00", 1), (b"<m>AAAAEQEAAAAfAAAAoQABDD4AAAGI</m>\x00", 1), (b"<m>AAAADQEAAAAZAAABCQAAAAA=</m>\x00", 2), (b"<m>AAAAFwEAAAAaAAABJwACDDwAAAABDEQAAAAJ</m>\x00", 2), (b"<m>AAAADQEAAAAbAAABGwAAAAA=</m>\x00", 2), (b"<m>AAAADQEAAAAcAAABDQAAAAA=</m>\x00", 2), (encode(b'\x00\x00\x00\x11\x01\x00\x00\x00\x1d\x00\x00\x00\xfa\x00\x01\x0c[' + self.account.uid_hex), 2)]
                for msg, sock_num in msgs:
                    if sock_num == 1:
                        throw_sock.sendall(msg)
                    else:
                        second_sock.sendall(msg)


                msg = encode(b'\x00\x00\x00m\x01\x00\x00\x00\xf2\x00\x00\x00>\xff\xf8\x1a\xe1\x00\x12game2.ourworld.com\x0cB\x00\x00\x00\x04\x18E\x00\rcondos/condo1\x18\xc6\x00\x04home\x0e\xe2\x00\x00$^\x18<\x00\x04town\x18\xcd\x00\rcondos/condo1\x0c\x1e'+self.account.uid_hex+b'\x00\x01\x00C\x00\x00\x00\x00')
                throw_sock.sendall(msg)
                throw_sock.sendall(msg)
                time.sleep(2)
                self.throw_sock = throw_sock
                self.second_sock = second_sock
            except:
                continue
            else:
                break
    def restart(self):
        try:
            self.throw_sock.close()
            self.second_sock.close()
        except: return
        self.throw_sock = None
        self.second_sock = None
        self.account.login()
        self._initialise()
        threading.Thread(target=self.keep_alive, daemon=True).start()
        print("Restarted")

    def keep_alive(self):
        while True:
            try:
                self.throw_sock.sendall(b'<m>AAAADQEAAABpAAAARAAAAAA=</m>\x00')
                self.second_sock.sendall(b'<m>AAAADQEAAAKlAAABHwAAAAA=</m>\x00')
                self.second_sock.sendall(b'<m>AAAAEQEAAABqAAAARAABDCkAAeMB</m>\x00')
                time.sleep(2)
            except:
                #print(e)
                break
        self.restart()


    def receiver(self, sock):
        last_part = b''
        while True:
            try:
                buff = sock.recv(4096)
            except:
                break
            if buff == b'':
                break
        # if sock == self.second_sock:
            last_part = self._split_msgs(buff, last_part)



    def _split_msgs(self, packet, last_part):
        msgs = packet.split(b'\x00')
        msgs[0] = last_part+msgs[0]
        last_part = msgs.pop()
        for msg in msgs:
            try:
                decoded = base64.b64decode(msg[3:-4])
            except: print("error in parse")
            else:
                self.parse_msg(decoded)
        return last_part


    def parse_msg(self, msg):
        """Subclass this class and implement this method"""
        pass

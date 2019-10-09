import sys
import socket
import argparse
import select
import mybuf21_pb2 as mybuf
import mybuf22_pb2 as mybuf2
import struct
import signal
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Hash import HMAC
import base64
from Crypto.Util.Padding import pad,unpad

def handler(signum,frame):
    print("Bye",flush=True)
    s.close()
    sys.exit(0)

def read_n_bytes(s,n):
    result = b''
    while n > 0:
        part = s.recv(n)
        if part == '':
            print('error',flush=True)
        result += part
        n = n - len(part)
    return result

def encrypt(message,key):
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key,AES.MODE_CBC,iv)
    data = cipher.encrypt(padding(message))
    data = iv+data
    data = base64.b64encode(data)
    return data

def padding(message):
    #print(message)
    #print(type(message))
    #print(chardet.detect(message))
    msg = str(message,encoding='utf-8')
    #print(msg)
    #print(type(msg))

    blockSize = AES.block_size
    remain = blockSize - len(msg) % blockSize
    msg = msg +remain*chr(remain)
    return msg.encode("utf-8")

def unpadding(message):
    return message[:-ord(message[len(message)-1:])]


def decrypt(message,key):
    blockSize = AES.block_size
    if(len(message)<blockSize):
        return message;
    iv = message[0:blockSize]
    cipher = AES.new(key,AES.MODE_CBC,iv)
    message = unpadding(cipher.decrypt(message[blockSize:]))
    return message


def main():
    #define a parser
    signal.signal(signal.SIGINT, handler)
    parser = argparse.ArgumentParser()
    #define two required argument
    parser.add_argument('-s', '--server', dest='servername', help='the server IP or hostname you want to connect', required=True)
    parser.add_argument('-n', '--nickname', dest='nickname', help='your nickname', required=True)
    parser.add_argument('-p', '--port', dest='port', help='port number', required=True)
    parser.add_argument('-c','--confidentialtykey',dest='confidentialtyKey',help='the confidentiality key you want to use',required=True)
    parser.add_argument('-a','--authenticitykey',dest='authenticityKey',help='the authenticityKey you want to use',required=True)
    args = parser.parse_args()
    hash = SHA256.new()
    hash.update(bytes(args.confidentialtyKey,encoding = "UTF-8"))
    k1 = hash.digest()
    hash.update(bytes(args.authenticityKey,encoding = "UTF-8"))
    k2 = hash.digest()

    global s
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    info = s.connect((args.servername,int(args.port)))
    #print('Connected to server')

    read_handles = [s, sys.stdin]
    msg = mybuf.Pack()
    encryptMsg = mybuf2.Pack()

    while True:
        ready_read, ready_write, ready_error = select.select(read_handles, [], [])
        for connection in ready_read:
            if connection == s:
                #print('connection is from s')
                #print("receive a message")
                data_len_unpacked = connection.recv(8,socket.MSG_WAITALL)
                #print('1')
                if len(data_len_unpacked) == 0:
                    s.close()
                    exit(0)
                data_len = struct.unpack('L',data_len_unpacked)[0]
                #print('2')
                data = read_n_bytes(connection,data_len)
                recv_encrypt_MSG = mybuf2.Pack()
                recv_encrypt_MSG.ParseFromString(data)
                recv_encrypt_message = recv_encrypt_MSG.MSG
                recv_encrypt_mac = recv_encrypt_MSG.MAC

                mac = HMAC.new(k2)
                mac.update(bytes(recv_encrypt_message,encoding="utf-8"))
                if mac.hexdigest() != recv_encrypt_mac:
                    print("Authentication failed",flush=True)
                    print("Authentication failed\n",flush=True)
                    continue

                #print('#cipher test is:',recv_encrypt_message)
                recv_encrypt_message = base64.b64decode(recv_encrypt_message)

                display_msg = decrypt(recv_encrypt_message,k1)
                #print('#data is:',display_msg)
                recv_msg = mybuf.Pack()
                recv_msg.ParseFromString(display_msg)


                print("%s: %s" % (recv_msg.name,recv_msg.msg),flush=True)
            else:
                #print('I am going to send')
                user_input = input()
                if user_input.lower() == 'exit':
                    s.close()
                    exit(0)
                if len(user_input) == 0:
                    continue
                msg.msg = user_input.encode("utf-8")
                msg.name = args.nickname.encode("utf-8")
                data = msg.SerializeToString()
                encryptMsg.MSG = encrypt(data,k1)
                mac = HMAC.new(k2)
                mac.update(bytes(encryptMsg.MSG,encoding="utf-8"))
                encryptMsg.MAC = mac.hexdigest()

                encrypt_data = encryptMsg.SerializeToString()
                #print('#final is:', encrypt_data)
                data_len = struct.pack('L',len(encrypt_data))
                s.sendall(data_len)
                s.sendall(encrypt_data)
                #print('send a message')
                #print('my send is:',user_input)
                #print('the length is :',len(user_input))

if __name__ == '__main__':
    main()

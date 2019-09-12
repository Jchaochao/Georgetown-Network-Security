import sys
import socket
import argparse
import select
import mybuf_pb2 as mybuf
import struct
import signal

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

def main():
    #define a parser
    signal.signal(signal.SIGINT, handler)
    parser = argparse.ArgumentParser()
    #define two required argument
    parser.add_argument('-s', '--server', dest='servername', help='the server IP or hostname you want to connect', required=True)
    parser.add_argument('-n', '--nickname', dest='nickname', help='your nickname', required=True)
    args = parser.parse_args()

    global s
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    info = s.connect((args.servername,9999))

    #print('Connected to server')

    read_handles = [s, sys.stdin]
    msg = mybuf.Pack()
    msg.name = args.nickname



    flag = 1
    while flag:

        ready_read, ready_write, ready_error = select.select(read_handles, [], [])

        for connection in ready_read:
            if connection == s:
                #print('connection is from s')
                #This part was cited from example receiver2.py
                data_len_unpacked = connection.recv(8,socket.MSG_WAITALL)
                #print('1')
                if len(data_len_unpacked) == 0:
                    s.close()
                    flag = 0
                    break
                data_len = struct.unpack('L',data_len_unpacked)[0]
                #print('2')
                data = read_n_bytes(connection,data_len)
                recv_msg = mybuf.Pack()
                recv_msg.ParseFromString(data)
                print("%s: %s" % (recv_msg.name,recv_msg.msg),flush=True)
            else:
                #print('I am going to send')
                user_input = input()
                if len(user_input) == 0:
                    continue
                msg.msg = user_input
                data = msg.SerializeToString()
                data_len = struct.pack('L',len(data))
                s.sendall(data_len)
                s.sendall(data)
                #print('my send is:',user_input)
                #print('the length is :',len(user_input))
                if user_input.lower() == 'exit':
                    s.close()
                    flag = 0
                    break


if __name__ == '__main__':
    main()

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
        result += part
        n = n - len(part)
    return result

def createLink(conn, addr):
	#print('A thread is successfully created, connected to',addr)
	while True:
		data = conn.recv(1024)
		conn.send((data+b'\n'))
		if data:
			print(data)
			if data == 'exit':
				break
	conn.close()

def main():
	#define a parser
	signal.signal(signal.SIGINT, handler)
	parser = argparse.ArgumentParser()
	parser.add_argument('-p', '--port', dest='port', help='port number', required=True)
	args = parser.parse_args()

	#define a socket for listening
	global s
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(('', int(args.port)))
	s.listen(5)

	read_handles = [ s ]
	connected = []

	while True:
		#print('Start a loop - connected list: ',len(connected))
		ready_read, ready_write, ready_error = select.select(read_handles, [], [])
		for connection in ready_read:
			if connection is s:
				#print('---A person just entered the chatroom')
				conn, addr = s.accept()
				#print("connection from", addr)
				read_handles.append(conn)
				connected.append(conn)
			else:
				#print("I received a msg")
				data_len_unpacked = connection.recv(8,socket.MSG_WAITALL)
				#print('the unpacked msg len is',len(data_len_unpacked))
				if len(data_len_unpacked) == 0 :
					read_handles.remove(connection)
					connected.remove(connection)
					connection.close()
					continue
				data_len = struct.unpack('L',data_len_unpacked)[0]
				#print('begin read')
				data = read_n_bytes(connection,data_len)
				#print('read all')
				msg = mybuf.Pack()
				msg.ParseFromString(data)
				#if(len(msg.msg) != 0):
				#	print("%s: %s" % (msg.name,msg.msg),flush=True)
				#print('len of msg is:',len(msg.msg))
				if len(msg.msg) == 0:
					#print('---The msg is empty and I will close the socket')
					read_handles.remove(connection)
					connected.remove(connection)
					connection.close()
				elif msg.msg.lower() == 'exit':
					#print('---The msg is exit, I will send it and close this sock')
					for client in connected:
						if client != connection:
							client.sendall(data_len_unpacked)
							client.sendall(data)
					connected.remove(connection)
					read_handles.remove(connection)
					connection.close()
				else:
					#print('---This is a normal msg, I will broadcast it')
					#print('sent')
					for client in connected:
						if client != connection:
							client.sendall(data_len_unpacked)
							client.sendall(data)

if __name__=='__main__':
    main()

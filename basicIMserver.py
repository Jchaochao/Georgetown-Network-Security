import sys
import socket
import argparse
import select
import threading
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
        result += part
        n = n - len(part)
    return result

def createLink(conn, addr):
	#print('A thread is successfully created, connected to',addr)
	while True:
		print('a')
		data = conn.recv(1024)
		print('b')
		conn.send((data+b'\n'))
		if data:
			print(data)
			if data == 'exit':
				break
	conn.close()
	#print('Thread closed')


def main():
	#define a parser
	signal.signal(signal.SIGINT, handler)
	parser = argparse.ArgumentParser()
	parser.add_argument('-d', '--debug', dest='de', help='debug option', required=False)
	args = parser.parse_args()

	#define a socket for listening
	global s
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(('', 9999))
	s.listen(5)


	#print('---Server Started---')

	read_handles = [ s, sys.stdin ]
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
			elif connection == sys.stdin:
				#print('select from input')
				msg = mybuf.Pack()
				msg.name = 'SERVER'
				msg.msg = input()
				for client in connected:
						data = msg.SerializeToString()
						data_len = struct.pack('L',len(data))
						client.sendall(data_len)
						client.sendall(data)
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
				data = read_n_bytes(connection,data_len)
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


			'''
				if len(data) == 0:
					print('because data = 0')
					connected.remove(connection)
				elif data == b'exit\n':
					print('because exit')

					connected.remove(connection)

					read_handles.remove(connection)

					connection.close()
				else:
					for client in connected:
						if client != connection:
							client.send(data)
			'''



		#print('bad attampt')
		#conn, addr = s.accept()
		#print('accept one')
		#thread = threading.Thread(target = createLink,args = (conn,addr))
		#thread.setDaemon(True)
		#thread.start()





if __name__=='__main__':
    main()

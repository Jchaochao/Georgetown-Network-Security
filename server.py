import sys
import socket
import argparse
import select
import threading

def createLink(conn, addr):
	print('A thread is successfully created, connected to',addr)
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
	print('Thread closed')
			

def main():
	#define a parser
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(('', 9999))
	s.listen(5)
	parser = argparse.ArgumentParser()
	parser.add_argument('-d', '--debug', dest='de', help='debug option', required=False)
	args = parser.parse_args()

	if args.de:
		print("waiting...")

	read_handles = [ s ]
	connected = []
	while True:
		ready_r, _, _ = select.select(read_handles, [], [])
		for connection in ready_r:
			if connection is s:
				conn, addr = s.accept()
				print("connection from", addr)
				read_handles.append(connection)
				connected.append(connection)
			else:
				data = s.recv(1024)
				for con in connected:
					con.send(data)


		#print('bad attampt')
		#conn, addr = s.accept()
		#print('accept one')
		#thread = threading.Thread(target = createLink,args = (conn,addr))
		#thread.setDaemon(True)
		#thread.start()





if __name__=='__main__':
    main()
    
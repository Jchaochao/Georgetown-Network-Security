import sys
import socket
import argparse
import select
def main():
    #define a parser
    parser = argparse.ArgumentParser()
    #define two required argument
    parser.add_argument('-s', '--server', dest='servername', help='the server IP or hostname you want to connect', required=True)
    parser.add_argument('-n', '--nickname', dest='nickname', help='your nickname', required=True)
    args = parser.parse_args()
    print(args.servername)
    print(args.nickname)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    info = s.connect((args.servername,9999))
    read_handles = [s, sys.stdin]

    while True:
        ready_to_read_list, _, _ = select.select(read_handles, [], [])
        if sys.stdin in ready_to_read_list:
            print(1)
            user_input = input()
            s.send((user_input+'\n').encode('utf-8'))
        if s in ready_to_read_list:
            print(2)
            data = s.recv(1024)
            print(data)
            if data == 'exit':
                break

    s.close()


if __name__ == '__main__':
    main()
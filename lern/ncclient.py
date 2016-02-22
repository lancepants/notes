#!/usr/bin/python3
'''
A simple python version of netcat.
'''
import socket
import sys
import optparse

def client(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # get IP address (notice gethostBYname)
    try:
        ip = socket.gethostbyname(host)
    except socket.gaierror:
        print("Error resolving hostname.")
        sys.exit(2)
    s.connect((ip, port))
    while True:
        try:
            msg = input()
        except EOFError:
            s.close()
            sys.exit()
        s.send(msg.encode())

if __name__ == '__main__':
    client(sys.argv[1], int(sys.argv[2]))

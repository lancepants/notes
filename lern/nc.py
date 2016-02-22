#!/usr/bin/python3
'''
A simple python version of netcat.

TODO:
- integrate optparse
- get client to notice when server goes away
'''
import socket
import sys
import optparse

def server(port):
    # create socket obj. AF_INET refers to ipv4
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', port))
    # put socket into listening mode, 1 conn max for simplicity
    s.listen(1)
    try:
        # conn is a NEW socket object used
        # to send/receive data to this connection address
        conn, addr = s.accept()
        print("got connection from ", addr)
        while True:
            print(conn.recv(1024).decode())
    except KeyboardInterrupt:
        s.shutdown(socket.SHUT_RDWR)
        s.close()

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
    server(int(sys.argv[1]))

import socket
import threading
import json

def client(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    try:
        sock.sendall(message + "\n")
        response = sock.recv(1024)
        print "Received: {}".format(response)
    finally:
        sock.close()

ip, port = "localhost", 9999

client(ip, port, '{"action": "register", "applicationClass": "class1"}')
client(ip, port, "Hello World 2")
client(ip, port, "Hello World 3")



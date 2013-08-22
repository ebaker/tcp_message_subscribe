import socket
import threading
import SocketServer
import json
from collections import defaultdict

def client(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    try:
        sock.sendall(message + "\n")
        response = sock.recv(1024)
        print "Received: {}".format(response)
    finally:
        sock.close()


class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):   
    def handle(self):
        handler = {'register' : self.handle_register,
                   'unregister' : self.handle_unregister,
                   'send' : self.handle_send}

        data = self.request.recv(1024)
        cur_thread = threading.current_thread()
        json_obj = None
        try:
            print data
            self.req_obj = json.loads(data )
            self.cur_thread = cur_thread
            action = self.req_obj['action']
            print "action: " + str(action)
            handler[action]()
        except:
            print 'error'
        response = "{}: {}".format(cur_thread.name, data)
        self.request.sendall(response)
        
    def handle_register(self):
        app_class = self.req_obj['applicationClass']
        cur_thread = self.cur_thread
        self.server.thread2class[cur_thread] = app_class
        self.server.class2threads[app_class].append(self.request)

    def handle_unregister(self):
        cur_thread = self.cur_thread
        app_class = self.server.thread2class[cur_thread]
        self.server.thread2class.remove(cur_thread)
        self.server.class2threads[app_class].remove(cur_thread)

    def handle_send(self):
        target_class = self.req_obj['targetClass']
        message_body = self.req_obj['messageBody']


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    def __init__(self, server_address, RequestHandlerClass):
        # self.allow_reuse_address = True
        self.thread2class = {}
        self.class2threads = defaultdict(list)
        SocketServer.TCPServer.__init__(self,
                                        server_address,
                                        RequestHandlerClass)
                                        # False)  # do not implicitly bind


if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "localhost", 9999

    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()
    print "Server loop running in thread:", server_thread.name

    
    #server.serve_forever()

    client(ip, port, '{"action": "register", "applicationClass": "class1"}')
    #print server.class2threads
    server.shutdown()

import asyncore
import socket
import json

from collections import defaultdict
import sys

CRLF = '\n' 
# CRLF = '\r\n' ## Windows

def read_exactly(sock, buflen):
    data = ''
    while len(data) != buflen:
        data += sock.recv(buflen - len(data))
    return data

def peek(sock, buflen):
    data = sock.recv(buflen, socket.MSG_PEEK)
    return data

def socket_send(sock, obj):
    data = json.dumps(obj)
    size = len(data)
    sock.sendall('%i%s%s' % (size, CRLF, data))

def socket_recv(sock):

    peekdata = peek(sock, 1024)
    print 'peeking at data:'
    print peekdata
    if peekdata == '':
        print 'Connection closed'
    #    raise ConnectionClosed
    sizepos = peekdata.find(CRLF)
    
    if sizepos == -1:
        #raise MalformedMessage('Did not find CRLF in message %r' % peekdata)
        print 'Did not find CRLF in message %r' % peekdata
        
    sizedata = read_exactly(sock, sizepos)
    print 'sizepos' + str(sizedata)
    read_exactly(sock, len(CRLF))
    result = None
    try:
        # size = int(sizedata)
        # data = read_exactly(sock, size)
        result = json.loads(sizedata)
    except:
        print "Unexpected error:", sys.exc_info()[0]
    #except ValueError:
     #   raise MalformedMessage('size data %r could not be converted to an int' % sizedata)
    return result



class EchoHandler(asyncore.dispatcher_with_send):

    def execute_req(self, req_data):
        # self.req_obj = json.loads(req_data )
        action = str(self.req_obj['action'])
        print "action: " + action
        handler_defs = {'register' : self.register_handler,
                        'unregister' : self.unregister_handler,
                        'message' : self.message_handler}
        handler_defs[action]()

    def handle_read(self):
        # data = self.recv(8192)
        self.req_obj = socket_recv(self.socket)
        #print 'test123'
        #print self.req_obj
        if self.req_obj != None:
            action = str(self.req_obj['action'])
            print "action: " + action
            handler_defs = {'register' : self.register_handler,
                            'unregister' : self.unregister_handler,
                            'message' : self.message_handler}
            handler_defs[action]()
        # if data:
        #     #self.send(data)
        #     json_obj = None
        #     try:
        #         print data + '>'
        #         self.data = data
        #         reqs = str(data).split('\n')
        #         for r in reqs:
        #             self.handle_req(r)
        #     except:
        #         print "Unexpected error:", sys.exc_info()[0]

    def register_handler(self):
        # {"action": "register", "applicationClass": "class2"}
        app_class = self.req_obj['applicationClass']
        self.server.handler2class[self] = app_class
        self.server.class2handlers[app_class].append(self)

    def unregister_handler(self):
        app_class = self.server.handler2class[self]
        self.server.handler2class.remove(self)
        self.server.class2handlers[app_class].remove(self)

    def message_handler(self):
        # {"action": "send", "targetClass": "class1", "messageBody": "my msg"}
        print 'send_msg_handler'
        target_class = self.req_obj['targetClass']
        message_body = self.req_obj['messageBody']
        handlers = self.server.class2handlers[target_class]
        if (len(handlers) > 0):
            print handlers[0].socket
            #handlers[0].send(self.data)
            socket_send(handlers[0].socket, self.req_obj)
            print 'send'
        else:
            print 'send_error'

class EchoServer(asyncore.dispatcher):

    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)
        self.handler2class = {}
        self.class2handlers = defaultdict(list)

    def handle_accept(self):
        pair = self.accept()
        if pair is None:
            pass
        else:
            sock, addr = pair
            print 'Incoming connection from %s' % repr(addr)
            handler = EchoHandler(sock)
            handler.server = self

server = EchoServer('localhost', 9999)
asyncore.loop()

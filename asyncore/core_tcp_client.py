import asyncore, socket, json

class MessageHandler():
    def __init__(self, tcp_client = None):
        #print 'init messagehandler'
        self.tcp_client = tcp_client
    def recv(self, sender_class, msg_obj):
        print "Recv from %s" % sender_class
    def send(self, target_class, msg_obj):
        self.tcp_client.send_message(target_class, msg_object)

class CoreTCPClient(asyncore.dispatcher_with_send):

    def __init__(self, host, port, init_class, msg_handler):
        asyncore.dispatcher_with_send.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect( (host, port) )
        self.app_class = init_class
        # self.buffer = '{"action": "register", "applicationClass": "%s"}\n' % init_class
        self.message_handler = msg_handler
        msg_handler.tcp_client = self
        self.register()
        #self.message("class1","msg_for_1")

    def handle_connect(self):
        pass

    def handle_close(self):
        self.close()

    def handle_read(self):
        data = self.recv(8192)
        print data +''
        try:
            self.data = strip(data)
            self.req_obj = json.loads(data )
            action = str(self.req_obj['action'])
            sender = str(self.req_obj['senderClass'])
            mb = self.req_obj['messageBody']
            print "action: " + str(action)
            #handler_defs = {'message' : recv}
            #self.message_handler.handler_defs[action](req_obj['senderClass'], req_obj['messageBody'])
            self.message_handler.recv(sender, mb)
        except:
            print 'error decoding json in handle_read'
        
    def register(self):
        print 'registering...'
        cmd = '{"action": "register", "applicationClass": "%s"}\n' % self.app_class
        print 'sending register message:'
        print cmd
        self.buffer = cmd
        self.sendall(cmd)

    def send_message(self, target_class, param_dict):
        cmd_obj = {"action": "message",
                   "targetClass": target_class,
                   "senderClass": self.app_class,
                   "messageBody": param_dict}
        cmd_str = json.dumps(cmd_obj)
        self.buffer = cmd_str
        self.sendall(cmd_str)

    #def recv_message(self, sender_class, msg_body):
        
msg_handler = MessageHandler()

client = CoreTCPClient('localhost', 9999, "class1", msg_handler)

asyncore.loop()

# client.register()



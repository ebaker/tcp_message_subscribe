import asyncore, socket, json

class MessageHandler():
    def __init__(self, tcp_client = None):
        self.tcp_client = tcp_client
    def MessageHandler(self, sender_class, msg_obj):
        print "Recv from %s" % sender_class

class CoreTCPClient(asyncore.dispatcher_with_send):

    def __init__(self, host, port, init_class, msg_handler):
        asyncore.dispatcher_with_send.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect( (host, port) )
        self.app_class = init_class
        # self.buffer = '{"action": "register", "applicationClass": "%s"}\n' % init_class
        self.message_handler = msg_handler
        self.register()
        

    def handle_connect(self):
        #pass
        self.send_message("class1","msg_for_1")

    def handle_close(self):
        self.close()

    def handle_read(self):
        data = self.recv(8192)
        print data
        # try:
        #     self.data = data
        #     self.req_obj = json.loads(data )
        #     action = self.req_obj['action']
        #     print "action: " + str(action)
        #     handler_defs = {'message' : self.message_handler}
        #     handler_defs[action].MessageHandler(req_obj['senderClass'], req_obj['messageBody'])
        # except:
        #     print 'error decoding json in handle_read'


    def register(self):
        print 'registering...'
        cmd = '{"action": "register", "applicationClass": "%s"}\n' % self.app_class
        print 'sending register message:'
        print cmd
        self.buffer = cmd
        self.send(cmd)

    def send_message(self, target_class, message_body):
        cmd_obj = {"action": "message",
                   "targetClass": target_class,
                   "senderClass": self.app_class,
                   "messageBody": message_body}
        cmd_str = json.dumps(cmd_obj) + "\n"
        print 'message json string:'
        print cmd_str
        #self.buffer = cmd_str
        self.send(cmd_str)

    #def recv_message(self, sender_class, msg_body):
        

client = CoreTCPClient('localhost', 9999, "class2", None)

asyncore.loop()

# client.register()



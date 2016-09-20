import socket
import sys
import select
import utils

class Client(object):

    def __init__(self, name, address, port):
    	self.name = name
        self.address = address
        self.port = int(port)
        self.socket = socket.socket()
        try:
            self.socket.connect((self.address, self.port))
        except:
            print "error"
            sys.exit()
    def send(self, message):
        sent = self.socket.send(message)
    def start(self):
        socketlist = [self.socket]
        readable, writeable, errored = select.select(socketlist, [],[], 0)
        self.socket.send('/new ' + self.name)
        # print 'sent /new ' + self.name
        sys.stdout.write(utils.CLIENT_MESSAGE_PREFIX); sys.stdout.flush()
        while 1:
            socketlist = [sys.stdin, self.socket]
            readable, writeable, errored = select.select(socketlist, [],[], 0)
            for sock in readable:
                if sock == self.socket:
                    data = sock.recv(2048)
                    if not data:
                        print 'disconnected'
                        sys.exit()
                    else:
                        sys.stdout.write(utils.CLIENT_WIPE_ME)
                        sys.stdout.flush()
                        sys.stdout.write('\r'+data)
                        sys.stdout.flush()
                        sys.stdout.write(utils.CLIENT_MESSAGE_PREFIX); sys.stdout.flush()
                else:
                    msg = sys.stdin.readline()
                    self.socket.send(msg)
                    sys.stdout.write(utils.CLIENT_MESSAGE_PREFIX); sys.stdout.flush()

args = sys.argv
if len(args) != 4:
    print "Please supply a name, server address and port."
    sys.exit()
name, addr, port = args[1:]
client = Client(name, addr, port)
# print 'wtf'
client.start()



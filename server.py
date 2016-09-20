import socket
import sys 
import select
import utils 

args = sys.argv
if len(args) != 2:
    print "Please supply a port."
    sys.exit()

port = int(args[1])

serversocket = socket.socket()
serversocket.bind(('', port))
serversocket.listen(5) # listen on this port for up to 5 connections

channel_to_client = {} # channel: list of clients in the channel
client_to_channel = {} # client: name of channel they're in
socket_to_name = {} # socket: username
name_to_socket = {}
LIST = "list" # /list
CREATE = "create" # /create name_of_channel username
JOIN = "join" # /join name_of_channel username
NEW = "new" # /new username 
MESSAGE = "message" # /message username actual-message

socketlist = [serversocket]
outputs = []
messages = {}

def parseCommand(data):
	split = data.split()
	return split[0], ' '.join(split[1:])

def send_to_channel(channel, socket, message, include_username=True):
	username = socket_to_name[socket]
	for member in channel_to_client[channel]:
		sock = name_to_socket[member]
		if sock != socket:
			try:
				msg = ''
				if include_username:
					msg += '[' + username + '] ' 
				msg += message
				sock.send(msg)
			except:
				sock.close()
				if sock in socketlist:
					socketlist.remove(sock)
def send_to_client(socket, message, include_newline=False):
	try:
		if include_newline:
			message += "\n"
		socket.send(message)
	except:
		print 'didnt work'
		socket.close()
		if socket in socketlist:
			socketlist.remove(sock)
def change_channel(username, new_channel):
	# remove from old channel
	old_channel = client_to_channel[username]
	if old_channel:
		channel_to_client[old_channel].remove(username)
	# add to new
	client_to_channel[username] = new_channel
	channel_to_client[new_channel].append(username)
	# tell everyone about it
	send_to_channel(channel, sock, utils.SERVER_CLIENT_JOINED_CHANNEL.format(socket_to_name[sock]), False)
while 1:
	try:
		ready_to_read, ready_to_write, in_error = select.select( \
			socketlist, [], [], 0)
	except select.error:
		print 'error! sad.'
		serversocket.close()
		exit(1)
	for sock in ready_to_read:
		if sock is serversocket: # server socket can accept a connection
			connection, addr = sock.accept() 
			socketlist.append(connection)
		else:
			try:
				data = sock.recv(1024)
				if data:
					if data[0] == '/':
						command, args = parseCommand(data)
						if command == '/new':
							socket_to_name[sock] = args
							name_to_socket[args] = sock
							client_to_channel[args] = None
						elif command == '/list':
							send_to_client(sock, '\n'.join(channel_to_client.keys()))
						elif command == '/create':
							channel = args
							if channel not in channel_to_client:
								
								# create the new one 
								channel_to_client[args] = []
								username = socket_to_name[sock]

								change_channel(username, channel)
								

							else:
								send_to_client(sock, utils.SERVER_CHANNEL_EXISTS.format(channel), True)
						elif command == '/join':
							channel = args
							if channel not in channel_to_client:
								send_to_client(sock, utils.SERVER_NO_CHANNEL_EXISTS.format(channel))
							else:
								change_channel(username, new_channel)
								
					else:
						username = socket_to_name[sock]
						if client_to_channel[username] == None:
							send_to_client(sock, utils.SERVER_CLIENT_NOT_IN_CHANNEL, True)
						else:
							send_to_channel(client_to_channel[username], sock, data)
				else:
					if sock in socketlist:
						socketlist.remove(sock)
					
			except:
				continue
				

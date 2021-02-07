from Pocket import Pocket
from Inbox import Inbox
from Outbox import Outbox
# import scapy
# import getmac

class Grapple:
	'''handles all connections to and exchange of information with remote nodes'''
	def __init__(self):
		self.socket = None # stores TCP connection with node

	def get_socket(self):
		'''returns current socket (active or otherwise)'''
		return self.socket

	def find_node(self):
		'''identifies, returns addr of node on local network'''
		# should run network scan to get all IPs
		# then compare mac addresses of all IPs to prefix for rpis
		# (https://raspberrypi.stackexchange.com/a/13937)
		# perform some sort of handshake with node to verify correctness
		return "127.0.0.1" # for the scope of hackathon, node address addr is hardcoded

	def setup(self, server_info):
		'''sets up socket for communication with node'''
		# create new socket, using ipv4 type address, tcp protocol
		new_socket = socket(AF_INET, SOCK_STREAM)
		# connect to the node with given info
		new_socket.connect(server_info)
		return new_socket

	def close(self):
		'''close socket and end communication with node'''
		self.socket.close()
		return

	def socket_message(self, message):
		'''encode and send given message over socket'''
		# https://stackoverflow.com/a/14473492/4513452
		self.socket.send( bytes(message) )
		return

	def identify_self(self):
		'''identify self to node by sending own pub key'''
		# *should* sign own public key and send that as message, node can verify ownership
		public_key = Pocket().public_key() # grab own pub key as bytes
		# for now will just send own public key to node
		self.socket_message(public_key)
		return

	def receive_messages(self, own_inbox):
		'''receive incoming messages via socket'''
		# wait to receive the response from the server (using buffer size of 2048)
		incoming_messages = [] # make list to hold all incoming messages
		# while not received end indicator
		while str(client_socket.recv(2048)) != "RECV_FINISHED":
			incoming_messages.append(client_socket.recv(2048)) # append to message list
		for i in range(len(incoming_messages)): # for all received messages
			# don't know what I was doing here, but pretty sure this method doesn't exist
			# own_inbox.add_transit_message(incoming_messages[i]) # add to given inbox
			own_inbox.add_message(incoming_messages[i]) # add to given inbox
		return

	def send_messages(self, own_outbox):
		'''send messages to node over socket'''
		# may want to check if message has already been delivered to a given node later
		outgoing_messages = [] # make list to hold outgoing messages
		for i in range(own_outbox.count_messages()): # for num messages in outbox
			# "send" message at front of outbox by adding to outgoing messages list
			# and decrementing remaining deliveries to make
			outgoing_messages.append(own_outbox.send_message())
		# send all messages in outgoing messages list
		for i in range(len(outgoing_messages)):
			self.socket_message(outgoing_messages[i])
		# send message indicating end of send
		self.socket_message("SEND_FINISHED")
		return

	def embrace(self, own_inbox, own_outbox):
		'''identifies node on local network, instantiates connection and exchanges messages'''
		node_address = self.find_node() # identify and record node location
		self.socket = self.setup(node_address) # instantiate socket and save to self
		self.identify_self() # identify self to node via socket
		self.receive_messages(own_inbox) # collect incoming messages and add to inbox
		self.send_messages(own_outbox) # send all outgoing messages from outbox
		self.close()
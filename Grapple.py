from Pocket import Pocket
from Inbox import Inbox
from Outbox import Outbox
from socket import *
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
		return ("127.0.0.1", 13337) # for the scope of hackathon, node address addr is hardcoded

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
		# janky, but default bytes() method for pgpy was causing encoding issues
		message = str(message)
		print("message being sent: ", message)
		self.socket.send( bytes(message, encoding='utf8') )
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
		# while not received end indicator (breaks out if received)
		count = 0
		while True: # easier this way because each read of socket is new message
			caught_message = self.socket.recv(2048).decode() # decoded socket data
			print("\n\tcaught message: ", caught_message)
			count += 1
			if count == 10:
				break
			if (caught_message == "RECV_FINISHED"): # received end indicator
				break
			incoming_messages.append(caught_message) # append to message list
		for i in range(len(incoming_messages)): # for all received messages
			# don't know what I was doing here, but pretty sure this method doesn't exist
			# own_inbox.add_transit_message(incoming_messages[i]) # add to given inbox
			own_inbox.add_message( incoming_messages[i] ) # add to given inbox
		return

	def send_messages(self, own_outbox):
		'''send messages to node over socket'''
		# may want to check if message has already been delivered to a given node later
		outgoing_messages = [] # make list to hold outgoing messages
		for i in range(own_outbox.count_messages()): # for num messages in outbox
			# "send" message at front of outbox by adding to outgoing messages list
			# and decrementing remaining deliveries to make
			outgoing_messages.append(own_outbox.send_message())
		# janky, but for sake of hackathon, slowing messages down
		import time
		# send all messages in outgoing messages list
		for i in range(len(outgoing_messages)):
			self.socket_message( outgoing_messages[i] )
			time.sleep(2)
		# janky, but for sake of hackathon
		time.sleep(2)
		# send message indicating end of send
		self.socket_message("SEND_FINISHED")
		return

	def embrace(self, own_inbox, own_outbox):
		'''identifies node on local network, instantiates connection and exchanges messages'''
		print("\n\tembrace 1")
		node_address = self.find_node() # identify and record node location
		print("\n\tembrace 2")
		self.socket = self.setup(node_address) # instantiate socket and save to self
		print("\n\tembrace 3")
		self.identify_self() # identify self to node via socket
		print("\n\tembrace 4")
		self.receive_messages(own_inbox) # collect incoming messages and add to inbox
		print("\n\tembrace 5")
		self.send_messages(own_outbox) # send all outgoing messages from outbox
		print("\n\tembrace 6")
		self.close()
		print("\n\tembrace 7")
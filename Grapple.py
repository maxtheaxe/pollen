from Pocket import Pocket
from Inbox import Inbox
from Outbox import Outbox
from socket import *
# import scapy
# import getmac
import sys

class Grapple:
	'''handles all connections to and exchange of information with remote nodes'''
	def __init__(self):
		self.socket = None # stores TCP connection with node
		# https://stackoverflow.com/a/26641964/4513452
		self.big_drop = "" # stores all messages, to be sent all at once

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

	def add_to_drop(self, new_message):
		'''adds message to string with "|" as dellineator'''
		# I apologize to anyone who reads this--no time to justify it right now
		self.big_drop += new_message + "$$$$"
		return

	def socket_message(self, message):
		'''encode and send given message over socket'''
		# https://stackoverflow.com/a/14473492/4513452
		# janky, but default bytes() method for pgpy was causing encoding issues
		message = str(message)
		# print("size of message being sent: ", sys.getsizeof(message))
		# print("message being sent: ", message)
		# self.socket.send( bytes(message, encoding='utf8') )
		# as temporary fix, instead of sending, add to compiled message
		self.add_to_drop(message)
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
		# incoming_messages = [] # make list to hold all incoming messages
		# # while not received end indicator (breaks out if received)
		# while True: # easier this way because each read of socket is new message
		# 	caught_message = self.socket.recv(2048).decode() # decoded socket data
		# 	print("\n\tcaught message: ", caught_message)
		# 	if (caught_message == "RECV_FINISHED"): # received end indicator
		# 		break
		# 	incoming_messages.append(caught_message) # append to message list
		# catch incoming messages (really just one big one)
		# incoming_data = self.socket.recv(2048).decode()
		incoming_data = ""
		while True:
			# receive data stream
			data_catch = self.socket.recv(2048).decode()
			# print("data_catch: ", data_catch)
			# continually add incoming data to storage string
			incoming_data += data_catch
			# wait for end of message indicator
			if (incoming_data[-4:] == "####"):
				break
		incoming_messages = incoming_data.split("$$$$")[:-1] # cut off end because it's not msg
		for i in range(len(incoming_messages)): # for all received messages
			# don't know what I was doing here, but pretty sure this method doesn't exist
			# own_inbox.add_transit_message(incoming_messages[i]) # add to given inbox
			# print("incoming message type: ", type(incoming_messages[i]))
			# print("incoming message: ", incoming_messages[i])
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
		# send all messages in outgoing messages list
		for i in range(len(outgoing_messages)):
			self.socket_message( outgoing_messages[i] )
		# send message indicating end of send
		# self.socket_message("SEND_FINISHED") # not for new type
		# temporary fix
		# print("actual message: ", (self.big_drop + "####")
		self.socket.send( bytes((self.big_drop + "####"), encoding='utf8') )
		return

	def embrace(self, own_inbox, own_outbox):
		'''identifies node on local network, instantiates connection and exchanges messages'''
		node_address = self.find_node() # identify and record node location
		self.socket = self.setup(node_address) # instantiate socket and save to self
		self.identify_self() # identify self to node (just add to front of out data)
		self.send_messages(own_outbox) # send all outgoing messages from outbox
		self.receive_messages(own_inbox) # collect incoming messages and add to inbox
		self.close()

if __name__ == '__main__':
	# pickle testing (just for testing which types have pickle issues)
	import pickler as pr
	var_name = 'new_grapple'
	og_init = " = " + "Grapple()"
	if pr.is_pickled(var_name):
		exec(var_name + " = pr.get_pickled(var_name)")
	else:
		exec(var_name + og_init)
		pr.pickle_it(var_name, eval(var_name))
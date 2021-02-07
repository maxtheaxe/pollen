from NodeBox import NodeBox
from socket import *

class Node:
	'''handles all node operations'''
	def __init__(self):
		self.nodebox = NodeBox()
		self.socket = self.setup_socket()
		self.version = "0.0.1"

	def setup_socket(self, server_address = "127.0.0.1", server_port = 13337):
		'''returns socket that will be used for communication with clients'''
		# store server communication info in tuple for later
		server_info = (server_address, server_port)
		# create new socket, using ipv4 type address, tcp protocol
		welcome_socket = socket(AF_INET, SOCK_STREAM)
		# bind the socket to the given info (basically just setting port)
		welcome_socket.bind(server_info)
		# listen for incoming connections on the socket
		welcome_socket.listen(1)
		# return the socket for later usage
		return welcome_socket

	def socket_message_monitor(self):
		'''monitor a given socket for messages'''
		# should loop infinitely while server is running
		while True:
			print("\n\t-------new loop-------")
			# create a new communication socket if requested
			communication_socket, client_address = self.socket.accept()
			# catch incoming messages (really just one big one)
			incoming_data = communication_socket.recv(2048).decode()
			# incoming_data = ""
			# while True:
			# 	# receive data stream
			# 	data_catch = communication_socket.recv(2048).decode()
			# 	# wait for end of message indicator (doesn't matter that it's after)
			# 	if (data_catch == "####"):
			# 		break
			# 	# continually add incoming data to storage string
			# 	incoming_data += data_catch
			# split up incoming data into list of messages
			print("before delete: ", incoming_data.split("$$$$"))
			incoming_messages = incoming_data.split("$$$$")[:-1] # cut off end because it's not msg
			# collect messages for user according to public key
			collected_messages = self.nodebox.collect_messages(public_key = incoming_messages.pop(0))
			print("collected_messages: ", collected_messages)
			# build outgoing messages string
			outgoing_messages = ""
			for i in range(len(collected_messages)):
				outgoing_messages += collected_messages[i] + "$$$$"
			# outgoing_messages += "SEND_FINISHED" # may not be necessary when sending all
			# encode into outgoing data, add end indicator
			outgoing_data = (outgoing_messages + "####").encode()
			# send messages back
			communication_socket.send(outgoing_data)
			print("done sending messages to client")
			# finish, close socket
			# communication_socket.close()
			# move all received messages to NodeBox
			for i in range(len(incoming_messages)):
				print("adding received")
				self.nodebox.add_message(incoming_messages[i]) # add each message
			print("done adding received: ", incoming_messages)
			# finished embrace with user, wait for next one

if __name__ == '__main__':
	# announce self running
	print("\n\tPollen Node Now Running...")
	# potentially load pickled version of old node later
	node_instance = Node()
	# start monitoring socket indefinitely
	node_instance.socket_message_monitor()
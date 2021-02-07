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
			# grab the incoming message on communication socket
			incoming_message = communication_socket.recv(2048)
			print("incoming message type: ", type(incoming_message))
			# decode received message
			incoming_message = (incoming_message.decode())
			print("incoming message type: ", type(incoming_message))
			# let user know message was received
			# print('\n\tMessage \n"{}" received'.format(incoming_message))
			# should check if incoming message is a pgp public key (for now assuming it is)
			# retrieve messages associated with given public key
			collected_messages = self.nodebox.collect_messages(public_key = incoming_message)
			print("collected_messages: ", collected_messages)
			# janky, but for sake of hackathon, slowing messages down
			import time
			# send messages back
			for i in range(len(collected_messages)):
				communication_socket.send( collected_messages[i].encode() ) # send over existing socket
				time.sleep(2)
			time.sleep(2)
			# indicate done sending messages
			communication_socket.send( "RECV_FINISHED".encode() )
			print("done sending messages to client")
			received_messages = []
			# listen for messages being dropped off while end hasn't been indicated
			count = 0
			while True: # easier this way because each read of socket is new message
				 # decoded socket data
				caught_message = communication_socket.recv(2048).decode()
				print("caught_message: ", caught_message)
				count += 1
				# if count == 10:
				# 	break
				if (caught_message == "SEND_FINISHED"): # received end indicator
					break
				# append it to received list
				received_messages.append(caught_message)
			# done receiving messages, close socket
			communication_socket.close()
			print("closed socket")
			# move all received messages to NodeBox
			for i in range(len(received_messages)):
				print("adding received")
				self.nodebox.add_message(received_messages[i]) # add each message
			print("done adding received")
			# finished embrace with user, wait for next one

if __name__ == '__main__':
	# announce self running
	print("\n\tPollen Node Now Running...")
	# potentially load pickled version of old node later
	node_instance = Node()
	# start monitoring socket indefinitely
	node_instance.socket_message_monitor()
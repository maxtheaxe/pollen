import pgpy
from MessageBox import MessageBox
from LocalMessage import LocalMessage
import re

class Conversation(MessageBox):
	'''handles all messages between two users'''
	def __init__(self, peer, messages = []):
		super().__init__(messages) # message storage list
		self.friendly_name = self.grab_name(peer) # get temp random name
		self.peer = peer # pgp key of other user in conversation

	def grab_name(self, pgp_key):
		'''returns first 8 character-long alpha sequence from given pgp key'''
		# https://www.programiz.com/python-programming/regex#python-regex
		pattern = '[a-zA-Z]{8}'
		name_found = re.search(pattern, str(pgp_key)) # search for usable sequence
		if (not name_found): # if no usable sequence was found
			random_name = "new_peer" # just use "new_peer" instead
		else:
			random_name = name_found.group() # grab the usable sequence
		return random_name

	def add_message(self, new_message):
		'''add new LocalMessage to list'''
		# if message type is LocalMessage
		if not (type(new_message) == LocalMessage):
			# raise error and show incorrect type
			error_text = "new message type: " + type(new_message)
			raise TypeError(error_text)
		else: # otherwise, append the new message
			self.messages.append(new_message)
		return

	def most_recent(self):
		'''returns most recent message in conversation'''
		return self.messages[-1]

if __name__ == '__main__':
	pass
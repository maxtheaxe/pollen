import pgpy
from MessageBox import MessageBox
from LocalMessage import LocalMessage
import re

class Conversation(MessageBox):
	'''handles all messages between two users'''
	def __init__(self, peer, messages = []):
		super().__init__(messages) # message storage list
		self.friendly_name = self.create_name(peer) # get temp random name
		self.peer = peer # pgp key of other user in conversation

	def create_name(self, pgp_key):
		'''returns 8 character-long alpha-numeric sequence from given pgp key'''
		# https://www.programiz.com/python-programming/regex#python-regex
		pattern = '[a-zA-Z0-9]{25}'
		name_found = re.search(pattern, str(pgp_key)) # search for usable sequence
		if (not name_found): # if no usable sequence was found
			random_name = "new_peer" # just use "new_peer" instead
		else:
			random_name = name_found.group()[17:25] # grab the usable sequence
		return random_name

	def get_name(self):
		'''returns friendly name of self'''
		return self.friendly_name

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

	def __getstate__(self):
		'''helper method that allows this class to be pickled'''
		# ref: https://stackoverflow.com/a/41754104
		pickled_self = {
			'messages' : self.messages,
			'friendly_name' : str(self.friendly_name),
			'peer' : str(self.peer)
		}
		return pickled_self

	def __setstate__(self, pickled_self):
		'''helper method that allows this class to be unpickled'''
		self.messages = pickled_self['messages']
		self.friendly_name = pickled_self['friendly_name']
		self.peer, _ = pgpy.PGPKey.from_blob(pickled_self['peer'])
		return

if __name__ == '__main__':
	import pgpy
	message = "hey, do messages work?"
	password = "fake_password"
	peer, _ = pgpy.PGPKey.from_file("other_pub.asc") # pubkey from local dir
	# pickle testing (just for testing which types have pickle issues)
	import pickler as pr
	var_name = 'new_convo'
	og_init = " = " + "Conversation(peer)"
	if pr.is_pickled(var_name):
		exec(var_name + " = pr.get_pickled(var_name)")
	else:
		exec(var_name + og_init)
		pr.pickle_it(var_name, eval(var_name))
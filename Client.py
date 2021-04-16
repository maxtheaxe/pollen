from Pocket import Pocket
from ConversationManager import ConversationManager
from Inbox import Inbox
from Outbox import Outbox
from LocalMessage import LocalMessage
from TransitMessage import TransitMessage
from Grapple import Grapple
import pickle

class Client:
	'''manages all functions of user'''
	def __init__(self):
		self.pocket = Pocket()
		self.conversation_manager = ConversationManager()
		self.inbox = Inbox()
		self.outbox = Outbox()
		self.password = "fake_password" # obv need to come up with better way
		# optimally, i'd prompt on each launch of app and store securely for session
		self.version = "0.0.1"

	def compose_message(self, peer, message_body):
		'''
		creates new message
			stores it in ConversationManager as LocalMessage
			stores it in Outbox as TransitMessage
		'''
		# side note: ^ this is why I don't like how docstrings look within code--so ugly
		local_message = LocalMessage(message_body, peer, False)
		self.conversation_manager.add_message(local_message)
		transit_message = TransitMessage(local_message, self.password)
		self.outbox.add_transit_message(transit_message)

	def meet_node(self):
		'''connect to node and exchange messages'''
		# obv no need for grapple to be a class here, but I'm thinking it may
		# make sense to maintain socket/connection for a period of time in the future
		Grapple().embrace(self.inbox, self.outbox)

	def update_messages(self):
		'''exchange messages with node, import new messages into ConversationManager'''
		# separated because it may also make sense not do these two things
		# at the same time later (sorting inbox doesn't require connection)
		self.meet_node() # exchange messages with node
		# sort messages just received and stored in inbox
		self.inbox.sort_messages(self.outbox, self.conversation_manager, self.password)

	def __getstate__(self):
		'''helper method that allows this class to be pickled'''
		# ref: https://stackoverflow.com/a/41754104
		# should verify that this is an acceptible usage,
		# but pickle should also be replaced altogether
		pickled_self = {
			'pocket' : pickle.dumps(self.pocket),
			'conversation_manager' : pickle.dumps(self.conversation_manager),
			'inbox' : pickle.dumps(self.inbox),
			'outbox' : pickle.dumps(self.outbox),
			'password' : self.password, # gotta fix this crap
			'version' : self.version
		}
		return pickled_self

	def __setstate__(self, pickled_self):
		'''helper method that allows this class to be unpickled'''
		# print("pocket:\n", pickled_self['pocket'])
		self.pocket = pickle.loads(pickled_self['pocket'])
		self.conversation_manager = pickle.loads(pickled_self['conversation_manager'])
		self.inbox = pickle.loads(pickled_self['inbox'])
		self.outbox = pickle.loads(pickled_self['outbox'])
		self.password = pickled_self['password'] # gotta fix this crap
		self.version = pickled_self['version']
		return

if __name__ == '__main__':
	import time
	import pgpy
	# announce self running
	print("\n\tPollen Client Now Running...")
	# pickle testing (just for testing which types have pickle issues)
	import pickler as pr
	var_name = 'client_instance'
	og_init = " = " + "Client()"
	if pr.is_pickled(var_name):
		exec(var_name + " = pr.get_pickled(var_name)")
	else:
		exec(var_name + og_init)
		pr.pickle_it(var_name, eval(var_name))
	# client_instance = Client()
	# message details
	# my_pubkey = client_instance.pocket.public_key()
	my_pubkey, _ = pgpy.PGPKey.from_file('second_pollen_key.asc')
	my_pubkey = my_pubkey.pubkey
	message_body = "this is a second message key sent using pollen.im"
	# compose new message
	client_instance.compose_message(my_pubkey, message_body)
	print("\n\tinbox num messages: ", client_instance.inbox.count_messages())
	pr.pickle_it(var_name, eval(var_name)) # updates pickle of instance
	# # embrace node and exchange messages
	# print("\n\tconnecting to node...")
	# client_instance.update_messages()
	# print("\n\tdone")
	# # wait 15 seconds
	# print("\n\tsleeping 5 seconds...")
	# time.sleep(5)
	# # embrace node and exchange messages again
	# print("\n\tconnecting to node again...")
	# client_instance.update_messages()
	# print("\n\tdone")
	# check final status of own boxes
	print("\n\tinbox num messages: ", client_instance.inbox.count_messages())
	print("\n\toutbox num messages: ", client_instance.outbox.count_messages())
	print("\n\tnum conversations: ", client_instance.conversation_manager.count_conversations())
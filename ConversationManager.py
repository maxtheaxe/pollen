import pgpy
from Conversation import Conversation

class ConversationManager:
	'''manages all conversations'''
	def __init__(self, conversations = {}):
		# key = pubkey of peer; value = conversation
		self.conversations = conversations # dict of existing conversations

	def add_message(self, new_message):
		'''adds LocalMessage to appropriate conversation, creates it if doesn't exist'''
		peer_key = str(new_message.get_peer()) # get pubkey of peer to sort into proper convo
		# ** might need to convert pgp keys to bytes if there are issues later **
		if peer_key not in self.conversations: # if convo with this peer doesn't exist yet
			# then create a new conversation
			self.conversations[peer_key] = Conversation(peer_key)
		# add the new message to the conversation (either newly-created or preexisting)
		self.conversations[peer_key].add_message(new_message)
		return

	def count_conversations(self):
		'''returns integer num conversations being managed'''
		return len(self.conversations)

if __name__ == '__main__':
	# pickle testing (just for testing which types have pickle issues)
	import pickler as pr
	var_name = 'new_convo_mgr'
	og_init = " = " + "ConversationManager()"
	if pr.is_pickled(var_name):
		exec(var_name + " = pr.get_pickled(var_name)")
	else:
		exec(var_name + og_init)
		pr.pickle_it(var_name, eval(var_name))
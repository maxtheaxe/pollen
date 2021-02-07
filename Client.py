from Pocket import Pocket
from ConversationManager import ConversationManager
from Inbox import Inbox
from Outbox import Outbox
from Grapple import Grapple

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
		Grapple.embrace(self.inbox, self.outbox)

	def update_messages(self):
		'''exchange messages with node, import new messages into ConversationManager'''
		# separated because it may also make sense not do these two things
		# at the same time later (sorting inbox doesn't require connection)
		self.meet_node() # exchange messages with node
		# sort messages just received and stored in inbox
		self.inbox.sort_messages(self.outbox, self.conversation_manager, self.password)

	def dump_data(self):
		'''basic data persistence via pickling entire self'''
		# will probably cause problems bc pickle doesn't like pgp objects
		return
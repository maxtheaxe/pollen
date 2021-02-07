import pgpy
from MessageBox import MessageBox
from Outbox import Outbox
from ConversationManager import ConversationManager
from TransitMessage import TransitMessage
from Pocket import Pocket

class Inbox(MessageBox):
	'''handles all aspects of incoming messages'''
	def __init__(self, messages = []):
		super().__init__(messages)

	# should sort messages
	# either just try and catch decrypting everything or sort out own msgs on receipt
	# own messages should be placed into appropriate conversations and deleted

	def add_message(self, new_message):
		'''de-jsonify messages and add new TransitMessage to list'''
		transit_message = TransitMessage(jsoned_message = new_message)
		super().add_message(transit_message) # add message to list
		return

	def plain_save(self, message, password):
		'''decrypts TransitMessage and returns as LocalMessage'''
		return message.detransit(password)

	def sort_messages(self, own_outbox, convo_mgr, password):
		'''sort own messages, store in either conversations or outbox'''
		for i in range(len(self.messages)):
			# check if message is intended for self
			if (self.messages[i].for_self()):
				# print("the message was for me")
				# decrypt and convert to LocalMessage
				local_message = self.plain_save(self.messages[i], password)
				# add to conversation with appropriate peer (sender)
				convo_mgr.add_message(local_message)
			else: # message intended for re-transmission
				own_outbox.add_transit_message(self.messages[i])
		# could also pop messages out from front rather than wiping, idk which is better
		self.messages = []
		return

if __name__ == '__main__':
	from LocalMessage import LocalMessage
	new_box = Inbox()
	new_outbox = Outbox()
	new_convo_mgr = ConversationManager()
	message = "hey, do messages work?"
	password = "fake_password"
	# same key is sender and receiver in this case; easier for testing
	peer, _ = pgpy.PGPKey.from_file("pollen_key.asc")
	peer = peer.pubkey # simplify to just pubkey
	# peer, _ = pgpy.PGPKey.from_file("other_pub.asc") # pubkey from local dir
	print("type: ", type(peer))
	sent = False # issue here (might be flipped?)
	new_message = LocalMessage(message, peer, sent)
	new_transit = TransitMessage(new_message, password)
	print("I am sender: ", bytes(new_transit.sender) == bytes(Pocket().public_key()))
	jsonified_transit = new_transit.jsonify()
	new_box.add_message(jsonified_transit)
	print("num messages: ", new_box.count_messages())
	# new_box.remove_message(0)
	new_box.sort_messages(new_outbox, new_convo_mgr, password)
	print("num messages: ", new_box.count_messages())
	print("outbox messages: ", new_outbox.count_messages())
	print("num conversations: ", new_convo_mgr.count_conversations())
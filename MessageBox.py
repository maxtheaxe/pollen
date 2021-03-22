from LocalMessage import LocalMessage
from TransitMessage import TransitMessage
from OutboxMessage import OutboxMessage

class MessageBox:
	'''the base message box, stores groups of messages'''
	def __init__(self, messages):
		self.messages = messages # holds LocalMessages, TransitMessages or OutboxMessages

	def add_message(self, new_message):
		'''appends new message to end of messages list'''
		# https://stackoverflow.com/a/19211875/4513452
		allowed_types = [LocalMessage, TransitMessage, OutboxMessage]
		# if message type is none of allowed types
		if not any(msg_type == type(new_message) for msg_type in allowed_types):
			# raise error and show incorrect type
			error_text = "new message type: " + type(new_message)
			raise TypeError(error_text)
		else: # otherwise, append the new message
			self.messages.append(new_message)

	def remove_message(self, message_index):
		'''removes, returns message at a given index'''
		return self.messages.pop(message_index)

	def count_messages(self):
		'''return the number of messages in MessageBox'''
		return len(self.messages)

if __name__ == '__main__':
	import pgpy
	# new_box = MessageBox([])
	message = "hey, do messages work?"
	password = "fake_password"
	peer, _ = pgpy.PGPKey.from_file("other_pub.asc") # pubkey from local dir
	# pickle testing (just for testing which types have pickle issues)
	import pickler as pr
	var_name = 'new_box'
	og_init = " = " + "MessageBox([])"
	if pr.is_pickled(var_name):
		exec(var_name + " = pr.get_pickled(var_name)")
	else:
		exec(var_name + og_init)
		pr.pickle_it(var_name, eval(var_name))
	print("type: ", type(peer))
	sent = False
	new_message = LocalMessage(message, peer, sent)
	print(new_message)
	print("num messages: ", new_box.count_messages())
	new_box.add_message(new_message)
	print("num messages: ", new_box.count_messages())
	new_box.remove_message(0)
	print("num messages: ", new_box.count_messages())
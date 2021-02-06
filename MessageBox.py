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
import pgpy
from LocalMessage import LocalMessage
from TransitMessage import TransitMessage
from OutboxMessage import OutboxMessage
from MessageBox import MessageBox

class Outbox(MessageBox):
	'''handles all aspects of outgoing messages'''
	def __init__(self, messages = []):
		super().__init__(messages)
		self.deliveries = 5 # default number of deliveries to make of each message to make

	def add_message(self, new_message, password, deliveries = self.deliveries):
		'''add new LocalMessage to list as OutboxMessage'''
		# convert the LocalMessage to an OutboxMessage (TransitMessage w delivery count)
		outbox_message = OutboxMessage(new_message, password, deliveries)
		# call the parent method with the converted message
		super().add_message(outbox_message)

	def send_message(self):
		'''send the message from front of list, decrement deliveries and send to back'''
		ready_message = self.messages.pop(0) # pop out first message in list
		ready_message.decrement() # decrement remaining deliveries by one
		if (ready_message.check_remaining() != 0): # if there are deliveries remaining
			super().add_message(ready_message) # re-add to end of list
		final_message = ready_message.jsonify() # jsonify popped message in order to send
		# connect to node and actually deliver message using grapple
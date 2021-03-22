import pgpy
from LocalMessage import LocalMessage
from TransitMessage import TransitMessage
from OutboxMessage import OutboxMessage
from MessageBox import MessageBox

class Outbox(MessageBox):
	'''handles all aspects of outgoing messages'''
	def __init__(self, messages = [], deliveries = 5):
		super().__init__(messages)
		self.deliveries = deliveries # number of deliveries to make of each message

	def add_message(self, new_message, password):
		'''add new LocalMessage to list as OutboxMessage'''
		# convert the LocalMessage to an OutboxMessage (TransitMessage w delivery count)
		outbox_message = OutboxMessage(new_message, password, deliveries = self.deliveries)
		# call the parent method with the converted message
		super().add_message(outbox_message)

	def add_transit_message(self, new_message):
		'''add new TransitMessage to list as OutboxMessage'''
		# jsonify message so OutboxMessage constructor can handle it
		new_jsonified = new_message.jsonify()
		# convert TransitMessage to an OutboxMessage (TransitMessage w delivery count)
		outbox_message = OutboxMessage(deliveries = self.deliveries,
										jsonified_transit = new_jsonified)
		# call the parent method with the converted message
		super().add_message(outbox_message)
		return

	def send_message(self):
		'''send the message from front of list, decrement deliveries and send to back'''
		ready_message = self.messages.pop(0) # pop out first message in list
		ready_message.decrement() # decrement remaining deliveries by one
		if (ready_message.check_remaining() != 0): # if there are deliveries remaining
			super().add_message(ready_message) # re-add to end of list
		final_message = ready_message.jsonify() # jsonify popped message in order to send
		# connect to node and actually deliver message using grapple
		return final_message

if __name__ == '__main__':
	# new_box = Outbox([])
	# pickle testing (just for testing which types have pickle issues)
	import pickler as pr
	var_name = 'new_box'
	og_init = " = " + "Outbox([])"
	if pr.is_pickled(var_name):
		exec(var_name + " = pr.get_pickled(var_name)")
	else:
		exec(var_name + og_init)
		pr.pickle_it(var_name, eval(var_name))
	message = "hey, do messages work?"
	password = "fake_password"
	peer, _ = pgpy.PGPKey.from_file("other_pub.asc") # pubkey from local dir
	print("type: ", type(peer))
	sent = False
	new_message = LocalMessage(message, peer, sent)
	print(new_message)
	new_transit = TransitMessage(new_message, password)
	jsonified_transit = new_transit.jsonify()
	print("num messages: ", new_box.count_messages())
	new_box.add_message(new_message, password)
	new_box.add_transit_message(jsonified_transit)
	print("num messages: ", new_box.count_messages())
	new_box.remove_message(0)
	print("num messages: ", new_box.count_messages())
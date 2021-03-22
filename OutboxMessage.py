from TransitMessage import TransitMessage
import pgpy
import json

class OutboxMessage(TransitMessage):
	'''numbered version of TransitMessage for keeping track of times message was sent'''
	def __init__(self, local_message = None, password = None, deliveries = 10,
					jsonified_transit = None, transit_message = None):
		# needed args to create from local message
		local_args = [local_message, password, deliveries]
		# should probably group this w jsonified and sort by checking type later
		# also definitely a better way of doing this...will explore later
		# https://stackoverflow.com/q/30105134
		if (transit_message != None):
			# store fields in appropriate areas (again, this is temporary)
			self.pgp_message = transit_message.pgp_message
			self.sender = transit_message.sender
			self.recipient = transit_message.recipient
		# i definitely jsonified something somewhere else that was unnecessary (inbox?)
		elif (jsonified_transit != None): # must be jsonified transit message input
			# un-json data and grab values from dict, convert to proper type
			unjsoned_data = json.loads(jsonified_transit)
			self.pgp_message = pgpy.PGPMessage.from_blob(unjsoned_data["pgp_message"])
			# https://pgpy.readthedocs.io/en/latest/api.html#pgpy.PGPKey.from_blob
			self.sender, _ = pgpy.PGPKey.from_blob(unjsoned_data["sender"])
			self.recipient, _ = pgpy.PGPKey.from_blob(unjsoned_data["recipient"])
		elif (any(arg == None for arg in local_args)): # bad arguments given
			# raise error and show faulty arguments
			error_text = "given args: " + str(local_message) + ", " + password + ", "
			# yeahh sorry there's a better way
			error_text += deliveries + ", " + jsonified_transit
			raise ValueError(error_text)
		else: # must be local message input
			super().__init__(local_message, password) # call super constr (never jsoned)
		self.deliveries = deliveries

	def decrement(self):
		'''decrements remaining deliveries by one'''
		self.deliveries -= 1

	def check_remaining(self):
		'''returns remaining deliveries'''
		return self.deliveries

if __name__ == '__main__':
	from Pocket import Pocket
	from LocalMessage import LocalMessage
	# test code from LocalMessage (surely there's a better way, sorry)
	message = "hey, do messages work?"
	password = "fake_password"
	peer = Pocket().public_key() # pubkey from local dir
	sent = False
	new_message = LocalMessage(message, peer, sent)
	# prepped_message = new_message.prep(password)
	# print("type: ", type(prepped_message))
	# pickle testing (just for testing which types have pickle issues)
	import pickler as pr
	var_name = 'new_outbox_message'
	og_init = " = " + "OutboxMessage(new_message, password)"
	if pr.is_pickled(var_name):
		exec(var_name + " = pr.get_pickled(var_name)")
	else:
		exec(var_name + og_init)
		pr.pickle_it(var_name, eval(var_name))
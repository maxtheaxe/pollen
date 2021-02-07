from TransitMessage import TransitMessage
import pgpy
import json

class OutboxMessage(TransitMessage):
	'''numbered version of TransitMessage for keeping track of times message was sent'''
	def __init__(self, local_message = None, password = None, deliveries = None, jsonified_transit = None):
		# needed args to create from local message
		local_args = [local_message, password, deliveries]
		if (jsonified_transit != None): # must be transit message input
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
from TransitMessage import TransitMessage
import json

class OutboxMessage(TransitMessage):
	'''numbered version of TransitMessage for keeping track of times message was sent'''
	def __init__(self, local_message = None, password = None, remaining_deliveries = None, transit_message = None):
		# needed args to create from local message
		local_args = [local_message, password, remaining_deliveries]
		if (transit_message != None): # must be transit message input
			# un-json data and grab values from dict, convert to proper type
			unjsoned_data = json.loads(transit_message)
			self.pgp_message = pgpy.PGPMessage.from_blob(unjsoned_data["pgp_message"])
			# https://pgpy.readthedocs.io/en/latest/api.html#pgpy.PGPKey.from_blob
			self.sender, _ = pgpy.PGPKey.from_blob(unjsoned_data["sender"])
			self.recipient, _ = pgpy.PGPKey.from_blob(unjsoned_data["recipient"])
		elif (any(arg == None for arg in local_args)): # bad arguments given
			# raise error and show faulty arguments
			error_text = "given args: " + str(local_message) + ", " + password + ", "
			# yeahh sorry there's a better way
			error_text += remaining_deliveries + ", " + transit_message
			raise ValueError(error_text)
		else: # must be local message input
			super().__init__(local_message, password) # call super constr (never jsoned)
		self.remaining_deliveries = remaining_deliveries

	def decrement(self):
		'''decrements remaining deliveries by one'''
		self.remaining_deliveries -= 1

	def check_remaining(self):
		'''returns remaining deliveries'''
		return self.remaining_deliveries
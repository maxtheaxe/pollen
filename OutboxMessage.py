from TransitMessage import TransitMessage

class OutboxMessage(TransitMessage):
	'''numbered version of TransitMessage for keeping track of times message was sent'''
	def __init__(self, local_message, password, remaining_deliveries):
		super().__init__(local_message, password) # call super constructor (never jsoned)
		self.remaining_deliveries = remaining_deliveries

	def decrement(self):
		'''decrements remaining deliveries by one'''
		self.remaining_deliveries -= 1
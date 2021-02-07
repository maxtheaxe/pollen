from MessageBox import MessageBox
import json
import random

class NodeBox(MessageBox):
	'''manages all messages held by node'''
	def __init__(self, messages = [], max_messages = 100):
		super().__init__(messages)
		self.max_messages = max_messages

	def add_message(self, new_message):
		'''add new jsonified message to list'''
		# no longer dejsonifying, doesn't make sense to add the extra step
		# because pgp keys need to be compared as string or bytes anyway
		self.messages.append(new_message)
		return

	def associated_messages(self, public_key):
		'''retrieves and returns list of messages associated with given public key'''
		matching_messages = []
		# print("type of incoming pubkey: ", type(public_key))
		# print("pubkey:\n", public_key)
		for i in reversed(range(len(self.messages))): # loop over all messages backwards
			# print("stored message type: ", type(self.messages[i]))
			# print("stored message: ", self.messages[i])
			message_content = json.loads(self.messages[i]) # unload json into dict
			# being explicit for testing later, bc I can't remember if one needs casting
			message_target = message_content["recipient"]
			# print("type of local pubkey: ", type(message_target))
			# check if each message is intended for given user
			if (public_key == message_target): # if pubkeys match
				# pop out matching messages and add to list created earlier
				matching_messages.append( self.messages.pop(i) )
			# otherwise, move on to next message
		return matching_messages

	def collect_messages(self, public_key, minimum = 5, multiplier = 2):
		'''collect all messages to be sent to a user with given public key'''
		# collect messages actually intended for them into list
		collected_messages = self.associated_messages(public_key)
		# calculate number of extra messages to send to user
		# default min is 5, number extra goes up with increased usage by user
		# by default, it collects 2 * the amount sent to them
		num_extra_messages = max(minimum, (multiplier * len(collected_messages)))
		# list of messages for popping off of (first way that came to mind)
		temp_messages = self.messages
		for i in range(num_extra_messages):
			# as long as there are messages left, collect num of extra messages
			if (len(temp_messages) != 0):
				# randomly choose an index
				selected_index = random.randint(0, (len(temp_messages) - 1))
				# pop it out and append it to collected messages (to be sent to user)
				collected_messages.append(temp_messages.pop(selected_index))
			else: # no extra messages left to be chosen from
				pass
		return collected_messages

	def prune_messages(self):
		'''trim messages list down to maximum allowed size'''
		# if number of messages is greater than allowed
		if (self.max_messages < len(self.messages)):
			# calculate difference
			diff = (len(self.messages) - self.max_messages)
			# delete difference, starting from the oldest
			self.messages = self.messages[diff:] # slice off oldest from front
		# otherwise do nothing
		return

if __name__ == '__main__':
	max_messages = 5
	messages = ["a", "b", "c", "d", "e", "f", "g", "h", "i"]
	new_nodebox = NodeBox(messages, max_messages)
	# collected_messages = new_nodebox.collect_messages("lmao")
	# print("collected messages: ", collected_messages)
	new_nodebox.prune_messages()
	print("remaining messages: ", new_nodebox.messages)
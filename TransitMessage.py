import pgpy
import json
from LocalMessage import LocalMessage
from Pocket import Pocket

class TransitMessage:
	'''storage format of all messages in transit'''
	def __init__(self, local_message = None, password = None, jsoned_message = None):
		# if importing an existing TransitMessage
		if (jsoned_message != None):
			# un-json data and grab values from dict, convert to proper type
			unjsoned_data = json.loads(jsoned_message)
			self.pgp_message = pgpy.PGPMessage.from_blob(unjsoned_data["pgp_message"])
			# https://pgpy.readthedocs.io/en/latest/api.html#pgpy.PGPKey.from_blob
			self.sender, _ = pgpy.PGPKey.from_blob(unjsoned_data["sender"])
			self.recipient, _ = pgpy.PGPKey.from_blob(unjsoned_data["recipient"])
		# if creating a new TransitMessage
		elif ((local_message != None) and (password != None)):
			self.pgp_message = local_message.prep(password) # prep LocalMessage
			if local_message.was_sent(): # if self is sender
				self.sender = Pocket().public_key() # get own pub key
				self.recipient = local_message.get_peer()
			else: # self is recipient
				self.sender = local_message.get_peer()
				self.recipient = Pocket().public_key() # get own pub key
		# some sort of mistake with arguments
		else:
			# raise error and show faulty arguments
			error_text = "given args: " + str(local_message) + ", " + password + ", " 
			error_text += jsoned_message # yeahh sorry there's a better way
			raise ValueError(error_text)

	def jsonify(self):
		'''returns self as strings within json in preparation for exchange'''
		# https://www.programiz.com/python-programming/json
		# make dict to store stringified fields
		transit_json = {
			"pgp_message"	: str(self.pgp_message),
			"sender"		: str(self.sender),
			"recipient"		: str(self.recipient)
		}
		return json.dumps(transit_json) # return dict as json

	def for_self(self):
		'''returns bool of whether recipient is self'''
		# direct comparison was causing issues--I think it was checking references
		own_pubkey = bytes(Pocket().public_key()) # grab own public key
		return (own_pubkey == bytes(self.recipient))

	def detransit(self, password):
		'''returns LocalMessage version of self'''
		contents = Pocket().raw_decrypt(self.pgp_message, password)
		# should probably make for_self into from_self to be consistent
		if self.for_self(): # if self is recipient
			peer = self.sender # peer sent it
			sent = False
		else: # if self sent it
			peer = self.recipient # peer will receive it
			sent = True
		return LocalMessage(contents, peer, sent)

if __name__ == '__main__':
	# test code from LocalMessage (surely there's a better way, sorry)
	message = "hey, do messages work?"
	password = "fake_password"
	peer = Pocket().public_key() # pubkey from local dir
	sent = False
	new_message = LocalMessage(message, peer, sent)
	# prepped_message = new_message.prep(password)
	# print("type: ", type(prepped_message))
	# make new TransitMessage using LocalMessage
	new_transit = TransitMessage(new_message, password)
	jsonified_transit = new_transit.jsonify()
	print("jsonified_transit type: ", type(jsonified_transit))
	print( jsonified_transit )
	# recreate TransitMessage using jsonified TransitMessage
	second_transit = TransitMessage(jsoned_message = jsonified_transit)
	print("pgp_message type: ", type(second_transit.pgp_message))
	print("sender type: ", type(second_transit.sender))
	print("recipient type: ", type(second_transit.recipient))
	# check if self is recipient
	# are_they_the_same = (bytes(second_transit.sender) == bytes(second_transit.recipient))
	# print("they are the same: ", are_they_the_same)
	for_me = new_transit.for_self()
	print("I am the intended recipient: ", for_me)
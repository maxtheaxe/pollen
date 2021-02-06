import pgpy
from datetime import datetime
from Pocket import Pocket

class LocalMessage:
	'''storage format of all local messages'''
	def __init__(self, message, peer, sent):
		self.message = message # plaintext message body
		self.peer = peer # public key of other person
		self.sent = sent # bool of whether it was sent (false == received)
		self.inception = datetime.now() # when it was sent or received

	def __str__(self):
		'''returns readable message representation'''
		# https://realpython.com/lessons/how-and-when-use-str/
		readable = self.inception.strftime("[%m/%d/%Y, %H:%M:%S] ") # add timestamp
		if self.was_sent(): # i said it
			readable += "me:   "
		else: # they said it
			readable += "them: "
		readable += self.message # add body of message
		return readable

	def get_message(self):
		'''returns plaintext body of message'''
		return self.message

	def was_sent(self):
		'''returns bool of whether it was sent (false == received)'''
		return self.sent

	def get_peer(self):
		'''returns peer associated with message'''
		return self.peer

	def get_inception(self):
		'''returns datetime obj of when it was sent or received'''
		return self.inception

	def prep(self, password):
		'''returns signed, encrypted message'''
		# create PGPMessage obj
		pgp_message = pgpy.PGPMessage.new(self.message)
		# sign message using priv key
		signed_message = Pocket().sign_message(pgp_message, password)
		# encrypt signed message using peer's pub key
		encrypted_message = self.peer.encrypt(signed_message)
		return encrypted_message

if __name__ == '__main__':
	message = "hey, do messages work?"
	password = "fake_password"
	# peer = pgpy.PGPKey.from_file("pgp_keys.asc") # pubkey from local dir
	peer = Pocket().public_key() # pubkey from local dir
	print("type: ", type(peer))
	sent = False
	new_message = LocalMessage(message, peer, sent)
	print(new_message)
	prepped_message = new_message.prep(password)
	print(prepped_message)
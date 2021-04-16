import pgpy
from datetime import datetime
from Pocket import Pocket
import json

class LocalMessage:
	'''storage format of all local messages'''
	def __init__(self, message, peer, sent):
		self.message = message # plaintext message body
		print
		if type(peer) == str:
			self.peer, _ = pgpy.PGPKey.from_blob(peer) # parse PGP key if given as str
		else:
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

	def __getstate__(self):
		'''helper method that allows this class to be pickled'''
		# ref: https://stackoverflow.com/a/41754104
		pickled_self = {
			'message' : self.message,
			'peer' : str(self.peer), # stringify the key!
			'sent' : self.sent,
			'inception' : self.inception.strftime("%Y.%m.%d.%H.%M.%S")
		}
		return pickled_self

	def __setstate__(self, pickled_self):
		'''helper method that allows this class to be unpickled'''
		self.message = pickled_self['message']
		self.peer, _ = pgpy.PGPKey.from_blob(pickled_self['peer'])
		self.sent = pickled_self['sent']
		pd = pickled_self['inception'].split('.') # parsed datetime
		self.inception = datetime(int(pd[0]), int(pd[1]), int(pd[2]), 
			int(pd[3]), int(pd[4]), int(pd[5]))
		return

if __name__ == '__main__':
	# message data
	message = "hey, do messages work?"
	password = "fake_password"
	sent = False
	# peer = pgpy.PGPKey.from_file("pgp_keys.asc") # pubkey from local dir
	peer = Pocket().public_key() # pubkey from local dir
	# print("state: ", peer.__getstate__())
	# pickle testing (just for testing which types have pickle issues)
	import pickler as pr
	var_name = 'new_message'
	og_init = " = " + "LocalMessage(message, peer, sent)"
	if pr.is_pickled(var_name):
		exec(var_name + " = pr.get_pickled(var_name)")
	else:
		exec(var_name + og_init)
		pr.pickle_it(var_name, eval(var_name))
	# new_message.__getstate__()
	# print("type: ", type(peer))
	print(new_message)
	prepped_message = new_message.prep(password)
	print(prepped_message)
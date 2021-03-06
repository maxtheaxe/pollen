import pgpy
from pgpy.constants import PubKeyAlgorithm, KeyFlags, HashAlgorithm, SymmetricKeyAlgorithm, CompressionAlgorithm
import os.path
from os import path

class Pocket:
	'''handles everything that has to do with the user's primary key'''
	def __init__(self, key = None, name = None, password = None, filename = "pollen_key.asc"):
		# # if key not passed as arg, should just check if exists in local dir
		if ((key == None) and (path.exists(filename))):
			key, _ = pgpy.PGPKey.from_file(filename) # using key from local storage instead
		# if ((key == None) and (name == None) and (password == None)): # check if all None
		# 	# may remove later, depending on how key is stored
		# 	raise ValueError("all arguments cannot be None")
		elif ((name != None) and (password != None)): # if name and pw are given
			key = self.create_key(name, password, filename)
		elif not any([key, name, password]): # if all args none, make new key w defaults
			key = self.create_key(name = "fake_user",
			                      password = "fake_password", filename = "fake_key.asc")
		else: # some sort of mistake with arguments
			# raise error and show faulty arguments
			error_text = "given args: " + str(key) + ", " + name + ", " + password
			raise ValueError(error_text)
		self.key = key # store key in object
		# self.password = password # not sure if this is how I should be using context mgr

	# def __enter__(self):
	# 	'''starts context manager given password'''
	# 	# https://www.geeksforgeeks.org/context-manager-in-python/
	# 	# really unsure about whether this is how you use context manager
	# 	return self.key.unlock(self.password)

	# def __exit__(self, exc_type, exc_value, exc_traceback):
	# 	'''theoretically ends context manager?'''
	# 	# https://www.geeksforgeeks.org/context-manager-in-python/
	# 	return

	def create_key(self, name, password, filename):
		'''returns a new PGP key given a desired name and password'''
		# make new primary key (RSA)
		key = pgpy.PGPKey.new(PubKeyAlgorithm.RSAEncryptOrSign, 4096)
		# make uid with given name to make key usable
		uid = pgpy.PGPUID.new(name)
		# add uid to key with defaults similar to GnuPG 2.1.x (no exp or keyserv)
		key.add_uid(uid, usage={KeyFlags.Sign, KeyFlags.EncryptCommunications, KeyFlags.EncryptStorage},
					hashes=[HashAlgorithm.SHA256, HashAlgorithm.SHA384, HashAlgorithm.SHA512, HashAlgorithm.SHA224],
					ciphers=[SymmetricKeyAlgorithm.AES256, SymmetricKeyAlgorithm.AES192, SymmetricKeyAlgorithm.AES128],
					compression=[CompressionAlgorithm.ZLIB, CompressionAlgorithm.BZ2, CompressionAlgorithm.ZIP, CompressionAlgorithm.Uncompressed])
		# encrypt key with given password
		key.protect(password, SymmetricKeyAlgorithm.AES256, HashAlgorithm.SHA256)
		# store key to file in local dir
		key_file = open(filename, "w")
		key_file.write(str(key))
		key_file.close()
		# also save public key
		public_filename = ("public_" + filename)
		self.save_public_key(key, public_filename)
		return key # return newly-minted key

	def public_key(self):
		'''returns public key associated with primary key'''
		return self.key.pubkey

	def save_public_key(self, key, filename):
		'''saves public key to local dir'''
		key_file = open(filename, "w")
		key_file.write(str(key.pubkey))
		key_file.close()
		return

	def sign_message(self, message, password):
		'''takes in PGP message and returns signed version using private key'''
		with self.key.unlock(password):
			message |= self.key.sign(message)
			return message

	def decrypt_message(self, message, password):
		'''takes in encrypted message and returns decrypted version'''
		with self.key.unlock(password): # using password to unlock priv key
			return self.key.decrypt(message) # return decrypted pgp message

	def raw_decrypt(self, message, password):
		'''takes in encrypted message and returns string contents of decrypted version'''
		with self.key.unlock(password): # using password to unlock priv key
			return self.key.decrypt(message).message # return decrypted *contents*

	def __getstate__(self):
		'''helper method that allows this class to be pickled'''
		# ref: https://stackoverflow.com/a/41754104
		# need to get rid of this AND current init save method
		return str(self.key)

	def __setstate__(self, pickled_self):
		'''helper method that allows this class to be unpickled'''
		self.key, _ = pgpy.PGPKey.from_blob(pickled_self)
		# print("key:\n", self.key)
		return

if __name__ == '__main__':
	filename = "pollen_key.asc"
	password = "fake_password"
	new_key = Pocket(name = "max", password = password, filename = filename)
	raw_message = "here is a test message"
	pgp_message = pgpy.PGPMessage.new(raw_message)
	# with new_key:
	signed_message = new_key.sign_message(pgp_message, password)
	encrypted_message = new_key.public_key().encrypt(signed_message)
	# encrypted_message = new_key.public_key().encrypt(pgp_message)
	decrypted_message = new_key.decrypt_message(encrypted_message, password)
	print("\nsigned message:\n", signed_message)
	print("\nencrypted message:\n", encrypted_message)
	print("\ndecrypted message:\n", decrypted_message)
	print("\ndecrypted message contents:\n", decrypted_message.message)
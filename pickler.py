# pickles different types of data for basic data persistence
import pickle

def is_pickled(variable_name):
	'''returns bool of whether pickle of given filename exists'''
	full_filename = variable_name + ".pickle"
	try: # lame data persistence
		open(full_filename, 'rb') # try opening it
		return True
	except FileNotFoundError: # file doesnt exist
		return False

def get_pickled(variable_name):
	'''attempts to return variable that was previously pickled'''
	if not is_pickled(variable_name):
		return False
	else:
		full_filename = variable_name + ".pickle"
		with open(full_filename, 'rb') as pfile:
			unpickled_variable = pickle.load(pfile) # load in var
		return unpickled_variable

def pickle_it(variable_name, variable):
	'''pickle a variable using its own name as a filename'''
	# we can return whether pickle already existed
	was_pickled = is_pickled(variable_name)
	full_filename = variable_name + ".pickle"
	with open(full_filename, 'wb') as pfile:
		pickle.dump(variable, pfile) # load in var
	return was_pickled
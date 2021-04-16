# pollen.im gui (main.py) by max
import pickle
import re  # review: to be removed later
from Client import Client
# normal imports
from kivy.app import App
from kivy.lang import Builder  # remove later
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.scatter import Scatter
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty
from kivy.uix.recycleview import RecycleView
# changing window size: https://stackoverflow.com/a/51809114/4513452
from kivy.core.window import Window

Window.size = (375, 667)


# create helper widgets
class ImageButton(ButtonBehavior, Image):
	'''image that can also be clicked like a button, with iname property as well'''
	# ref: https://stackoverflow.com/a/33489264
	pass


class NamedImageButton(ImageButton):
	'''image that can also be clicked like a button, with iname property as well'''

	def __init__(self, iname, **kwargs):
		super(ImageButton, self).__init__(**kwargs)
		self.iname = iname

	pass


class BoxButton(ButtonBehavior, BoxLayout):
	'''a box layout that also allows onpress events'''
	pass


# noinspection SpellCheckingInspection
class ConvoItem(BoxButton):
	'''a mini preview version of a conversation'''

	# contact_name = StringProperty('') # blank string is default # review: does this NEED to be a kivy prop?
	# contact = StringProperty('') # review: does this NEED to be a kivy prop?
	def __init__(self, **kwargs):
		super(ConvoItem, self).__init__(**kwargs)
		self.contact_name = ''
		self.contact = ''

	def set_contact_name(self, given_name):
		'''sets the contact_name property to a given string'''
		self.contact_name = given_name
		return

	def select_convo(self, chosen_contact=None):
		'''switch to the chat screen for a given contact'''
		if chosen_contact is None:  # review (janky)
			chosen_contact = self.contact
		self.parent.parent.parent.parent.manager.screens[4].set_contact(chosen_contact)
		self.parent.parent.parent.parent.manager.current = 'convo'  # swap to convo screen
		return

	pass


class Message(BoxButton):
	'''parent message type'''
	message_text = StringProperty('')  # blank string is default
	sent = BooleanProperty(True)  # blank string is default
	pass


class ClearMessage(Message):
	'''plaintext view of message'''
	pass


class InMessage(Message):
	'''inbox view of message'''
	pass


class OutMessage(Message):
	'''outbox view of message'''
	pass


class HeaderBar(BoxLayout):
	'''box that contains a back button and screen title'''
	title = StringProperty('')  # blank string is default
	pass


class ConvoBox(RecycleView):
	'''box that contains a scrollable section of conversations'''

	# ref: https://www.geeksforgeeks.org/python-recycleview-in-kivy/
	def __init__(self, **kwargs):
		super(ConvoBox, self).__init__(**kwargs)
		self.data = []
		return

	def populate_convos(self):
		'''populate home screen with conversations'''
		# handle no messages exist
		client_instance = self.parent.parent.manager.screens[0].client_instance
		if client_instance.conversation_manager.count_conversations() != 0:
			for contact in client_instance.conversation_manager.conversations:
				friendly_name = client_instance.conversation_manager.conversations[contact].friendly_name
				self.data.append({'contact_name': friendly_name, 'contact': contact})
		return

	pass


class MessageBoxHeader(BoxLayout):
	pass


class MessageBox(RecycleView):
	'''basic building block for message boxes'''
	# if i want to use this widget elsewhere and pass in a property at instantiation
	# need to define a kivy property as such:
	title = StringProperty('')  # blank string is default

	def __init__(self, **kwargs):
		super(MessageBox, self).__init__(**kwargs)
		self.data = []
		return

	def set_contact(self, chosen_contact_key):  # needs massive cleaning up; just for testing
		'''sets the current contact to the given (string) key'''
		self.data = []  # wipe existing elements
		client_instance = self.parent.parent.manager.screens[0].client_instance
		contact_key = str(chosen_contact_key)
		contact = client_instance.conversation_manager.conversations[contact_key]
		for message_item in contact.messages:
			self.data.append({'message_text': message_item.message, 'sent': message_item.sent})
		return

	def set_target(self, location):
		'''sets the current location to the selection (inbox/outbox)'''
		self.data = []  # wipe existing elements
		client_instance = self.parent.parent.manager.screens[0].client_instance
		# no friendly names for TransitMessage type--will generate dynamically now, but
		# should think about alternatives
		if location == 'inbox':
			target = client_instance.inbox
			for message_item in target.messages:
				friendly_name = self.create_name(message_item.sender)
				self.data.append({'message_text': friendly_name, 'sent': False})
		else:
			target = client_instance.outbox
			for message_item in target.messages:
				friendly_name = self.create_name(message_item.recipient)
				self.data.append({'message_text': friendly_name, 'sent': True})
		return

	def create_name(self, pgp_key):  # review: duplicate from Conversation class, improve
		'''returns 8 character-long alpha-numeric sequence from given pgp key'''
		# https://www.programiz.com/python-programming/regex#python-regex
		pattern = '[a-zA-Z0-9]{25}'
		name_found = re.search(pattern, str(pgp_key))  # search for usable sequence
		if (not name_found):  # if no usable sequence was found
			random_name = "new_peer"  # just use "new_peer" instead
		else:
			random_name = name_found.group()[17:25]  # grab the usable sequence
		return random_name

	pass


# create different screens
class HomeScreen(Screen):

	def __init__(self, **kwargs):
		super(Screen, self).__init__(**kwargs)
		self.client_instance = self.startup()  # creates new instance if doesn't exist

	def startup(self):
		'''perform startup operations'''
		try:  # lame data persistence
			# attempt to open existing pickled (serialized) instance
			with open("client_instance.pickle", 'rb') as pfile:
				return pickle.load(pfile)  # load in saved instance
		except IOError:  # file doesnt exist
			with open("client_instance.pickle", 'wb') as pfile:
				new_client = Client()
				pickle.dump(new_client, pfile)  # dump new instance for later
				return new_client
		pass

	def box_navigate(self, location):
		'''navigate to a selected box'''
		if location == 'inbox':
			self.manager.screens[1].set_target(location)
		else:
			self.manager.screens[2].set_target(location)
		self.manager.current = location  # swap to selected box screen
		return

	def refresh(self):
		'''update messages in client, then save state'''
		self.client_instance.update_messages()  # exchange messages with node, if possible
		# dump self
		return

	pass


class ComposeScreen(Screen):
	pass


class BoxScreen(Screen):
	pass


class ConversationScreen(BoxScreen):
	# ref: https://stackoverflow.com/a/50294037/4513452
	message_box = ObjectProperty(None)  # so we can call child methods later

	def set_contact(self, contact):
		self.message_box.set_contact(contact)
		return

	pass


class InboxScreen(BoxScreen):
	# ref: https://stackoverflow.com/a/50294037/4513452
	message_box = ObjectProperty(None)  # so we can call child methods later

	def set_target(self, location):
		self.message_box.set_target(location)
		return

	pass


class OutboxScreen(BoxScreen):
	# ref: https://stackoverflow.com/a/50294037/4513452
	message_box = ObjectProperty(None)  # so we can call child methods later

	def set_target(self, location):
		self.message_box.set_target(location)
		return

	pass


class SettingsScreen(Screen):
	title = StringProperty('')  # blank string is default
	pass


class SetupScreen(Screen):
	pass


# create screen manager
class ScreenManagement(ScreenManager):
	# ref: https://kivy.org/doc/stable/api-kivy.uix.screenmanager.html
	# ref: https://stackoverflow.com/a/38110500
	pass


# run app
class PollenApp(App):
	def build(self):
		return ScreenManagement()


if __name__ == '__main__':
	PollenApp().run()

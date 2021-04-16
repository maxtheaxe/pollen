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
from kivy.clock import Clock
# changing window size: https://stackoverflow.com/a/51809114/4513452
from kivy.core.window import Window
# from kivy_garden.zbarcam import ZBarCam

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


class HighlightTextInput(TextInput):
	'''TextInput box that highlights all contents when pressed'''

	# ref: https://stackoverflow.com/a/51453778
	def on_touch_down(self, touch):
		Clock.schedule_once(lambda dt: self.select_all())
		TextInput.on_touch_down(self, touch)

	pass


class BoxButton(ButtonBehavior, BoxLayout):
	'''a box layout that also allows onpress events'''
	pass


# noinspection SpellCheckingInspection
class ConvoItem(BoxButton):
	'''a mini preview version of a conversation'''

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

	def get_arrow(self):
		'''returns appropriate arrow based on whether it was sent or not'''
		if self.sent:
			return "images/double_left_arrow.png"
		else:
			return "images/double_right_arrow.png"
		pass

	def alignment(self):
		'''returns appropriate alignment based on whether it was sent or not'''
		if self.sent:
			return "right"
		else:
			return "left"
		pass

	def get_color(self):
		'''returns appropriate color based on whether it was sent or received'''
		if self.sent:
			return (255, 255, 255)
		else:
			return (0, 0, 0)
		pass

	def get_text_color(self):
		'''returns appropriate color based on whether it was sent or received'''
		if not self.sent:
			return (255, 255, 255)
		else:
			return (0, 0, 0)
		pass

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
		self.save_state()  # dump self
		return

	def save_state(self):
		'''save serialized version (pickle) of self as form of basic persistence'''
		with open("client_instance.pickle", 'wb') as pfile:
			pickle.dump(self.client_instance, pfile)  # dump current instance for later
		return

	pass


class ComposeScreen(Screen):
	def send_message(self, recipient_key, message_body):
		'''send new message with given inputs'''
		try:
			self.manager.screens[0].client_instance.compose_message(recipient_key, message_body)
			self.manager.screens[0].save_state()
			# only wipes text input upon successful message send
			self.ids.recipient_key.text = ""
			self.ids.recipient_key.hint_text = "Recipient PGP Key"
			self.ids.message_body.text = ""
			self.manager.current = 'home'  # message sent, return to home screen
		except:  # invalid pgp key for recipient
			self.ids.recipient_key.text = ""
			self.ids.recipient_key.hint_text = "invalid recipient--please retry"
		return

	def pass_recipient(self, peer_key):
		'''set recipient field for new message'''
		self.ids.recipient_key.text = peer_key  # pass given key
		self.manager.current = 'compose'
		return

	pass


class BoxScreen(Screen):
	pass


class ConversationScreen(BoxScreen):
	# ref: https://stackoverflow.com/a/50294037/4513452
	message_box = ObjectProperty(None)  # so we can call child methods later
	contact = StringProperty() # so we can call compose directly later

	def set_contact(self, contact):
		self.message_box.set_contact(contact)
		self.title = self.create_name(contact)
		self.contact = contact
		return

	def start_message(self):
		'''open message compose screen with current peer'''
		self.manager.screens[3].pass_recipient(self.contact) # pass peer key to compose
		return

	def create_name(self, pgp_key):  # review: double duplicate from Conversation class, improve
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


class ScanScreen(Screen):
	def scan_qr(self):
		'''passes scanned qr into compose screen'''
		self.manager.screens[3].pass_recipient(self.qr_data)  # pass peer key to compose
	pass


class StartScreen(Screen):
	def handle_key(self):
		'''handle the creation/unlocking of pgp key'''
		return
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

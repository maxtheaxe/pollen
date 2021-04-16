# pollen.im gui (main.py) by max
from Client import Client
# normal imports
from kivy.app import App
from kivy.lang import Builder # remove later
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

# track client instance globally (def not right way to do this, but until db is set up)
global client_instance
# pickle testing (just for testing which types have pickle issues)
import pickler as pr
var_name = 'client_instance'
og_init = " = " + "Client()"
if pr.is_pickled(var_name):
	exec(var_name + " = pr.get_pickled(var_name)")
else:
	exec(var_name + og_init)
	pr.pickle_it(var_name, eval(var_name))
# convo testing
# global current_convo
# for contact in client_instance.conversation_manager.conversations:
# 	current_convo = contact_key = str(client_instance.conversation_manager.conversations[contact].peer)
# 	# current_convo = client_instance.conversation_manager.conversations[contact]

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

class ConvoItem(BoxButton):
	'''a mini preview version of a conversation'''
	# contact_name = StringProperty('') # blank string is default # review: does this NEED to be a kivy prop?
	# contact = StringProperty('') # review: does this NEED to be a kivy prop?
	def __init__(self, **kwargs):
		super(ConvoItem, self).__init__(**kwargs)
		self.contact_name = ''
		self.contact = ''
	def set_contact_name(given_name):
		'''sets the contact_name property to a given string'''
		self.contact_name = given_name
	def select_convo(self, chosen_contact = None):
		'''switch to the chat screen for a given contact'''
		if chosen_contact == None: # review (janky)
			chosen_contact = self.contact
		# print("chosen contact: ", chosen_contact)
		self.parent.parent.parent.parent.manager.screens[4].set_contact(chosen_contact)
		self.parent.parent.parent.parent.manager.current = 'convo' # swap to convo screen
		# print(self.chosen_contact)
		# global current_convo
		# current_convo = self.contact
		# print(current_convo)
		# self.parent.parent.parent.parent.manager.current.set_contact()
		# MessageBox.set_contact()
		# ConversationScreen.set_contact(chosen_contact) # pass contact key string
	pass

class Message(BoxButton):
	'''parent message type'''
	message_text = StringProperty('') # blank string is default
	sent = BooleanProperty(True) # blank string is default
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
	title = StringProperty('') # blank string is default
	pass

class ConvoBox(RecycleView):
	'''box that contains a scrollable section of content (either messages or conversations)'''
	# ref: https://www.geeksforgeeks.org/python-recycleview-in-kivy/
	def __init__(self, **kwargs): 
		super(ConvoBox, self).__init__(**kwargs)
		self.data = []
		global client_instance
		# handle no messages exist
		if client_instance.conversation_manager.count_conversations() != 0:
			for contact in client_instance.conversation_manager.conversations:
				friendly_name = client_instance.conversation_manager.conversations[contact].friendly_name
				self.data.append({'contact_name': friendly_name, 'contact': contact})
	pass

class MessageBoxHeader(BoxLayout):
	pass

class MessageBox(RecycleView):
	'''basic building block for message boxes'''
	# if i want to use this widget elsewhere and pass in a property at instantiation
	# need to define a kivy property as such:
	title = StringProperty('') # blank string is default
	def __init__(self, **kwargs):
		super(MessageBox, self).__init__(**kwargs)
		self.data = []
		return

	def set_contact(self, chosen_contact_key): # needs massive cleaning up; just for testing
		'''sets the current contact to the given (string) key'''
		contact_key = str(chosen_contact_key)
		contact = client_instance.conversation_manager.conversations[contact_key]
		self.data = []
		for message_item in contact.messages:
			self.data.append({'message_text': message_item.message, 'sent': message_item.sent})
		return

	def set_target(self, location):
		return
	pass

# create different screens
class HomeScreen(Screen):
	# def __init__(self, **kwargs):
	# 	super(Screen, self).__init__(**kwargs)
	pass

class ComposeScreen(Screen):
	pass

class BoxScreen(Screen):
	pass

class ConversationScreen(BoxScreen):
	# chosen_contact = StringProperty('') # review: might not be necessary, can't remember
	# ref: https://stackoverflow.com/a/50294037/4513452
	message_box = ObjectProperty(None) # so we can call child methods later
	def set_contact(self, contact):
		chosen_contact = contact # maybe remove
		# print("contact: ", contact)
		# now call the set contact method within message box
		self.message_box.set_contact(contact)
		return
	pass

class InboxScreen(BoxScreen):
	pass

class OutboxScreen(BoxScreen):
	pass

class SettingsScreen(Screen):
	title = StringProperty('') # blank string is default
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
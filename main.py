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
from kivy.properties import StringProperty, BooleanProperty
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

# create helper widgets
class ImageButton(ButtonBehavior, Image):
	'''image that can also be clicked like a button, with iname property as well'''
	# ref: https://stackoverflow.com/a/33489264
class NamedImageButton(ImageButton):
	'''image that can also be clicked like a button, with iname property as well'''
	def __init__(self, iname, **kwargs):
		super(ImageButton, self).__init__(**kwargs)
		self.iname = iname
class BoxButton(ButtonBehavior, BoxLayout):
	'''a box layout that also allows onpress events'''
	pass
class ConvoItem(BoxButton):
	'''a mini preview version of a conversation'''
	contact_name = StringProperty('') # blank string is default
	contact = StringProperty('')
	def set_contact_name(given_name):
		'''sets the contact_name property to a given string'''
		self.contact_name = given_name
	pass
class Message(BoxButton):
	'''parent message type'''
	message_text = StringProperty('') # blank string is default
	sent = StringProperty('') # blank string is default
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
class ContentBox(RecycleView):
	'''box that contains a scrollable section of content (either messages or conversations)'''
	# ref: https://www.geeksforgeeks.org/python-recycleview-in-kivy/
	def __init__(self, **kwargs): 
		super(ContentBox, self).__init__(**kwargs)
		self.data = []
		global client_instance
		for contact in client_instance.conversation_manager.conversations:
			friendly_name = client_instance.conversation_manager.conversations[contact].friendly_name
			self.data.append({'contact_name': friendly_name, 'contact': contact})
class MessageBox(BoxLayout):
	'''basic building block for message boxes'''
	# if i want to use this widget elsewhere and pass in a property at instantiation
	# need to define a kivy property as such:
	title = StringProperty('') # blank string is default
	# by default, it doesn't wipe old value--prob need to add func to do so,
	# but dynamic updating isn't necessary here
	def __init__(self, **kwargs): 
		super(MessageBox, self).__init__(**kwargs)
		self.data = []
		global client_instance
		# temp contact grab for testing
		test_contact = None
		for contact in client_instance.conversation_manager.conversations:
			test_contact = client_instance.conversation_manager.conversations[contact]
		for message_item in test_contact.messages:
			self.data.append({'message_text': message_item.message, 'sent': message_item.sent})
			print("message text: ", message_item.message)
		return

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
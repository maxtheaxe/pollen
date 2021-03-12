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
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.uix.recycleview import RecycleView


# create helper widgets
class ImageButton(ButtonBehavior, Image):
	'''image that can also be clicked like a button, with iname property as well'''
	# ref: https://stackoverflow.com/a/33489264
class NamedImageButton(ImageButton):
	'''image that can also be clicked like a button, with iname property as well'''
	def __init__(self, iname, **kwargs):
		super(ImageButton, self).__init__(**kwargs)
		self.iname = iname
class ContentBox(RecycleView):
	'''box that contains a scrollable section of content (either messages or conversations)'''
	# ref: https://www.geeksforgeeks.org/python-recycleview-in-kivy/
	def __init__(self, **kwargs): 
		super(ContentBox, self).__init__(**kwargs)
		self.data = [{'text': str(x)} for x in range(20)] 

# create different screens
class HomeScreen(Screen):
	pass
class ComposeScreen(Screen):
	pass
class ConversationScreen(Screen):
	pass
class InboxScreen(ConversationScreen):
	pass
class OutboxScreen(ConversationScreen):
	pass
class SettingsScreen(Screen):
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
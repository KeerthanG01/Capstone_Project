from kivymd.app import MDApp
from locationmapview import LocationMapView
import sqlite3
class MainApp(MDApp):
	connection = None 
	cursor = None
	def on_start(self):
		#Initialize GPS

		#Connect to database 
		self.connection = sqlite3.connect('Locations.db')
		self.cursor = self.connection.cursor()
		# Instantiate SearchPopupMenu 

MainApp().run()
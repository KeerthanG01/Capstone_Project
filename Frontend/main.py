from kivymd.app import MDApp
from locationmapview import LocationMapView
from searchpopupmenu import SearchPopupMenu
import sqlite3
import speech_recognition as sr
class MainApp(MDApp):
	connection = None 
	geo_location = None
	cursor = None
	search_menu = None
	location = None
	def on_start(self):
		#Initialize GPS
		#Connect to database 
		self.connection = sqlite3.connect('Locations.db')
		self.cursor = self.connection.cursor()
		# Instantiate SearchPopupMenu 
		self.search_menu = SearchPopupMenu()
	
	def voice_menu(self):
		my_label = self.root.ids.label
		r = sr.Recognizer()
		try:
			with sr.Microphone() as source:
				r.adjust_for_ambient_noise(source)

				print("Tell me the location:")
				audio = r.listen(source)
				print()
				print("Recognizing.... ")

				self.location = r.recognize_google(audio)
				self.location = str(self.location)
				self.location = self.location[0].upper() + self.location[1:].lower()
				print(self.location)
				my_label.text = self.location
				my_label.size_hint = [0.2,0.1]
				self.geocode(self.location)
		except:
			my_label = self.root.ids.label
			my_label.text = "Data Not Available for " + self.location
			my_label.size_hint = [0.2,0.1]
			print("Retry Again")
	
	def geocode(self,location):
		location = location[0].upper() + location[1:].lower()
		sql_statement = "SELECT * FROM Locations Where Location='%s'"%location
		self.cursor.execute(sql_statement)
		self.geo_location = self.cursor.fetchall()

		if len(self.geo_location) == 0:
			label.text = "Data Not Available for " + location
			my_label.size_hint = [0.2,0.1]
			print("No location data available")

		else:
			self.set_lat_lon(self.geo_location)

	def set_lat_lon(self,geo_location):
		latitude = geo_location[0][1]
		longitude = geo_location[0][2]
		mapview = self.root.ids.mapview
		mapview.center_on(latitude, longitude)
MainApp().run()
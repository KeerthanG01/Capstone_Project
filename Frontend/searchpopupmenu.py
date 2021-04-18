from kivymd.uix.dialog import MDInputDialog
from kivy.app import App 
import sqlite3
class SearchPopupMenu(MDInputDialog):
	title = "Search by Location"
	text_button_ok = "Search"
	def __init__(self):
		super().__init__()
		self.size_hint = [.9,.3]
		self.events_callback = self.callback


	def callback(self,*args):
		location = "" 
		location = self.text_field.text
		if location == "":
			app = App.get_running_app()
			my_label = app.root.ids.label 
			my_label.text = "Location not Provided"
			my_label.size_hint = [0.2,0.1]
			print("Location not provided")
		else:
			location = location[0].upper() + location[1:].lower()
			print(location)
			self.geocode(location)


	def geocode(self,location):
		geo_location = None
		app = App.get_running_app()
		sql_statement = "SELECT * FROM Locations Where Location='%s'"%location
		app.cursor.execute(sql_statement)
		geo_location = app.cursor.fetchall()

		if len(geo_location) == 0:
			app = App.get_running_app()
			my_label = app.root.ids.label 
			my_label.text = "Data not available for " + location 
			my_label.size_hint = [0.2,0.1]
			print("No location data available")

		else:
			my_label = app.root.ids.label 
			my_label.text = location 
			my_label.size_hint = [0.2,0.1]
			self.set_lat_lon(geo_location)

	def set_lat_lon(self,geo_location):
		latitude = geo_location[0][1]
		longitude = geo_location[0][2]
		app = App.get_running_app()
		mapview = app.root.ids.mapview
		mapview.center_on(latitude, longitude)

from kivy_garden.mapview import MapView
from kivy.clock import Clock
from kivy.app import App
from locationmarker import LocationMarker 
class LocationMapView(MapView):
	get_locations_timer = None 
	location_names = [] #acts as a global cache 
	def start_getting_locations_in_fov(self):
		try:
			self.get_locations_timer.cancel()

		except:
			pass
		self.get_locations_timer = Clock.schedule_once(self.get_locations_in_fov,1)

	def get_locations_in_fov(self,*args):
		min_lat,min_lon,max_lat,max_lon = self.get_bbox()
		app = App.get_running_app()
		sql_statement = "SELECT * FROM Locations WHERE Latitude > %s AND Latitude < %s AND Longitude > %s AND Longitude < %s"%(min_lat,max_lat,min_lon,max_lon)
		app.cursor.execute(sql_statement)
		locations = app.cursor.fetchall()
		print(locations)
		for location in locations:
			location_name = location[0]
			if location_name in self.location_names:
				continue
			else:
				self.add_location(location)

	def add_location(self,location):
		lat,lon = location[1],location[2]
		marker = LocationMarker(lat=lat,lon=lon,source='m_1.png')
		marker.location_name =location
		self.add_widget(marker)

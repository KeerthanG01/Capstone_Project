from kivy_garden.mapview import MapMarkerPopup
from locationpopupmenu import LocationPopupMenu
class LocationMarker(MapMarkerPopup):
	location_name = []
	def on_release(self):
		menu=LocationPopupMenu(self.location_name)
		menu.size_hint = [.8,.9]
		menu.open()
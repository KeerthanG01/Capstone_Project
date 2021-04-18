from kivymd.uix.dialog import ListMDDialog
import requests
import json
class LocationPopupMenu(ListMDDialog):
	def __init__(self,location_name):
		super().__init__()
		city = location_name[0]
		city =city.lower()
		#set all of the fields of market data 
		header=["Date1","Possibility_of_Rain1","Water_to_be_Irrigated1","Date2","Possibility_of_Rain2","Water_to_be_Irrigated2","Date3","Possibility_of_Rain3","Water_to_be_Irrigated3","Date4","Possibility_of_Rain4","Water_to_be_Irrigated4","Date5","Possibility_of_Rain5","Water_to_be_Irrigated5","Date6","Possibility_of_Rain6","Water_to_be_Irrigated6","Date7","Possibility_of_Rain7","Water_to_be_Irrigated7"]
		URL = "http://127.0.0.1:5000/user/{loc}/{sensor}".format(loc=city,sensor=4)
		#print("URL1:",URL)
		r = requests.get(URL)
		status = r.json()["status"]
		if status == "201":
			URL2 = "http://127.0.0.1:5000/user/{loc}".format(loc=city)
			#print("URL2:",URL2)
			r = requests.get(URL2)
			#print(r.text)
			date = r.json()["Date"]
			rain = r.json()["Rain"]
			water = r.json()["Water"]
			#print(date)
			
		header_value = []
		for i in range(len(date)):
			header_value.append(date[i])
			header_value.append(str(rain[i]))
			header_value.append(str(water[i]))
		
		for i in range(len(header)):
			attribute_name = header[i]
			attribute_value = header_value[i]
			setattr(self,attribute_name,attribute_value)

		
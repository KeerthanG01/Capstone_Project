import speech_recognition as sr
import requests 
import json

def main():
	while(1):
		r = sr.Recognizer()
		with sr.Microphone() as source:
			r.adjust_for_ambient_noise(source)

			print("Tell me the location:")
			audio = r.listen(source)
			print()
			print("Recognizing.... ")

			location = r.recognize_google(audio)
			location = str(location)
			location = location.lower()
			print()

			print(location)
			URL = "http://127.0.0.1:5000/user/{loc}/{sensor}".format(loc=location,sensor=4)
			print("URL1:",URL)
			r = requests.get(URL)
			status = r.json()["status"]
			if status == "201":
				URL2 = "http://127.0.0.1:5000/user/{loc}".format(loc=location)
				print("URL2:",URL2)
				r = requests.get(URL2)
				date = r.json()["Date"]
				rain = r.json()["Rain"]
				water = r.json()["Water"]
				for i in range(len(date)):
					print("Date:",date[i],"  Water:",water[i],"	Rain:",rain[i])
			else:
				print("Retry once again")

		
print("Welcome")
main()
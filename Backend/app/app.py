import flask
import mysql.connector
import requests
import os
import pandas as pd 
import numpy as np
import time 
import datetime
import math
app = flask.Flask(__name__)
Columns=["Date","Tmean","Mean Solar Radiation","Wind Speed","Slope of Saturation Vapor Pressure","Atmospheric Pressure","Psychometric Constant","Delta Term","PSI Term","Temperature Term","Es","Ea","dr","solar_declination","radians","Ws(Sunset Hour Angle)","Ra","Rso","Rns","Rnl","Rn","Rng","ET_rad","ET_Wind","ETo","Pan Evaporation","Probability of Rain","Possiblity of Rain in mm","Predicted Irrigation Water","Predicted Irrigation Water with Rain Factor"]
Initial=["Day","IW/CPE Ratio"]
config = {
		'user': 'root',
		'password':'password',
		'host': 'cloudintegration_db_1',
		'port': '3306',
		'database': 'cities'
		}

@app.route('/user/<city>/<sensor_reading>', methods = ['GET'])
def Evapotranspiration(city,sensor_reading):
	city=city.lower()
	sensor_reading = float(sensor_reading)
	url1 = 'http://api.openweathermap.org/data/2.5/weather?q={}&appid=852da5493a5fce7d30913e63068de668&units=metric'.format(city)
	conn = mysql.connector.connect(**config)
	cursor =conn.cursor()
	res=requests.get(url1)
	if(res.status_code == 200):
				data=res.json()
				filename = city+".csv"
				path ="./"+filename
				if os.path.exists(path)==False:
					sql="insert into rain_information (City,Rainfall) values (%s,%s) on duplicate key update Rainfall= %s"
					val= (city,"0","0")
					cursor.execute(sql,val)
					conn.commit()
					df=pd.DataFrame(columns=Initial)
					li=[]
					for i in range(8):
						li.append(i)
					df['Day']=li
					li.clear()
					for i in range(8):
						df['IW/CPE Ratio'].iloc[i] = 0.85
					df=pd.concat([df,pd.DataFrame(columns=Columns)])
					date=datetime.datetime.today()
					for i in range(0,8):
						date_t= date + datetime.timedelta(days=i)
						df['Date'].iloc[i]=date_t.strftime("%d-%m-%Y")
					df.to_csv(filename,index=False)
				df=pd.read_csv(filename)		
				Rain=0
				x=[]
				lat = data['coord']['lat']
				lon = data['coord']['lon']
				date=datetime.datetime.fromtimestamp(int(data['dt']))
				i=df[df['Date'] == date.strftime("%d-%m-%Y")].index.values
				index=i[0]
				if index > 0 :
					for i in range(0,8):
						date_t= date + datetime.timedelta(days=i)
						df['Date'].iloc[index+i]=date_t.strftime("%d-%m-%Y")

				url2='https://api.jawg.io/elevations?locations='+str(lat)+','+str(lon)+'&access-token=nxVBt8VayKK6bIzzfvk4ntXSIAzadPniwgER1fvwSUckjEQ2cX7rR3v8xcYSsnUX'
				res2=requests.get(url2)
				data2=res2.json()
				sea_level=float(data2[0]['elevation'])
				url3 ='https://api.openweathermap.org/data/2.5/onecall?lat='+ str(lat)+'&lon='+str(lon)+'&exclude=current,minutely,hourly,alerts&appid=852da5493a5fce7d30913e63068de668&units=metric'
				res3=requests.get(url3)
				data3=res3.json()
				#-----------------Step1 : Tmean ------------------------------------------
				for i in range(8):
					temp_low = float(data3['daily'][i]['temp']['min'])
					temp_high = float(data3['daily'][i]['temp']['max'])
					Tmean=(temp_low + temp_high )/2
					#x.append(Tmean)
					Ratio=float(df["IW/CPE Ratio"].iloc[index+i])

					df['Tmean'].iloc[index+i]=Tmean

				#--------------------Step2: Mean Solar Radiation Rs-------------------------------
					#x.append(0)


				#--------------------Step3: Wind Speed--------------------------------------------

					Wind = float(data3['daily'][i]['wind_speed']) * (18/5)
					#height correction formula 
					Wind=(Wind*4.87)/(math.log(67.8*2 -5.42))
					#x.append(Wind)
					df['Wind Speed'].iloc[index+i]=Wind

				#-----------------Step4: Slope of Saturation Vapor Pressure-----------------------
					exp_num= 17.27*Tmean 
					exp_den= (Tmean+237.3)
					exponentterm= math.exp(exp_num /exp_den)
					Delta_numerator = 4098*0.6108*exponentterm
					Delta_denominator=(Tmean+237.3)**2
					Delta = Delta_numerator/Delta_denominator 
					#x.append(Delta)
					df['Slope of Saturation Vapor Pressure'].iloc[index+i]=Delta

				#---------------Step5: Atmospheric Pressure---------------------------------------

					P = int(data3['daily'][i]['pressure'])/10
					#x.append(P)
					df['Atmospheric Pressure'].iloc[index+i]=P
				#--------------Step6: Psychometric Constant---------------------------------------
					Gamma=0.000665*P 
					#x.append(Gamma)
					df['Psychometric Constant'].iloc[index+i]=Gamma


				#-------------Step7: Delta Term---------------------------------------------------
					DT= Delta / (Delta + Gamma*(1+0.34*Wind))
					#x.append(DT)
					df['Delta Term'].iloc[index+i]=DT

				#------------Step8: PSI Term------------------------------------------------------
					PT= Gamma / (Delta + Gamma*(1+0.34*Wind))
					#x.append(PT)
					df['PSI Term'].iloc[index+i]=PT

				#-------------Step9: Temperature Term (TT)----------------------------------------
					TT=  (900 / (Tmean + 273)) *Wind
					df['Temperature Term'].iloc[index+i]=TT

				#-------------Step10: Es----------------------------------------------------------
					Etmax= 0.6108*math.exp( (17.27*temp_high) / (temp_high + 237.3) )
					Etmin= 0.6108*math.exp( (17.27*temp_low) / (temp_low + 237.3) )
					Es = (Etmax + Etmin)/2 
					#x.append(Es)
					df['Es'].iloc[index+i]=Es

				#------------Step11: Ea-----------------------------------------------------------

					RHmean = int(data3['daily'][i]['humidity'])
					Ea = (RHmean * Es)/100
					#x.append(Ea)
					df['Ea'].iloc[index+i]=Ea

				#-----------Step12: dr and solar_declination ---------------------------------------
					date=datetime.datetime.fromtimestamp(int(data3['daily'][i]['dt'])).strftime('%d-%m-%Y')
					day,month,year=date.split("-")
					date=day+"/"+month+"/"+year
					day=int(day)
					month=int(month)
					year=int(year)

					days = [31, 28, 31, 30, 31, 30, 
							31, 31, 30, 31, 30, 31]
					if (month > 2 and year % 4 == 0 and 
						   (year % 100 != 0 or year % 400 == 0)): 
						day += 1
					month -= 1
					while month > 0: 
					 day = day + days[month - 1]
					 month -= 1 
					day_no=day 

					dr= 1+0.033*math.cos( (2*math.pi*day_no) / 365 )
					solar_declination=0.409*math.sin( ((2*math.pi*day_no) / 365) - 1.39 )
					#x.append(dr)
					df['dr'].iloc[index+i]=dr
					#x.append(solar_declination)
					df['solar_declination'].iloc[index+i]=solar_declination

				#---------Step13: Conversion of latitude degrees in radians --------------------------

					degree = float(data['coord']['lat'])
					degree_decimal = degree% 1
					if degree > 0 :
						degree = degree - degree_decimal + (degree_decimal*100)/60 
					elif degree < 0 : 
						degree = degree - degree_decimal + (degree_decimal*(-100))/60 
					radians = math.pi * degree / 180 
					#x.append(radians)
					df['radians'].iloc[index+i]=radians

				#--------Step14: Sunset hour angle ----------------------------------------------------
					Ws= math.acos(-math.tan(radians)*math.tan(solar_declination))
					#x.append(Ws)
					df['Ws(Sunset Hour Angle)'].iloc[index+i]=Ws

				#-------Step15: Extraterrestrial Radiation (Ra)----------------------------------------
					Ra= 24 * (60 / math.pi) * 0.0820 * dr * ( ( Ws*math.sin(radians)*math.sin(solar_declination)) + (math.cos(radians)*math.cos(solar_declination)*math.sin(Ws) ) )
					#x.append(Ra)
					df['Ra'].iloc[index+i]=Ra
					#calculate mean solar radiation 
					Rs= 0.16* Ra * math.sqrt((temp_high- temp_low))
					#x[1]=Rs
					df['Mean Solar Radiation'].iloc[index+i]=Rs



				#-------Step16: Rso--------------------------------------------------------------------
					lat = data['coord']['lat']
					lon = data['coord']['lon']
					Rso = (0.75 + 2*2.71*(10**-5)*sea_level) * Ra 
					#x.append(Rso)
					df['Rso'].iloc[index+i]=Rso
				#------Step17: Rns---------------------------------------------------------------------
					Rns= (1-0.23)*Rs 
					#x.append(Rns)
					df['Rns'].iloc[index+i]=Rns

				#------Step18: Rnl---------------------------------------------------------------------
					sigma= 4.903 * 10**-9 
					first= ( (temp_high + 273.16)**4 + (temp_low+273.16)**4 )/2 
					second = (0.34 - 0.14*math.sqrt(Ea))
					third= 1.35 * (Rs/Rso) -0.35 
					Rnl=sigma*first*second*third
					#x.append(Rnl)
					df['Rnl'].iloc[index+i]=Rnl


				#------Step19: Rn ----------------------------------------------------------------------
					Rn =Rns-Rnl
					#x.append(Rn)
					df['Rn'].iloc[index+i]=Rn
					Rng=0.408*Rn
					#x.append(Rng)
					df['Rng'].iloc[index+i]=Rng



				#-----------------Final Step------------------------------------------------------------

				#----------------------------Radiation Term (ET_rad)------------------------------------
					ET_rad=DT*Rng
					#x.append(ET_rad)
					df['ET_rad'].iloc[index+i]=ET_rad

				#---------------------------Wind Term (ET_wind)-----------------------------------------
					ET_wind=PT*TT*(Es-Ea)
					#x.append(ET_wind)
					df['ET_Wind'].iloc[index+i]=ET_wind

					ETo = ET_rad + ET_wind 
					#x.append(ETo)
					df['ETo'].iloc[index+i]=ETo

					#x.insert(0,date)

				#------------------------Pan Evaporation,Cumulative Pan Evaporation and RainFall------------------------------------------------
					E = ETo/0.7
					#x.append(E)
					df['Pan Evaporation'].iloc[index+i]=E
					if 'rain' in data3['daily'][i]: 
						Rain = float(data3['daily'][i]['rain'])*float(data3['daily'][i]['pop'])
						df['Probability of Rain'].iloc[index+i] = float(data3['daily'][i]['pop'])
						df['Possiblity of Rain in mm'].iloc[index+i]=Rain
						sql=("update rain_information set Rainfall= Rainfall + %s where City=%s")
						val=(str(Rain),city)
						cursor.execute(sql,val)
						conn.commit()
					else:
						Rain=0
						df['Possiblity of Rain in mm'].iloc[index+i]=0 		
						df['Probability of Rain'].iloc[index+i] = 0
					IW = Ratio*E 
					print("Actual Irrigation Water: ", IW)
					df['Predicted Irrigation Water'].iloc[index+i]=IW
					sql="select Rainfall from rain_information where City=%s"
					val=(city,)
					cursor.execute(sql,val)
					Excess_Rain=cursor.fetchone()
					Excess_Rain = float(Excess_Rain[0])
					if Excess_Rain > IW : 
						Excess_Rain = Excess_Rain - IW 
						sql=("update rain_information set Rainfall=Rainfall - %s where City=%s")
						val=(str(IW),city)
						cursor.execute(sql,val)
						conn.commit()
						IW=0
					else:
						IW = IW - Excess_Rain
				#	if IW < 0 :
				#		IW =0
					IW = IW - sensor_reading 

					if IW < 0:
						df["Predicted Irrigation Water with Rain Factor"].iloc[index+i]= 0
					else:
						df["Predicted Irrigation Water with Rain Factor"].iloc[index+i]= IW
				
					df.to_csv(filename,index=False)

				dic = {} 
				dic["status"] = "201"
				return dic
				#---------------------------Updating the CSV File---------------------------------------
					#x.clear()

	else:
		print("Location Data not Present")
		dic = {} 
		dic["status"] = "404"
		return dic

@app.route('/user/<city>', methods = ['GET'])
def get_info(city):
	city=city.lower()
	filename = str(city)  + ".csv"
	if os.path.exists(filename):
		df = pd.read_csv(filename)
		df1 = df[["Date","Possiblity of Rain in mm","Predicted Irrigation Water with Rain Factor"]]
		df1=df1.dropna()
		date = df1.iloc[:,0].tolist()
		rain=df1.iloc[:,1].tolist()
		rain_infor = df1.iloc[:,2].tolist()
		dic = {}
		dic["Date"] = date
		dic["Rain"] = rain
		dic["Water"] = rain_infor
		return dic
	else:
		dic = {} 
		dic["status"] = "404"
		return dic
if __name__=="__main__":
	app.run(host='0.0.0.0', threaded=True)
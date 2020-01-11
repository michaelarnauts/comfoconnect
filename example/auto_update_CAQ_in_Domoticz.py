#!/usr/bin/python

import sys
import subprocess
import datetime
import time
from configparser import ConfigParser
import argparse
from pycomfoconnect import *
import requests

# provide config file with setup information for Domoticz and ComfoConnectLAN
FILENAME = sys.argv[1] if len(sys.argv) > 1 else 'config.ini'
CONFIG = ConfigParser()
CONFIG.read(FILENAME)
try:
	DOMO = CONFIG['DOMOTICZ']
	CAQ = CONFIG['COMFOAIRQ']
	DEVICE = CONFIG['DEVICE']
except (KeyError, TypeError):
	raise Exception('Config file is unreadable or incomplete.')
DOMO['URL'] = 'http://'+DOMO['SERVER']+'/json.htm?'

# table to store last value received from CAQ
CAQ_pdid = 300*[None]
CAQ_pdid_time = 300*[0]

def domo_online():
	try:
		r = requests.get(DOMO['URL']+'type=command&param=getversion', auth=(DOMO['USER'], DOMO['PASS']))
	except requests.exceptions.ConnectionError:
		print('Could not connect to '+DOMO['SERVER']+'.')
		return False
	return True

def domo_request(req):
	try:
		r = requests.get(DOMO['URL']+req, auth=(DOMO['USER'], DOMO['PASS']))
	except requests.exceptions.ConnectionError:
		raise Exception('Could not connect to '+DOMO['SERVER']+'. Exiting. ')

	if r.ok:
		return r.json()
	raise Exception('Could not connect to Domoticz (status code '+r.status_code+'.')

def domo_switchOnOff(cmd, idx):
	# seems specific for light switches!?
	print(domo_request('type=command&param=switchlight&idx='+DEVICE['IDX_'+idx]+'&switchcmd='+cmd+'&passcode='+DOMO['PROTECTION'])['status'])

def domo_updatedevice(cmd, idx):
	return(domo_request('type=command&param=udevice&idx='+idx+'&'+cmd+'&passcode='+DOMO['PROTECTION'])['status'])

def domo_getSpeedSelector():
	response = domo_request('type=devices&rid='+DEVICE['SPEED_SELECTOR'])

	if 'result' in response:
		try:
			level = response['result'][0]['Level']
		except:
			raise Exception('Unknown response '+response['result']+'.')
		return(get_speed(level))
	raise Exception('Switch with idx '+DEVICE['SPEED_SELECTOR']+' does not exist.')

def domo_getModeSelector():
	response = domo_request('type=devices&rid='+DEVICE['MODE_SELECTOR'])

	if 'result' in response:
		try:
			level = response['result'][0]['Level']
		except:
			raise Exception('Unknown response '+response['result']+'.')
		return(get_mode(level))
	raise Exception('Switch with idx '+DEVICE['MODE_SELECTOR']+' does not exist.')

def domo_setSelector(idx, level):
	return(domo_request('type=command&param=switchlight&idx='+idx+'&switchcmd=Set%20Level&level='+str(level)+'&passcode='+DOMO['PROTECTION'])['status'])

def domo_OnOffstatus():
	response = domo_request('type=devices&rid='+DEVICE['IDX'])

	if 'result' in response:
		try:
			status = response['result'][0]['Status']
		except:
			raise Exception('Unknown response '+response['result']+'.')
		if status == 'On':
			return True
		if status == 'Off':
			return False
		raise Exception('Switch with idx '+DEVICE['IDX']+' has unknown status ("'+status+'").')
	raise Exception('Switch with idx '+DEVICE['IDX']+' does not exist.')

def domo_status(idx):
	response = domo_request('type=devices&rid='+idx)

	if 'result' in response:
		try:
			status = response['result'][0]['Data']
			return response['result'][0]
		except:
			raise Exception('Unknown response '+response['result']+'.')

def bridge_discovery():
	## Bridge discovery ################################################################################################

	# Method 1: Use discovery to initialise Bridge
	# bridges = Bridge.discover(timeout=1)
	# if bridges:
	#	 bridge = bridges[0]
	# else:
	#	 bridge = None

	# Method 2: Use direct discovery to initialise Bridge
	#bridges = Bridge.discover(args.ip)
	print('Connecting directly to address '+CAQ['IP'])
	bridges = Bridge.discover(CAQ['IP'])
	if bridges:
		bridge = bridges[0]
	else:
		# Method 1: Use discovery to initialise Bridge
		print('No bridge found yet, using discovery method...')
		bridges = Bridge.discover(timeout=1)
		if bridges:
			bridge = bridges[0]
		else:
			bridge = None

	# Method 3: Setup bridge manually
	# bridge = Bridge(args.ip, bytes.fromhex('0000000000251010800170b3d54264b4'))

	if bridge is None:
		print("No bridges found!")
		exit(1)

	print("Bridge found: %s (%s)" % (bridge.uuid.hex(), bridge.host))
	bridge.debug = False

	return bridge

def get_hum_stat(hum):
	# HUM_STAT: 0=Normal; 1=Comfortable; 2=Dry; 3=Wet; below 30 Dry, between 30 and 45 Normal, and 45 and 70 comfortable, above 70 wet.

	if hum < 30: return("2")
	if hum >=30 and hum < 45: return("0")
	if hum >=45 and hum < 70: return("1")
	if hum >=70: return("3")
	
	return("0")

def get_hum(pdid):
	# get humidity of the air flow of the supplied temperature pdid (

	rvalue = None
	if pdid == SENSOR_TEMPERATURE_SUPPLY: rvalue = CAQ_pdid[SENSOR_HUMIDITY_SUPPLY]
	if pdid == SENSOR_TEMPERATURE_EXTRACT: rvalue = CAQ_pdid[SENSOR_HUMIDITY_EXTRACT]
	if pdid == SENSOR_TEMPERATURE_EXHAUST: rvalue = CAQ_pdid[SENSOR_HUMIDITY_EXHAUST]
	if pdid == SENSOR_TEMPERATURE_OUTDOOR: rvalue = CAQ_pdid[SENSOR_HUMIDITY_OUTDOOR]
	
	if rvalue == None:
		return(int(domo_status(DEVICE['IDX_'+str(pdid)])['Humidity']))
	else:
		return(rvalue)

def get_temp(pdid):
	# get temperature of the air flow of the supplied humidity pdid (temperature is *10)

	rvalue = None
	if pdid == SENSOR_HUMIDITY_EXTRACT: rvalue = CAQ_pdid[SENSOR_TEMPERATURE_EXTRACT]
	if pdid == SENSOR_HUMIDITY_EXHAUST: rvalue = CAQ_pdid[SENSOR_TEMPERATURE_EXHAUST]
	if pdid == SENSOR_HUMIDITY_OUTDOOR: rvalue = CAQ_pdid[SENSOR_TEMPERATURE_OUTDOOR]
	if pdid == SENSOR_HUMIDITY_SUPPLY: rvalue = CAQ_pdid[SENSOR_TEMPERATURE_SUPPLY]

	if rvalue == None:
		return(int(domo_status(DEVICE['IDX_'+str(pdid)])['Temp'])*10)
	else:
		return(rvalue)

def get_power(pdid):
	# get power (avoided or consumption) 
	
	rvalue = None
	
	if pdid == SENSOR_POWER_TOTAL: rvalue = CAQ_pdid[SENSOR_POWER_CURRENT]
	if pdid == SENSOR_POWER_CURRENT: rvalue = CAQ_pdid[SENSOR_POWER_TOTAL]
	if pdid == SENSOR_AVOIDED_HEATING_TOTAL: rvalue = CAQ_pdid[SENSOR_AVOIDED_HEATING_CURRENT]
	if pdid == SENSOR_AVOIDED_HEATING_CURRENT: rvalue = CAQ_pdid[SENSOR_AVOIDED_HEATING_TOTAL]

	if rvalue == None:
		if pdid == SENSOR_POWER_CURRENT or pdid == SENSOR_AVOIDED_HEATING_CURRENT:
			return(int(domo_status(DEVICE['IDX_'+str(pdid)])['Data'][0:-8]))
		else:
			return(int(domo_status(DEVICE['IDX_'+str(pdid)])['Usage'][0:-5]))
	else:
		return(rvalue)

def get_speed(value):
	# return selected fan speed (in string)

	if value == 0: return('AWAY')
	if value == 10: return('LOW')
	if value == 20: return('MEDIUM')
	if value == 30: return('HIGH')
	return('UNKNOWN speed '+str(value))

def get_mode(value):
	# return selected mode (in string)

	if value == 0: return('MANUAL (timer)')
	if value == 10: return('MANUAL')
	if value == 20: return('AUTO')
	return('UNKNOWN mode '+str(value))

def callback_sensor(pdid, value):
	## Callback sensors ################################################################################################

	idx = None
	CommandValue = None
	nvalue = None
	Precision = 1	## 1: natural numbers (1, 2, 3); 10: tientallen (10, 20, 30)
	
	# Each PDID section should do the following:
	# 1) Generate a 'CommandValue' that can be provided to domo_updatedevice
	# 2) Create a 'LogValue' describing what is happening --> WITHOUT LOGVALUE, NO COMMAND WILL BE SEND TO DOMOTICZ
	# 3) Setting 'nvalue' to the new value
	# Common for each pdid is executing the JSON command to Domoticz, printing the logmessage, updating the sensor value array and time after which an update to Domoticz is needed
	
	# Fast initialize
	if CAQ_pdid[pdid] == None: CAQ_pdid[pdid]=value
	
	# UPDATE TEMPERATURE
	if pdid == SENSOR_TEMPERATURE_SUPPLY or pdid == SENSOR_TEMPERATURE_EXTRACT or pdid == SENSOR_TEMPERATURE_EXHAUST or pdid == SENSOR_TEMPERATURE_OUTDOOR:
		## Update Temperature & Humidity: Temperature received from CAQ / 10
		# /json.htm?type=command&param=udevice&idx=IDX&nvalue=0&svalue=TEMP;HUM;HUM_STAT
		Precision = 1
		nvalue = round((value/Precision + CAQ_pdid[pdid]/Precision)/2)*Precision
		CommandValue = 'nvalue=0&svalue='+str(nvalue/10)+';'+str(get_hum(pdid))+';'+get_hum_stat(get_hum(pdid))
		if pdid == SENSOR_TEMPERATURE_SUPPLY: LogValue = 'Supply '
		if pdid == SENSOR_TEMPERATURE_EXTRACT: LogValue = 'Extract '
		if pdid == SENSOR_TEMPERATURE_EXHAUST: LogValue = 'Exhaust '
		if pdid == SENSOR_TEMPERATURE_OUTDOOR: LogValue = 'Outdoor '
		LogValue += 'Air Temperature to ' + str(nvalue/10) + 'C.'

	# UPDATE HUMIDITY
	if pdid == SENSOR_HUMIDITY_EXTRACT or pdid == SENSOR_HUMIDITY_EXHAUST or pdid == SENSOR_HUMIDITY_OUTDOOR or pdid == SENSOR_HUMIDITY_SUPPLY:
		## Update Temperature & Humidity: Humidity received from CAQ in %
		# /json.htm?type=command&param=udevice&idx=IDX&nvalue=0&svalue=TEMP;HUM;HUM_STAT
		Precision = 10 # for temperature value actually
		nvalue = value
		CommandValue = 'nvalue=0&svalue='+str(get_temp(pdid)/10)+';'+str(value)+';'
		# HUM_STAT: 0=Normal; 1=Comfortable; 2=Dry; 3=Wet; below 30 Dry, between 30 and 45 Normal, and 45 and 70 comfortable, above 70 wet.
		CommandValue += get_hum_stat(value)
		if pdid == SENSOR_HUMIDITY_EXTRACT: LogValue = 'Extract '
		if pdid == SENSOR_HUMIDITY_EXHAUST: LogValue = 'Exhaust '
		if pdid == SENSOR_HUMIDITY_OUTDOOR: LogValue = 'Outdoor '
		if pdid == SENSOR_HUMIDITY_SUPPLY: LogValue = 'Supply '
		LogValue += 'Air Humidity to ' + str(value) + '% '
		if CommandValue[-1] == '0': LogValue += '(normal).'
		if CommandValue[-1] == '1': LogValue += '(comfortable).'
		if CommandValue[-1] == '2': LogValue += '(dry).'
		if CommandValue[-1] == '3': LogValue += '(wet).'

	# UPDATE FAN SPEED SETTING (AWAY, LOW, MEDIUM, HIGH)
	if pdid == SENSOR_FAN_SPEED_MODE:
		LogValue = 'Speed selection to '+str(value)+': '
		nvalue = value * 10
		# unclear how to detect BOOST mode
		LogValue += (get_speed(nvalue).lower() + '.')
		
	# OPERATION MODE
	if pdid == SENSOR_OPERATING_MODE_BIS:
		# unclear how to detect BOOST mode  (`01` = limited manual, `05` = unlimited manual, `ff` = auto) | '07' = boost mode on a timer?
		LogValue = 'Mode selection to '+str(value)+': '
		if value == 5: 
			nvalue = 10
			LogValue += 'manual.'
		elif value == -1: 
			nvalue = 20
			LogValue += 'auto.'
		else: # value == 1 or value == 7
			nvalue = 0
			LogValue += 'manual (timer).'
		
	# BYPASS MODE
	# unknown!
	
	# BYPASS STATE
	if pdid == SENSOR_BYPASS_STATE:
		## Update Percentage
		# /json.htm?type=command&param=udevice&idx=IDX&nvalue=0&svalue=PERCENTAGE
		nvalue = value
		LogValue = 'Bypass ratio to ' + str(value) + '%.'
		CommandValue = 'nvalue=0&svalue='+str(value)
	
	# EXHAUST and SUPPLY FAN DUTY CYCLE / AIR FLOW
	if pdid == SENSOR_FAN_EXHAUST_DUTY or pdid == SENSOR_FAN_SUPPLY_DUTY:
		## Update Percentage (DUTY CYCLE)
		# /json.htm?type=command&param=udevice&idx=IDX&nvalue=0&svalue=PERCENTAGE
		#Read out present duty cycle (number shown in domoticz is average of exhaust and supply duty cycle!)
		nvalue = int(round((value + CAQ_pdid[pdid])/2))
		if pdid == SENSOR_FAN_EXHAUST_DUTY: CAQ_pdid[SENSOR_FAN_SUPPLY_DUTY] = nvalue
		if pdid == SENSOR_FAN_SUPPLY_DUTY: CAQ_pdid[SENSOR_FAN_EXHAUST_DUTY] = nvalue
		CommandValue = 'nvalue=0&svalue='+str(nvalue)
		LogValue = 'Fan duty cycle to ' + str(nvalue) + '%.'
	if pdid == SENSOR_FAN_EXHAUST_FLOW or pdid == SENSOR_FAN_SUPPLY_FLOW:
		## Custom sensor (FLOW)
		#/json.htm?type=command&param=udevice&idx=IDX&nvalue=0&svalue=VALUE
		#Read out present flow (number shown in domoticz is average of exhaust and supply duty cycle!)
		nvalue = round(round((value + CAQ_pdid[pdid])/2)/10)*10
		if pdid == SENSOR_FAN_EXHAUST_FLOW: CAQ_pdid[SENSOR_FAN_SUPPLY_FLOW] = nvalue
		if pdid == SENSOR_FAN_SUPPLY_FLOW: CAQ_pdid[SENSOR_FAN_EXHAUST_FLOW] = nvalue
		CommandValue = 'nvalue=0&svalue='+str(nvalue)
		LogValue = 'Air Flow to ' + str(nvalue) + 'm3/hr.'
	
	# POWER CONSUMPTION
	if pdid == SENSOR_POWER_CURRENT:
		## Update Power; ENERGY can be either from device or computer by Domoticz (configurable through 'edit' of device)
		# /json.htm?type=command&param=udevice&idx=IDX&nvalue=0&svalue=POWER;ENERGY
		Precision = 1
		#Read out value as shown in domoticz to average out value and prevent 'continuous updates'
		nvalue = round(round((value + CAQ_pdid[pdid])/2)/Precision)*Precision
		CommandValue = 'nvalue=0&svalue='+str(round(nvalue/Precision)*Precision)+';'+str(get_power(pdid)*1000)
		LogValue = 'current Power Consumption to ' + str(round(nvalue/Precision)*Precision) + 'W (cumulative: ' + str(get_power(pdid)) + 'kWh).'
	if pdid == SENSOR_POWER_TOTAL:
		## Update Power; ENERGY can be either from device or computer by Domoticz (configurable through 'edit' of device)
		# /json.htm?type=command&param=udevice&idx=IDX&nvalue=0&svalue=POWER;ENERGY
		Precision = 1
		nvalue = value
		#Read out present cumulative power consumption
		CommandValue = 'nvalue=0&svalue='+str(round(get_power(pdid)/Precision)*Precision)+';'+str(value*1000)
		LogValue = 'cumulative Power Consumption to ' + str(value) + 'kWh (current: ' + str(round(get_power(pdid)/Precision)*Precision) + 'W).'
	
	# AVOIDED HEATING
	if pdid == SENSOR_AVOIDED_HEATING_CURRENT:
		## Update Avoided ; ENERGY can be either from device or computer by Domoticz (configurable through 'edit' of device)
		# /json.htm?type=command&param=udevice&idx=IDX&nvalue=0&svalue=POWER;ENERGY
		Precision = 10
		#Read out value as shown in domoticz to average out value and prevent 'continuous updates'
		nvalue = round(round((value + CAQ_pdid[pdid])/2)/Precision)*Precision
		CommandValue = 'nvalue=0&svalue='+str(round(nvalue/Precision)*Precision)+';'+str(get_power(pdid)*1000)
		LogValue = 'current Avoided Heating to ' + str(round(nvalue/Precision)*Precision) + 'W (cumulative: ' + str(get_power(pdid)) + 'kWh).'
	if pdid == SENSOR_AVOIDED_HEATING_TOTAL:
		## Update Avoided ; ENERGY can be either from device or computer by Domoticz (configurable through 'edit' of device)
		# /json.htm?type=command&param=udevice&idx=IDX&nvalue=0&svalue=POWER;ENERGY
		Precision = 10
		nvalue = value
		#Read out present cumulative power consumption
		CommandValue = 'nvalue=0&svalue='+str(round(get_power(pdid)/Precision)*Precision)+';'+str(value*1000)
		LogValue = 'cumulative Avoided Heating to ' + str(value) + 'kWh (current: ' + str(round(get_power(pdid)/Precision)*Precision) + 'W).'
	
	
	if LogValue == None: 
		print("No action defined for pdid %s : %s" % (pdid, value))
	else:
		try:
			idx = DEVICE['IDX_'+str(pdid)]
		except (KeyError, TypeError):
			print("Cannot notify Domoticz, because no idx set for pdid %s : %s" % (pdid, value))
		else:
			if CAQ_pdid[pdid] != nvalue or time.time() > CAQ_pdid_time[pdid]:
				if pdid == 49 or pdid == 65:
					LogValue += ' ' + domo_setSelector(idx, nvalue)
				else:
					LogValue += ' ' + domo_updatedevice(CommandValue, idx)
				
				# store new value
				CAQ_pdid[pdid] = nvalue
				
				# determine log message type
				if CAQ_pdid_time[pdid] == 0:
					print('Registering sensor ' + LogValue)
				elif time.time() > CAQ_pdid_time[pdid]: 
					print('Keep alive update to ' + LogValue)
				else:
					print('Update to ' + LogValue)
				CAQ_pdid_time[pdid] = time.time() + int(DOMO['KEEP_ALIVE'])
			else: # no need to reprogram existing value in Domoticz --> save CPU bandwidth
				pass

def print_modes(new_mode, new_speed, change_ok):

	print("WAS -  Setmode %s ; Setspeed %s" % (was_DOMO_mode, was_DOMO_speed))
	print("NEW -  Setmode %s ; Setspeed %s ; change_speed %s" % (new_mode, new_speed, str(change_ok)))

	return

def infinite_loop():
	# Check if Domoticz is online
	if domo_online():
		print('Domoticz server ' + DOMO['SERVER'] + ' is online.')
	else:
		# Try to restart server one time
		print('Could not connecto to Domoticz server ' + DOMO['SERVER'] + '. Trying to restart Domoticz...')
		subprocess.call('sudo systemctl restart domoticz > /dev/null', shell=True)
		time.sleep(10)
		if not(domo_online()): 
			print('Failed to find Domoticz server at ' + DOMO['SERVER'] + '. Quiting...')
		exit(1)
	
	# Discover the bridge
	bridge = bridge_discovery()

	## Setup a Comfoconnect session  ###################################################################################
	local_uuid = bytes.fromhex('00000000000000000000000000000005')
	comfoconnect = ComfoConnect(bridge, local_uuid, CAQ['LOCAL_NAME'], CAQ['PIN'])
	comfoconnect.callback_sensor = callback_sensor

	try:
		# Connect to the bridge
		# comfoconnect.connect(False)  # Don't disconnect existing clients.
		comfoconnect.connect(True)  # Disconnect existing clients.

	except Exception as e:
		print('ERROR: %s' % e)
		exit(1)

	# VersionRequest
	version = comfoconnect.cmd_version_request()
	print(version)

	# Register sensors
	comfoconnect.register_sensor(SENSOR_FAN_EXHAUST_DUTY)  # Fans: Exhaust fan duty cycle
	comfoconnect.register_sensor(SENSOR_FAN_SUPPLY_DUTY)  # Fans: Exhaust fan duty cycle
	comfoconnect.register_sensor(SENSOR_FAN_EXHAUST_FLOW)  # Fans: Exhaust fan duty cycle
	comfoconnect.register_sensor(SENSOR_FAN_SUPPLY_FLOW)  # Fans: Exhaust fan duty cycle
	comfoconnect.register_sensor(SENSOR_POWER_CURRENT)  # Power Consumption: Current Ventilation
	comfoconnect.register_sensor(SENSOR_POWER_TOTAL)  # Power Consumption: Total from start
	#comfoconnect.register_sensor(SENSOR_DAYS_TO_REPLACE_FILTER)  # Days left before filters must be replaced
	comfoconnect.register_sensor(SENSOR_AVOIDED_HEATING_CURRENT)  # Avoided Heating: Avoided actual
	comfoconnect.register_sensor(SENSOR_AVOIDED_HEATING_TOTAL)  # Avoided Heating: Avoided total
	comfoconnect.register_sensor(SENSOR_TEMPERATURE_SUPPLY)  # Temperature & Humidity: Supply Air (temperature)
	comfoconnect.register_sensor(SENSOR_TEMPERATURE_EXTRACT)  # Temperature & Humidity: Extract Air (temperature)
	comfoconnect.register_sensor(SENSOR_TEMPERATURE_EXHAUST)  # Temperature & Humidity: Exhaust Air (temperature)
	comfoconnect.register_sensor(SENSOR_TEMPERATURE_OUTDOOR)  # Temperature & Humidity: Outdoor Air (temperature)
	comfoconnect.register_sensor(SENSOR_HUMIDITY_SUPPLY)  # Temperature & Humidity: Supply Air (humidity)
	comfoconnect.register_sensor(SENSOR_HUMIDITY_EXTRACT)  # Temperature & Humidity: Extract Air (humidity)
	comfoconnect.register_sensor(SENSOR_HUMIDITY_EXHAUST)  # Temperature & Humidity: Exhaust Air (humidity)
	comfoconnect.register_sensor(SENSOR_HUMIDITY_OUTDOOR)  # Temperature & Humidity: Outdoor Air (humidity)
	comfoconnect.register_sensor(SENSOR_BYPASS_STATE)  # Bypass state
	comfoconnect.register_sensor(SENSOR_OPERATING_MODE_BIS)  # Operating mode (bis)
	comfoconnect.register_sensor(SENSOR_FAN_SPEED_MODE)  # Operating mode (bis)

	print('Going into infinite loop ... stop with CTRL+C')
	try:
		while domo_online():
			# Callback messages will arrive in the callback method.
			# use time.sleep command to set polling interval of changes of speed selector
			time.sleep(DOMO.getint('INTERVAL'))
			
			if not comfoconnect.is_connected():
				print('We are not connected anymore...trying to reconnect...')
			else:
				domo_MODE = domo_getModeSelector()
				if get_mode(CAQ_pdid[SENSOR_OPERATING_MODE_BIS]) != domo_MODE:
					print('domo_MODE='+domo_MODE+'; CAQ_pdid='+get_mode(CAQ_pdid[SENSOR_OPERATING_MODE_BIS]))
					print('Request for changing mode detected... Go to mode: '+ domo_MODE)
					if domo_MODE == 'MANUAL':
						CAQ_pdid[SENSOR_OPERATING_MODE_BIS] = 10
						comfoconnect.cmd_rmi_request(CMD_MODE_MANUAL)
					if domo_MODE == 'AUTO':
						CAQ_pdid[SENSOR_OPERATING_MODE_BIS] = 10
						comfoconnect.cmd_rmi_request(CMD_MODE_MANUAL)
						CAQ_pdid[SENSOR_OPERATING_MODE_BIS] = 20
						comfoconnect.cmd_rmi_request(CMD_MODE_AUTO)

					CAQ_pdid_time[SENSOR_OPERATING_MODE_BIS] = time.time() + int(DOMO['KEEP_ALIVE'])

				domo_SPEED = domo_getSpeedSelector()
				if get_speed(CAQ_pdid[SENSOR_FAN_SPEED_MODE]) != domo_SPEED: 
					print('domo_SPEED='+domo_SPEED+'; CAQ_pdid='+get_speed(CAQ_pdid[SENSOR_FAN_SPEED_MODE]))
					print('Request for changing speed detected... Go to speed: '+domo_SPEED)
					if domo_SPEED == 'AWAY':
						CAQ_pdid[SENSOR_FAN_SPEED_MODE] = 0
						comfoconnect.cmd_rmi_request(CMD_FAN_MODE_AWAY)
					if 	domo_SPEED == 'LOW':
						CAQ_pdid[SENSOR_FAN_SPEED_MODE] = 10
						comfoconnect.cmd_rmi_request(CMD_FAN_MODE_LOW)
					if domo_SPEED == 'MEDIUM':
						CAQ_pdid[SENSOR_FAN_SPEED_MODE] = 20
						comfoconnect.cmd_rmi_request(CMD_FAN_MODE_MEDIUM)
					if domo_SPEED == 'HIGH':
						CAQ_pdid[SENSOR_FAN_SPEED_MODE] = 30
						comfoconnect.cmd_rmi_request(CMD_FAN_MODE_HIGH)

					CAQ_pdid_time[SENSOR_FAN_SPEED_MODE] = time.time() + int(DOMO['KEEP_ALIVE'])

	except KeyboardInterrupt:
		pass

	## Closing the session #############################################################################################
	print('Disconnecting...')
	comfoconnect.disconnect()


infinite_loop()


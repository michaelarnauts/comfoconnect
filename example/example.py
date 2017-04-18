#!/usr/bin/python3
import argparse
from time import sleep

from pycomfoconnect import *

parser = argparse.ArgumentParser()
parser.add_argument("ip", help="ip address of the bridge")
args = parser.parse_args()

## Configuration #######################################################################################################

pin = 0
local_name = 'Computer'
local_uuid = bytes.fromhex('00000000000000000000000000000001')

## Bridge discovery ####################################################################################################

# Method 1: Use discovery to initialise Bridge
# bridges = Bridge.discover()
# if bridges:
#     bridge = bridges[0]
# else:
#     bridge = None

# Method 2: Use direct discovery to initialise Bridge
bridges = Bridge.discover(args.ip)
if bridges:
    bridge = bridges[0]
else:
    bridge = None

# Method 3: Setup bridge manually
# bridge = Bridge(args.ip, bytes.fromhex('0000000000251010800170b3d54264b4'))

if bridge is None:
    print("No bridges found!")
    exit(1)

print("Bridge found: %s (%s)" % (bridge.remote_uuid.hex(), bridge.ip))


## Setting up a session ########################################################################################

def callback(var, value):
    print("%s = %s" % (var, value))


def setup_comfoconnect(bridge, callback):
    """Setup a Comfoconnect session"""
    comfoconnect = ComfoConnect(bridge, callback, debug=False)

    try:
        # Connect to the bridge
        version_info = comfoconnect.connect(local_uuid, local_name, pin)
        print('Connected to bridge with serial %s' % version_info['serialNumber'])

    except PyComfoConnectOtherSession as e:
        print('ERROR: Another session with "%s" is active.' % e.devicename)
        exit(1)

    except PyComfoConnectNotAllowed:
        print('ERROR: Could not register. Invalid PIN!')
        exit(1)

    ## Execute functions ###############################################################################################

    # ListRegisteredApps
    # for app in comfoconnect._bridge.ListRegisteredApps():
    #     print('%s: %s' % (app['uuid'].hex(), app['devicename']))

    # DeregisterApp
    # comfoconnect._bridge.DeregisterApp(bytes.fromhex('a996190220044d68a07d85a2e3866fff'))
    # comfoconnect._bridge.DeregisterApp(bytes.fromhex('a996190220044d68a07d85a2e3866fce'))

    # VersionRequest
    # versioninfo = comfoconnect._bridge.VersionRequest()
    # print(versioninfo)

    # CnTimeRequest
    # timeinfo = comfoconnect._bridge.CnTimeRequest()
    # print(timeinfo)

    ## Register sensors ################################################################################################

    # comfoconnect.request(const.SENSOR_FAN_NEXT_CHANGE) # General: Countdown until next fan speed change
    comfoconnect.request(const.SENSOR_FAN_SPEED_MODE)  # Fans: Fan speed setting
    comfoconnect.request(const.SENSOR_FAN_SUPPLY_DUTY)  # Fans: Supply fan duty
    comfoconnect.request(const.SENSOR_FAN_EXHAUST_DUTY)  # Fans: Exhaust fan duty
    comfoconnect.request(const.SENSOR_FAN_SUPPLY_FLOW)  # Fans: Supply fan flow
    comfoconnect.request(const.SENSOR_FAN_EXHAUST_FLOW)  # Fans: Exhaust fan flow
    comfoconnect.request(const.SENSOR_FAN_SUPPLY_SPEED)  # Fans: Supply fan speed
    comfoconnect.request(const.SENSOR_FAN_EXHAUST_SPEED)  # Fans: Exhaust fan speed
    # comfoconnect.request(const.SENSOR_POWER_CURRENT) # Power Consumption: Current Ventilation
    # comfoconnect.request(const.SENSOR_POWER_TOTAL_YEAR) # Power Consumption: Total year-to-date
    # comfoconnect.request(const.SENSOR_POWER_TOTAL) # Power Consumption: Total from start
    # comfoconnect.request(const.SENSOR_DAYS_TO_REPLACE_FILTER)  # Days left before filters must be replaced
    # comfoconnect.request(const.SENSOR_AVOIDED_HEATING_CURRENT) # Avoided Heating: Avoided actual
    # comfoconnect.request(const.SENSOR_AVOIDED_HEATING_TOTAL_YEAR) # Avoided Heating: Avoided year-to-date
    # comfoconnect.request(const.SENSOR_AVOIDED_HEATING_TOTAL) # Avoided Heating: Avoided total
    # comfoconnect.request(const.SENSOR_TEMPERATURE_SUPPLY)  # Temperature & Humidity: Supply Air (temperature)
    # comfoconnect.request(const.SENSOR_TEMPERATURE_EXTRACT)  # Temperature & Humidity: Extract Air (temperature)
    # comfoconnect.request(const.SENSOR_TEMPERATURE_EXHAUST)  # Temperature & Humidity: Exhaust Air (temperature)
    # comfoconnect.request(const.SENSOR_TEMPERATURE_OUTDOOR)  # Temperature & Humidity: Outdoor Air (temperature)
    # comfoconnect.request(const.SENSOR_HUMIDITY_SUPPLY)  # Temperature & Humidity: Supply Air (temperature)
    # comfoconnect.request(const.SENSOR_HUMIDITY_EXTRACT)  # Temperature & Humidity: Extract Air (temperature)
    # comfoconnect.request(const.SENSOR_HUMIDITY_EXHAUST)  # Temperature & Humidity: Exhaust Air (temperature)
    # comfoconnect.request(const.SENSOR_HUMIDITY_OUTDOOR)  # Temperature & Humidity: Outdoor Air (temperature)

    return comfoconnect


try:
    print('Initialising connection')
    comfoconnect = setup_comfoconnect(bridge, callback)

    ## Executing functions #########################################################################################

    # comfoconnect.set_fan_mode(const.FAN_MODE_AWAY) # Go to auto mode
    # comfoconnect.set_fan_mode(const.FAN_MODE_LOW) # Set fan speed to 1
    # comfoconnect.set_fan_mode(const.FAN_MODE_MEDIUM) # Set fan speed to 2
    # comfoconnect.set_fan_mode(const.FAN_MODE_HIGH) # Set fan speed to 3

    ## Example interaction #########################################################################################

    print('Waiting... Stop with CTRL+C')
    sleep(3)
    comfoconnect.disconnect()
    print('Disconnected')

    sleep(1)

    print('Initialising new connection')
    comfoconnect = setup_comfoconnect(bridge, callback)

    print('Waiting... Stop with CTRL+C')
    while True:

        # Callback messages will still arrive in the callback method.
        sleep(1)

        if not comfoconnect.is_connected():
            print('It seems we got disconnected.')
            exit()

except KeyboardInterrupt:
    pass

## Closing the session #################################################################################################

comfoconnect.disconnect()

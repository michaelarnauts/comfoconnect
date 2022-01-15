#!/usr/bin/python3
import argparse
from time import sleep

from pycomfoconnect import *

parser = argparse.ArgumentParser()
parser.add_argument('--ip', help='ip address of the bridge')
args = parser.parse_args()

## Configuration #######################################################################################################

pin = 0
local_name = 'Computer'
local_uuid = bytes.fromhex('00000000000000000000000000000005')


def bridge_discovery():
    ## Bridge discovery ################################################################################################

    # Method 1: Use discovery to initialise Bridge
    # bridges = Bridge.discover(timeout=1)
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

    print("Bridge found: %s (%s)" % (bridge.uuid.hex(), bridge.host))
    bridge.debug = True

    return bridge


def callback_sensor(var, value):
    ## Callback sensors ################################################################################################

    print("%s = %s" % (var, value))


def main():
    # Discover the bridge
    bridge = bridge_discovery()

    ## Setup a Comfoconnect session  ###################################################################################

    comfoconnect = ComfoConnect(bridge, local_uuid, local_name, pin)
    comfoconnect.callback_sensor = callback_sensor

    try:
        # Connect to the bridge
        # comfoconnect.connect(False)  # Don't disconnect existing clients.
        comfoconnect.connect(True)  # Disconnect existing clients.

    except Exception as e:
        print('ERROR: %s' % e)
        exit(1)

    ## Register sensors ################################################################################################

    # comfoconnect.register_sensor(SENSOR_FAN_NEXT_CHANGE)  # General: Countdown until next fan speed change
    # comfoconnect.register_sensor(SENSOR_FAN_SPEED_MODE)  # Fans: Fan speed setting
    # comfoconnect.register_sensor(SENSOR_FAN_SUPPLY_DUTY)  # Fans: Supply fan duty
    # comfoconnect.register_sensor(SENSOR_FAN_EXHAUST_DUTY)  # Fans: Exhaust fan duty
    # comfoconnect.register_sensor(SENSOR_FAN_SUPPLY_FLOW)  # Fans: Supply fan flow
    # comfoconnect.register_sensor(SENSOR_FAN_EXHAUST_FLOW)  # Fans: Exhaust fan flow
    # comfoconnect.register_sensor(SENSOR_FAN_SUPPLY_SPEED)  # Fans: Supply fan speed
    # comfoconnect.register_sensor(SENSOR_FAN_EXHAUST_SPEED)  # Fans: Exhaust fan speed
    # comfoconnect.register_sensor(SENSOR_POWER_CURRENT)  # Power Consumption: Current Ventilation
    # comfoconnect.register_sensor(SENSOR_ENERGY_TOTAL_YEAR)  # Power Consumption: Total year-to-date
    # comfoconnect.register_sensor(SENSOR_ENERGY_TOTAL)  # Power Consumption: Total from start
    # comfoconnect.register_sensor(SENSOR_DAYS_TO_REPLACE_FILTER)  # Days left before filters must be replaced
    # comfoconnect.register_sensor(SENSOR_AVOIDED_HEATING_CURRENT)  # Avoided Heating: Avoided actual
    # comfoconnect.register_sensor(SENSOR_AVOIDED_HEATING_TOTAL_YEAR)  # Avoided Heating: Avoided year-to-date
    # comfoconnect.register_sensor(SENSOR_AVOIDED_HEATING_TOTAL)  # Avoided Heating: Avoided total
    comfoconnect.register_sensor(SENSOR_TEMPERATURE_SUPPLY)  # Temperature & Humidity: Supply Air (temperature)
    comfoconnect.register_sensor(SENSOR_TEMPERATURE_EXTRACT)  # Temperature & Humidity: Extract Air (temperature)
    comfoconnect.register_sensor(SENSOR_TEMPERATURE_EXHAUST)  # Temperature & Humidity: Exhaust Air (temperature)
    comfoconnect.register_sensor(SENSOR_TEMPERATURE_OUTDOOR)  # Temperature & Humidity: Outdoor Air (temperature)
    comfoconnect.register_sensor(SENSOR_HUMIDITY_SUPPLY)  # Temperature & Humidity: Supply Air (temperature)
    comfoconnect.register_sensor(SENSOR_HUMIDITY_EXTRACT)  # Temperature & Humidity: Extract Air (temperature)
    comfoconnect.register_sensor(SENSOR_HUMIDITY_EXHAUST)  # Temperature & Humidity: Exhaust Air (temperature)
    comfoconnect.register_sensor(SENSOR_HUMIDITY_OUTDOOR)  # Temperature & Humidity: Outdoor Air (temperature)
    comfoconnect.register_sensor(SENSOR_BYPASS_STATE)  # Bypass state
    comfoconnect.register_sensor(SENSOR_OPERATING_MODE)  # Operating mode
    comfoconnect.register_sensor(SENSOR_OPERATING_MODE_BIS)  # Operating mode (bis)

    # comfoconnect.register_sensor(16) # 1
    # comfoconnect.register_sensor(33) # 1
    # comfoconnect.register_sensor(37) # 0
    # comfoconnect.register_sensor(53) # -1
    # comfoconnect.register_sensor(66) # 0
    # comfoconnect.register_sensor(67) # 0
    # comfoconnect.register_sensor(70) # 0
    # comfoconnect.register_sensor(71) # 0
    # comfoconnect.register_sensor(82) # ffffffff
    # comfoconnect.register_sensor(85) # ffffffff
    # comfoconnect.register_sensor(86) # ffffffff
    # comfoconnect.register_sensor(87) # ffffffff
    # comfoconnect.register_sensor(144) # 0
    # comfoconnect.register_sensor(145) # 0
    # comfoconnect.register_sensor(146) # 0
    # comfoconnect.register_sensor(176) # 0
    # comfoconnect.register_sensor(208) # 0
    # comfoconnect.register_sensor(210) # 0
    # comfoconnect.register_sensor(211) # 0
    # comfoconnect.register_sensor(212) # 228
    # comfoconnect.register_sensor(216) # 0
    # comfoconnect.register_sensor(217) # 28
    # comfoconnect.register_sensor(218) # 28
    # comfoconnect.register_sensor(219) # 0
    # comfoconnect.register_sensor(224) # 3
    # comfoconnect.register_sensor(225) # 1
    # comfoconnect.register_sensor(226) # 100
    # comfoconnect.register_sensor(228) # 0
    # comfoconnect.register_sensor(321) # 15
    # comfoconnect.register_sensor(325) # 1
    # comfoconnect.register_sensor(337) #
    # comfoconnect.register_sensor(338) # 00000000
    # comfoconnect.register_sensor(341) # 00000000
    # comfoconnect.register_sensor(369) # 0
    # comfoconnect.register_sensor(370) # 0
    # comfoconnect.register_sensor(371) # 0
    # comfoconnect.register_sensor(372) # 0
    # comfoconnect.register_sensor(384) # 0
    # comfoconnect.register_sensor(386) # 0
    # comfoconnect.register_sensor(400) # 0
    # comfoconnect.register_sensor(401) # 0
    # comfoconnect.register_sensor(402) # 0
    # comfoconnect.register_sensor(416) # -400
    # comfoconnect.register_sensor(417) # 100
    # comfoconnect.register_sensor(418) # 0
    # comfoconnect.register_sensor(419) # 0

    ## Execute functions ###############################################################################################

    # ListRegisteredApps
    # for app in comfoconnect.cmd_list_registered_apps():
    #     print('%s: %s' % (app['uuid'].hex(), app['devicename']))

    # DeregisterApp
    # comfoconnect.cmd_deregister_app(bytes.fromhex('00000000000000000000000000000001'))

    # VersionRequest
    version = comfoconnect.cmd_version_request()
    print(version)

    # TimeRequest
    # timeinfo = comfoconnect.cmd_time_request()
    # print(timeinfo)

    ## Executing functions #############################################################################################

    # comfoconnect.cmd_rmi_request(CMD_FAN_MODE_AWAY)  # Go to away mode
    # comfoconnect.cmd_rmi_request(CMD_FAN_MODE_LOW)  # Set fan speed to 1
    # comfoconnect.cmd_rmi_request(CMD_FAN_MODE_MEDIUM)  # Set fan speed to 2
    # comfoconnect.cmd_rmi_request(CMD_FAN_MODE_HIGH)  # Set fan speed to 3

    ## Example interaction #############################################################################################

    try:
        print('Waiting... Stop with CTRL+C')
        while True:
            # Callback messages will arrive in the callback method.
            sleep(1)

            if not comfoconnect.is_connected():
                print('We are not connected anymore...')

    except KeyboardInterrupt:
        pass

    ## Closing the session #############################################################################################

    print('Disconnecting...')
    comfoconnect.disconnect()


if __name__ == "__main__":
    main()

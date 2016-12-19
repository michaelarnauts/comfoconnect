#!/usr/bin/python3
from pycomfoconnect import Bridge, PyComfoConnectNotAllowed, PyComfoConnectOtherSession
from pycomfoconnect import zehnder_pb2

import argparse
import struct

parser = argparse.ArgumentParser()
parser.add_argument("ip", help="ip address of the bridge")
parser.add_argument("my_uuid", help="uuid of the local machine")
args = parser.parse_args()

## Bridge discovery ####################################################################################################

# Method 1: Use discovery to initialise Bridge
# bridges = Bridge.discover()
# if bridges:
#     bridge = bridges[0]
# else:
#     bridge = None

# Method 2: Use direct discovery to initialise Bridge
# bridges = Bridge.discover(args.ip)
# if bridges:
#     bridge = bridges[0]
# else:
#     bridge = None

# Method 3: Setup bridge manually
bridge = Bridge(args.ip, bytes.fromhex('0000000000251010800170b3d54264b4'))

if bridge is None:
    print("No bridges found!")
    exit(1)
print("Bridge found: %s (%s)" % (bridge.remote_uuid.hex(), bridge.ip))

## Setting up a session ################################################################################################

# Connect to the bridge
bridge.connect(bytes.fromhex(args.my_uuid))

try:
    message = bridge.StartSession(takeover=True)

except PyComfoConnectOtherSession as e:
    print('ERROR: Another session with "%s" is active.' % e.devicename)
    exit(1)

except PyComfoConnectNotAllowed:
    try:
        # Register with the bridge
        bridge.RegisterApp('Computer test', 0)

    except PyComfoConnectOtherSession as e:
        print('ERROR: Another session with "%s" is active.' % e.devicename)
        exit(1)

    except PyComfoConnectNotAllowed:
        print('ERROR: Could not register. Invalid PIN!')
        exit(1)

    # Start session
    bridge.StartSession()

# Read a notification message
message = bridge._read_message()

# Read a notification message
message = bridge._read_message()

## Executing commands ##################################################################################################

# ListRegisteredApps
# apps = bridge.ListRegisteredApps()
# for app in apps:
#     print('%s: %s' % (app['uuid'].hex(), app['devicename']))

# DeregisterApp
# bridge.DeregisterApp(bytes.fromhex('a996190220044d68a07d85a2e3866fff'))
# bridge.DeregisterApp(bytes.fromhex('a996190220044d68a07d85a2e3866fce'))

# VersionRequest
# versioninfo = bridge.VersionRequest()
# print(versioninfo)

# CnTimeRequest
# timeinfo = bridge.CnTimeRequest()
# print(timeinfo)

## Reading sensors #@@@#################################################################################################

# CnRpdoRequest
# bridge.CnRpdoRequest(65, 1, 1) # Fans: Fan speed setting
# bridge.CnRpdoRequest(117, 1, 1) # Fans: Supply fan duty
# bridge.CnRpdoRequest(118, 1, 1) # Fans: Exhaust fan duty
# bridge.CnRpdoRequest(119, 1, 2) # Fans: Supply fan flow
# bridge.CnRpdoRequest(120, 1, 2) # Fans: Exhaust fan flow
# bridge.CnRpdoRequest(121, 1, 2) # Fans: Supply fan speed
# bridge.CnRpdoRequest(122, 1, 2) # Fans: Exhaust fan speed
# bridge.CnRpdoRequest(128, 1, 2) # Power Consumption: Current Ventilation
# bridge.CnRpdoRequest(129, 1, 2) # Power Consumption: Total year-to-date
# bridge.CnRpdoRequest(130, 1, 2) # Power Consumption: Total from start
# bridge.CnRpdoRequest(192, 1, 2) # Days left before filters must be replaced

# bridge.CnRpdoRequest(213, 1, 2) # Avoided Heating: Avoided actual
# bridge.CnRpdoRequest(214, 1, 2) # Avoided Heating: Avoided year-to-date
# bridge.CnRpdoRequest(215, 1, 2) # Avoided Heating: Avoided total

# bridge.CnRpdoRequest(221, 1, 6) # Temperature & Humidity: Supply Air (temperature)
# bridge.CnRpdoRequest(274, 1, 6) # Temperature & Humidity: Extract Air (temperature)
# bridge.CnRpdoRequest(275, 1, 6) # Temperature & Humidity: Exhaust Air (temperature)
# bridge.CnRpdoRequest(276, 1, 6) # Temperature & Humidity: Outdoor Air (temperature)
# bridge.CnRpdoRequest(290, 1, 1) # Temperature & Humidity: Extract Air (humidity)
# bridge.CnRpdoRequest(291, 1, 1) # Temperature & Humidity: Exhaust Air (humidity)
# bridge.CnRpdoRequest(292, 1, 1) # Temperature & Humidity: Outdoor Air (humidity)
# bridge.CnRpdoRequest(294, 1, 1) # Temperature & Humidity: Supply Air (humidity)

# bridge.CnRpdoRequest(33, 1, 1) # 01
# bridge.CnRpdoRequest(37, 1, 1) # 00
# bridge.CnRpdoRequest(49, 1, 1) # 01
# bridge.CnRpdoRequest(53, 1, 1) # ff
# bridge.CnRpdoRequest(56, 1, 1) # 01
# bridge.CnRpdoRequest(65, 1, 1) # 01
# bridge.CnRpdoRequest(66, 1, 1) # 00
# bridge.CnRpdoRequest(67, 1, 1) # 02 or 00
# bridge.CnRpdoRequest(70, 1, 1) # 00
# bridge.CnRpdoRequest(71, 1, 1) # 00
# bridge.CnRpdoRequest(81, 1, 3) # ffffffff
# bridge.CnRpdoRequest(82, 1, 3) # ffffffff
# bridge.CnRpdoRequest(85, 1, 3) # ffffffff
# bridge.CnRpdoRequest(86, 1, 3) # ffffffff
# bridge.CnRpdoRequest(87, 1, 3) # ffffffff
# bridge.CnRpdoRequest(176, 1, 1) # 00
# bridge.CnRpdoRequest(208, 1, 1) # 00
# bridge.CnRpdoRequest(209, 1, 6) # 4700
# bridge.CnRpdoRequest(212, 1, 6) # ee00
# bridge.CnRpdoRequest(213, 1, 6) # ee00
# bridge.CnRpdoRequest(221, 1, 6) # ac00
# bridge.CnRpdoRequest(224, 1, 1) # 03
# bridge.CnRpdoRequest(225, 1, 1) # 01
# bridge.CnRpdoRequest(226, 1, 2) # 6400
# bridge.CnRpdoRequest(276, 1, 6) # 4300
# bridge.CnRpdoRequest(321, 1, 2) # 0700
# bridge.CnRpdoRequest(325, 1, 2) # 0100
# bridge.CnRpdoRequest(337, 1, 3) # 26000000
# bridge.CnRpdoRequest(338, 1, 3) # 00000000
# bridge.CnRpdoRequest(341, 1, 3) # 00000000
# bridge.CnRpdoRequest(369, 1, 1) # 00
# bridge.CnRpdoRequest(370, 1, 1) # 00
# bridge.CnRpdoRequest(371, 1, 1) # 00
# bridge.CnRpdoRequest(372, 1, 1) # 00
# bridge.CnRpdoRequest(386, 1, 0) # 00
# bridge.CnRpdoRequest(402, 1, 0) # 00
# bridge.CnRpdoRequest(419, 1, 0) # 00

# Read 50 messages
while True:
    message = bridge._read_message()
    if message is not None and message.cmd.type == zehnder_pb2.GatewayOperation.CnRpdoNotificationType:
        data = message.msg.data.hex()
        if len(data) == 2:
            print("%s = %s (%s)" % (message.msg.pdid, data, struct.unpack('b', message.msg.data)[0]))
        if len(data) == 4:
            print("%s = %s (%s)" % (message.msg.pdid, data, struct.unpack('h', message.msg.data)[0]))
        if len(data) == 8:
            print("%s = %s (%s)" % (message.msg.pdid, data))

## Closing the session #@###############################################################################################

bridge.CloseSession()

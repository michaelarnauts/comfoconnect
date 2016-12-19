#!/usr/bin/python3
from pycomfoconnect import Bridge, PyComfoConnectNotAllowed
import argparse

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
bridge = Bridge(args.ip, bytearray.fromhex('0000000000251010800170b3d54264b4'))

if bridge is None:
    print("No bridges found!")
    exit(1)
print("Bridge found: %s (%s)" % (bridge.remote_uuid.hex(), bridge.ip))

## Setting up a session ################################################################################################

# Connect to the bridge
bridge.connect(bytearray.fromhex(args.my_uuid))

try:
    bridge.StartSession()
except PyComfoConnectNotAllowed:
    try:
        # Register with the bridge
        bridge.RegisterApp('Computer', 0)

    except PyComfoConnectNotAllowed:
        print('Could not register. Invalid PIN!')
        exit(1)

    # Start session
    bridge.StartSession()

# Read a notification message
message = bridge._read_message()

# Read a notification message
message = bridge._read_message()

## Executing commands #@@###############################################################################################

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

## Closing the session #@###############################################################################################

bridge.CloseSession()

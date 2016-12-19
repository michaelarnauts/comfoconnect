#!/usr/bin/python3
import comfoconnect
import argparse
import time

parser = argparse.ArgumentParser()
parser.add_argument("ip", help="ip address of the bridge")
parser.add_argument("uuid", help="uuid of the bridge")
parser.add_argument("my_uuid", help="uuid of the local machine")

args = parser.parse_args()


def callback(cmd, msg):
    print(cmd)
    print(msg)
    pass


bridge = comfoconnect.Bridge(args.ip, args.uuid, callback)
bridge.connect(args.my_uuid)

try:
    # Start session
    bridge.StartSession()

except Exception as e:
    try:
        # Register with the bridge
        bridge.RegisterApp('Computer', 0)

    except Exception as e:
        print('Could not register. Invalid PIN!')
        exit(1)

    # Start session
    bridge.StartSession()

# Read a notification message
cmd, msg = bridge._read_message()

# Read a notification message
cmd, msg = bridge._read_message()

# List registered apps
# apps = bridge.ListRegisteredApps()
# print(apps)

# bridge.DeregisterApp('a996190220044d68a07d85a2e3866fcd')
# bridge.DeregisterApp('a996190220044d68a07d85a2e3866fce')

# version = bridge.VersionRequest()
# print(version)

# time = bridge.CnTimeRequest()
# print(time)

# Close session
bridge.CloseSession()

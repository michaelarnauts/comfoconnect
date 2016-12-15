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
    pass


bridge = comfoconnect.Bridge(args.ip, args.uuid, callback)
bridge.connect(args.my_uuid)

# Register with the bridge
try:
    bridge.RegisterApp('Computer', 0)
    print("Successfully registered")
except:
    print('Could not register. Invalid PIN!')
    exit(1)

# Start session
bridge.StartSession()

# Read a notification message
cmd, msg = bridge._read_message()

# Read a notification message
cmd, msg = bridge._read_message()

# Close session
bridge.CloseSession()





#
#
#
# # Login
# msg = GatewayOperation()
# msg.type = GatewayOperation.OperationType.Value('StartSessionRequestType')
# msg.reference = 1
# send_message(tcpsocket, 4, msg)
#
# # Login reply
# rpl = get_message(tcpsocket, GatewayOperation)
# print(rpl)
#
# tcpsocket.close()
#


# Logout
# msg = zehnder_pb2.GatewayOperation()
# msg.type = zehnder_pb2.GatewayOperation.OperationType.Value('CloseSessionRequestType')
# print(msg)

# login = zehnder_pb2.GatewayOperation()
#
# print(login.OperationType.)

# login.OperationType = zehnder_pb2.StartSessionRequest
# print(login.SerializeToString())

# Send login command
# login = zehnder_pb2.GatewayOperation()
# login.OperationType = zehnder_pb2._REGISTERAPPREQUEST
# print(login)

# data = tcpsocket.recv(4)
# print(data)

# Try to read response
# parser = zehnder_pb2.DiscoveryOperation()
# while True:
#     try:
#         udpsocket.settimeout(5)
#         data, source = udpsocket.recvfrom(100)
#         if data:
#             parser.ParseFromString(data)
#             print("Found bridge:")
#             print("* IP:      %s" % parser.searchGatewayResponse.ipaddress)
#             print("  UUID:    %s" % parser.searchGatewayResponse.uuid.hex())
#             print("  VERSION: %d" % parser.searchGatewayResponse.version)
#     except socket.timeout:
#         break

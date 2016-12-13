#!/usr/bin/python3
import socket
import zehnder_pb2

UDP_IP = "192.168.1.255"
UDP_PORT = 56747
UDP_MESSAGE = "\x0a\x00"

# Setup broadcast socket
udpsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udpsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
udpsocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
udpsocket.sendto(UDP_MESSAGE.encode(), (UDP_IP, UDP_PORT))

# Try to read response
parser = zehnder_pb2.DiscoveryOperation()
while True:
    try:
        udpsocket.settimeout(5)
        data, source = udpsocket.recvfrom(100)
        if data:
            parser.ParseFromString(data)
            print("Found bridge:")
            print("* IP:      %s" % parser.searchGatewayResponse.ipaddress)
            print("  UUID:    %s" % parser.searchGatewayResponse.uuid.hex())
            print("  VERSION: %d" % parser.searchGatewayResponse.version)
    except socket.timeout:
        break
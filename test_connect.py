#!/usr/bin/python3
import socket
from zehnder_pb2 import *
import struct

ZEHNDER_IP =    "192.168.1.213"
ZEHNDER_PORT =  56747
ZEHNDER_UUID = "0000000000251010800170b3d54264b4"
MY_UUID =      "af154804169043898d2da77148f886be"

def send_message(sock, cmd, msg):
    """ Send a serialized message (protobuf Message interface)
        to a socket, prepended by a header (length, src, dst).
    """
    cmd_buf = cmd.SerializeToString()
    msg_buf = msg.SerializeToString()
    header = struct.pack('>L16s16sH', 32 + 2 + len(cmd_buf) + len(msg_buf), bytearray.fromhex(MY_UUID), bytearray.fromhex(ZEHNDER_UUID), len(cmd_buf))

    print('tx:' + header.hex() + cmd_buf.hex() + msg_buf.hex())
    sock.sendall(header + cmd_buf + msg_buf)

def get_message(sock, msgtype):
    """ Read a message from a socket. msgtype is a subclass of protobuf Message.
    """

    # Read full packet
    msg_len_buf = sock.recv(4)
    msg_len = struct.unpack('>L', msg_len_buf)[0]
    msg_buf = sock.recv(msg_len)

    # Extract headers
    src_buf = msg_buf[:16]
    dst_buf = msg_buf[16:32]
    cmd_len_buf = msg_buf[32:34]
    cmd_len = struct.unpack('>H', cmd_len_buf)[0]
    cmd_buf = msg_buf[34:34+cmd_len]
    msg_buf = msg_buf[34+cmd_len:]

    print('rx:')
    print(msg_len_buf.hex())
    print(src_buf.hex())
    print(dst_buf.hex())
    print(cmd_len_buf.hex())
    print(cmd_buf.hex())
    print(msg_buf.hex())


    cmd = msgtype()
    cmd.ParseFromString(cmd_buf)

    msg_type = cmd.type


    print(msg_type)


    exit()

    src_buf = socket_read_n(sock, 16)
    dst_buf = socket_read_n(sock, 16)
    cmd_len_buf = socket_read_n(sock, 2)


    msg = msgtype()
    msg.ParseFromString(msg_buf)
    return msg

def socket_read_n(sock, n):
    """ Read exactly n bytes from the socket.
        Raise RuntimeError if the connection closed before
        n bytes were read.
    """
    buf = ''
    while n > 0:
        data = sock.recv(n)
        if data == '':
            raise RuntimeError('unexpected connection close')
        buf += data
        n -= len(data)
    return buf

# Setup socket and connect
tcpsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpsocket.connect((ZEHNDER_IP, ZEHNDER_PORT))


# Register
cmd = GatewayOperation()
cmd.type = GatewayOperation.OperationType.Value('RegisterAppRequestType')
cmd.reference = 2

msg = RegisterAppRequest()
msg.uuid = bytes.fromhex(MY_UUID)
msg.pin = 0
msg.devicename = 'Computer'
send_message(tcpsocket, cmd, msg)

# Register reply
rpl = get_message(tcpsocket, GatewayOperation)
print(rpl)

tcpsocket.close()



# Login
msg = GatewayOperation()
msg.type = GatewayOperation.OperationType.Value('StartSessionRequestType')
msg.reference = 1
send_message(tcpsocket, 4, msg)

# Login reply
rpl = get_message(tcpsocket, GatewayOperation)
print(rpl)

tcpsocket.close()



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
#!/usr/bin/python3
import comfoconnect
import struct
import sys
import zehnder_pb2

"""
Usage:
  $ cat captures/raw_input.txt | xxd -r -p | ./manually_decode.py
"""

pdids = {}
pdidstype = {}
rmis = {}

message = comfoconnect.Message()
while True:

    # Read packet size
    msg_len_buf = sys.stdin.buffer.read(4)
    if not msg_len_buf:
        break

    msg_len = struct.unpack('>L', msg_len_buf)[0]

    # Read rest of packet
    msg_buf = sys.stdin.buffer.read(msg_len)

    cmd, msg = message.decode(msg_len_buf + msg_buf)
    print(cmd)
    print(msg)

    if cmd.type == zehnder_pb2.GatewayOperation.OperationType.Value('CnRmiRequestType'):
        if not int(cmd.reference) in rmis:
            rmis[int(cmd.reference)] = {0: None, 1: None}
        rmis[int(cmd.reference)][0] = [msg.nodeId, msg.message.hex()]

    if cmd.type == zehnder_pb2.GatewayOperation.OperationType.Value('CnRmiResponseType'):
        if not int(cmd.reference) in rmis:
            rmis[int(cmd.reference)] = {0: None, 1: None}
        rmis[int(cmd.reference)][1] = msg.message

    if cmd.type == zehnder_pb2.GatewayOperation.OperationType.Value('CnRpdoNotificationType'):
        try:
            pdids[int(msg.pdid)].append(msg.data.hex())
        except KeyError:
            pdids[int(msg.pdid)] = [msg.data.hex()]

    if cmd.type == zehnder_pb2.GatewayOperation.OperationType.Value('CnRpdoRequestType'):
        pdidstype[int(msg.pdid)] = [msg.zone, msg.type]

print("CnRpdo")
for pdid in pdids:
    print(pdid, pdidstype[pdid], pdids[pdid])

print()
print("RMI")
for rmi in rmis:
    print(rmi, rmis[rmi][0], rmis[rmi][1])


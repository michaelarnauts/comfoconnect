#!/usr/bin/python3
import struct
import sys

import pycomfoconnect
from pycomfoconnect import zehnder_pb2

"""
Pipe the messages to this programm to decode them. If they are stored in HEX, you should pass them to xxd -r -p first.
You can combine both input and output streams.

Usage:
  $ cat captures/raw_*.txt | xxd -r -p | ./manually_decode.py
"""

pdids = {}
rmis = {}

while True:

    # Read packet from file
    msg_len_buf = sys.stdin.buffer.read(4)
    if not msg_len_buf:
        break
    msg_len = struct.unpack('>L', msg_len_buf)[0]
    msg_buf = sys.stdin.buffer.read(msg_len)

    # Decode packet
    message = pycomfoconnect.Message.decode(msg_len_buf + msg_buf)

    if message.cmd.type == zehnder_pb2.GatewayOperation.CnRmiRequestType:
        if not message.cmd.reference in rmis:
            rmis[message.cmd.reference] = {}
        rmis[message.cmd.reference]['tx'] = message.msg.message.hex()

    if message.cmd.type == zehnder_pb2.GatewayOperation.CnRmiResponseType:
        if not message.cmd.reference in rmis:
            rmis[message.cmd.reference] = {}
        rmis[message.cmd.reference]['rx'] = message.msg.message.hex()

    if message.cmd.type == zehnder_pb2.GatewayOperation.CnRpdoRequestType:
        if not message.msg.pdid in pdids:
            pdids[message.msg.pdid] = {}
        try:
            pdids[message.msg.pdid]['tx'].append(message.msg.type)
        except KeyError:
            pdids[message.msg.pdid]['tx'] = [message.msg.type]

    if message.cmd.type == zehnder_pb2.GatewayOperation.CnRpdoConfirmType:
        pass

    if message.cmd.type == zehnder_pb2.GatewayOperation.CnRpdoNotificationType:
        if not message.msg.pdid in pdids:
            pdids[message.msg.pdid] = {}
        try:
            pdids[message.msg.pdid]['rx'].append(message.msg.data.hex())
        except KeyError:
            pdids[message.msg.pdid]['rx'] = [message.msg.data.hex()]

print("CnRpdoRequestType")
for pdid in pdids:
    print(pdid, pdids[pdid])
#
# # print("CnRmiRequestType")
# # for rmi in rmis:
# #     print(rmi, rmis[rmi])
#

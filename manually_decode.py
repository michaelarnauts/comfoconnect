#!/usr/bin/python3
import comfoconnect
import struct
import sys

"""
Usage:
  $ cat captures/raw_input.txt | xxd -r -p | ./manually_decode.py
"""

message = comfoconnect.Message()
while True:

    # Read packet size
    msg_len_buf = sys.stdin.buffer.read(4)
    if not msg_len_buf:
        exit()

    msg_len = struct.unpack('>L', msg_len_buf)[0]

    # Read rest of packet
    msg_buf = sys.stdin.buffer.read(msg_len)

    cmd, msg = message.decode(msg_len_buf + msg_buf)
    print(message)
    print(cmd)
    print(msg)

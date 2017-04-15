"""
PyComfoConnect: Manage your Zehnder ComfoConnect Q350/Q450/Q650 ventilation unit
"""
from __future__ import print_function

from .zehnder_pb2 import *
from .message import *
from .error import *

import socket
import struct


class Bridge(object):
    local_uuid = None
    ip = None
    remote_uuid = None
    version = None
    debug = None

    socket = None
    reference = None

    notification_callback = None

    def __init__(self, ip, remote_uuid, version=1, debug=False):
        self.ip = ip
        self.remote_uuid = remote_uuid
        self.version = version
        self.debug = debug

        self.reference = 15  # todo: random value

    @staticmethod
    def discover(ip=None):
        # Setup socket
        udpsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udpsocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        udpsocket.settimeout(2)

        # Send broadcast packet
        if ip is None:
            udpsocket.sendto("\x0a\x00".encode(), ('<broadcast>', 56747))
        else:
            udpsocket.sendto("\x0a\x00".encode(), (ip, 56747))

        # Try to read response
        parser = zehnder_pb2.DiscoveryOperation()
        bridges = []
        while True:
            try:
                data, source = udpsocket.recvfrom(100)
                if data:
                    # Parse data
                    parser.ParseFromString(data)
                    ip_address = parser.searchGatewayResponse.ipaddress
                    uuid = parser.searchGatewayResponse.uuid
                    version = parser.searchGatewayResponse.version

                    # Create bridge objects
                    bridge = Bridge(ip_address, uuid, version)
                    if ip:
                        return [bridge]
                    bridges.append(bridge)

            except socket.timeout:
                break

        # Return found bridges
        return bridges

    def connect(self, local_uuid, notification_callback):
        self.local_uuid = local_uuid
        self.notification_callback = notification_callback

        try:
            # Connect to bridge
            tcpsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcpsocket.settimeout(10)
            tcpsocket.connect((self.ip, 56747))
            self.socket = tcpsocket

        except OSError:
            raise PyComfoConnectError('Could not connect to the bridge')

        return True

    def _send_message(self, message):
        if self.socket is None:
            raise PyComfoConnectError('Not connected!')

        # Construct packet
        packet = message.encode()

        self.socket.sendall(packet)

        # Debug message
        if self.debug:
            print("tx: %s" % message)

        return True

    def _read_message(self):
        if self.socket is None:
            raise PyComfoConnectError('Not connected!')

        # Read packet size
        try:
            msg_len_buf = self.socket.recv(4)
            if not msg_len_buf:
                raise PyComfoConnectError('Disconnected.')

            msg_len = struct.unpack('>L', msg_len_buf)[0]

            # Read rest of packet
            msg_buf = self.socket.recv(msg_len)

        except OSError:
            return None

        # Extract headers
        message = Message.decode(msg_len_buf + msg_buf)

        # Debug message
        if self.debug:
            print("rx: %s" % message)

        # Check if the message is for us
        if message.dst != self.local_uuid:
            raise BaseException(
                "Received message destination (%s) is not for us (%s)" % (message.dst.hex(), self.local_uuid.hex()))

        return message

    def StartSession(self, takeover=False):
        cmd = zehnder_pb2.GatewayOperation()
        cmd.type = zehnder_pb2.GatewayOperation.StartSessionRequestType
        cmd.reference = self.reference
        self.reference += 1

        msg = zehnder_pb2.StartSessionRequest()
        if takeover:
            msg.takeover = 1

        # Send the message
        message = Message(cmd, msg, self.local_uuid, self.remote_uuid)
        self._send_message(message)

        # Read a message
        reply = self._read_message()

        # Read a notification message
        message = self._read_message()
        self.notification_callback(message)

        # Read a notification message
        message = self._read_message()
        self.notification_callback(message)

        return reply

    def CloseSession(self):
        cmd = zehnder_pb2.GatewayOperation()
        cmd.type = zehnder_pb2.GatewayOperation.CloseSessionRequestType
        cmd.reference = self.reference
        self.reference += 1

        msg = zehnder_pb2.CloseSessionRequest()

        # Send the message
        message = Message(cmd, msg, self.local_uuid, self.remote_uuid)
        self._send_message(message)

        return True

    def ListRegisteredApps(self):
        cmd = zehnder_pb2.GatewayOperation()
        cmd.type = zehnder_pb2.GatewayOperation.ListRegisteredAppsRequestType
        cmd.reference = self.reference
        self.reference += 1

        msg = zehnder_pb2.ListRegisteredAppsRequest()

        # Send the message
        message = Message(cmd, msg, self.local_uuid, self.remote_uuid)
        self._send_message(message)

        # Read feedback
        reply = self._read_message()

        apps = []
        for app in reply.msg.apps:
            apps.append({
                'uuid': app.uuid,
                'devicename': app.devicename
            })

        return apps

    def RegisterApp(self, devicename, pin=0):
        cmd = zehnder_pb2.GatewayOperation()
        cmd.type = zehnder_pb2.GatewayOperation.RegisterAppRequestType
        cmd.reference = self.reference
        self.reference += 1

        msg = zehnder_pb2.RegisterAppRequest()
        msg.uuid = self.local_uuid
        msg.pin = pin
        msg.devicename = devicename

        # Send the message
        message = Message(cmd, msg, self.local_uuid, self.remote_uuid)
        self._send_message(message)

        # Read feedback
        reply = self._read_message()

        return reply

    def DeregisterApp(self, uuid):
        cmd = zehnder_pb2.GatewayOperation()
        cmd.type = zehnder_pb2.GatewayOperation.DeregisterAppRequestType
        cmd.reference = self.reference
        self.reference += 1

        msg = zehnder_pb2.DeregisterAppRequest()
        msg.uuid = uuid

        # Send the message
        message = Message(cmd, msg, self.local_uuid, self.remote_uuid)
        self._send_message(message)

        # Read feedback
        reply = self._read_message()

        return True

    def VersionRequest(self):
        cmd = zehnder_pb2.GatewayOperation()
        cmd.type = zehnder_pb2.GatewayOperation.VersionRequestType
        cmd.reference = self.reference
        self.reference += 1

        msg = zehnder_pb2.VersionRequest()

        # Send the message
        message = Message(cmd, msg, self.local_uuid, self.remote_uuid)
        self._send_message(message)

        # Read feedback
        reply = self._read_message()

        return {
            'gatewayVersion': reply.msg.gatewayVersion,
            'serialNumber': reply.msg.serialNumber,
            'comfoNetVersion': reply.msg.comfoNetVersion

        }

    def CnTimeRequest(self):
        cmd = zehnder_pb2.GatewayOperation()
        cmd.type = zehnder_pb2.GatewayOperation.CnTimeRequestType
        cmd.reference = self.reference
        self.reference += 1

        msg = zehnder_pb2.CnTimeRequest()

        # Send the message
        message = Message(cmd, msg, self.local_uuid, self.remote_uuid)
        self._send_message(message)

        # Read feedback
        reply = self._read_message()

        return reply.msg.currentTime

    def CnRmiRequest(self, nodeId, message):
        cmd = zehnder_pb2.GatewayOperation()
        cmd.type = zehnder_pb2.GatewayOperation.CnRmiRequestType
        cmd.reference = self.reference
        self.reference += 1

        msg = zehnder_pb2.CnRmiRequest()
        msg.nodeId = nodeId
        msg.message = message

        # Send the message
        message = Message(cmd, msg, self.local_uuid, self.remote_uuid)
        self._send_message(message)

        # Read feedback
        reply = self._read_message()

        return reply

    def CnRpdoRequest(self, pdid, zone, type, timeout=None):
        cmd = zehnder_pb2.GatewayOperation()
        cmd.type = zehnder_pb2.GatewayOperation.CnRpdoRequestType
        cmd.reference = self.reference
        self.reference += 1

        msg = zehnder_pb2.CnRpdoRequest()
        msg.pdid = pdid
        msg.zone = zone
        msg.type = type
        if timeout is not None:
            msg.timeout = timeout

        # Send the message
        message = Message(cmd, msg, self.local_uuid, self.remote_uuid)
        self._send_message(message)

        # Read feedback
        reply = self._read_message()

        return True

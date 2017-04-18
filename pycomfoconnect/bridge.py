from __future__ import print_function

import queue
import socket
import threading

from .message import *


class Bridge(object):
    @staticmethod
    def discover(ip=None):
        # Setup socket
        udpsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udpsocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        udpsocket.settimeout(2)

        # Send broadcast packet
        if ip is None:
            udpsocket.sendto(b"\x0a\x00", ('<broadcast>', 56747))
        else:
            udpsocket.sendto(b"\x0a\x00", (ip, 56747))

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

                    # Create bridge objects
                    bridge = Bridge(ip_address, uuid)
                    if ip:
                        return [bridge]
                    bridges.append(bridge)

            except socket.timeout:
                break

        # Return found bridges
        return bridges

    def __init__(self, ip: str, remote_uuid: str) -> None:
        self.ip = ip
        self.remote_uuid = remote_uuid
        self.local_uuid = None

        self._callback = None
        self._reference = 1

        self._stopping = None
        self._thread = None
        self._queue = None

        self.debug = False

    def connect(self, local_uuid: str, callback=None) -> bool:
        """Open connection to the bridge."""

        self.local_uuid = local_uuid
        self._callback = callback
        try:
            # Connect to bridge
            tcpsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcpsocket.settimeout(None)
            tcpsocket.connect((self.ip, 56747))
            self._socket = tcpsocket

        except OSError:
            raise PyComfoConnectError('Could not connect to the bridge')

        return True

    def disconnect(self):
        """Close connection to the bridge."""

        # Ask the message thread to stop if it is running and wait
        if self._thread.is_alive():
            self._stopping.set()
            self._thread.join()

        # Disconnect from bridge
        self._socket.close()


    def is_connected(self):
        return self._thread.is_alive()

    def _message_thread(self):
        """Listen for incoming messages and queue them or send them to a callback method."""
        self._stopping = threading.Event()
        self._queue = queue.Queue()

        while not self._stopping.isSet():
            message = self._socket_read_message()
            if message is None:
                return False

            if message.cmd.type in [zehnder_pb2.GatewayOperation.CnNodeNotificationType,
                                    zehnder_pb2.GatewayOperation.CnRpdoNotificationType,
                                    zehnder_pb2.GatewayOperation.CnAlarmNotificationType]:
                # Send notifications to a callback function.
                self._callback(message)

            elif message.cmd.type in [zehnder_pb2.GatewayOperation.CloseSessionRequestType]:
                raise Exception('Another app disconnected us.')

            else:
                # Send other messages to a queue
                self._queue.put(message)

    def _send_message(self, message):
        return self._socket_send_message(message)

    def _read_message(self, timeout=5):
        if self._thread and self._thread.is_alive():
            try:
                message = self._queue.get(timeout)
                if message:
                    self._queue.task_done()
                    return message

            except queue.Empty:
                return None
        else:
            return self._socket_read_message()

    def _socket_send_message(self, message):
        if self._socket is None:
            raise PyComfoConnectError('Not connected!')

        # Construct packet
        packet = message.encode()

        # Send packet
        self._socket.sendall(packet)

        # Debug message
        if self.debug:
            print("tx: %s" % message)

        return True

    def _socket_read_message(self):
        # Read packet size
        msg_len_buf = self._socket.recv(4, socket.MSG_WAITALL)
        if not msg_len_buf:
            return None

        msg_len = struct.unpack('>L', msg_len_buf)[0]

        # Read rest of packet
        msg_buf = self._socket.recv(msg_len, socket.MSG_WAITALL)

        # Extract headers
        message = Message.decode(msg_len_buf + msg_buf)

        # Debug message
        if self.debug:
            print("rx: %s" % message)

        # Check if the message is for us
        if message.dst != self.local_uuid:
            raise Exception(
                "Received message destination (%s) is not for us (%s)" % (message.dst.hex(), self.local_uuid.hex()))

        return message

    def StartSession(self, takeover=False):
        cmd = zehnder_pb2.GatewayOperation()
        cmd.type = zehnder_pb2.GatewayOperation.StartSessionRequestType
        cmd.reference = self._reference
        self._reference += 1

        msg = zehnder_pb2.StartSessionRequest()
        if takeover:
            msg.takeover = 1

        # Send the message
        message = Message(cmd, msg, self.local_uuid, self.remote_uuid)
        self._send_message(message)

        # Read a message
        reply = self._read_message()

        # Starts the message thread
        self._thread = threading.Thread(target=self._message_thread)
        self._thread.start()

        return reply

    def CloseSession(self):
        cmd = zehnder_pb2.GatewayOperation()
        cmd.type = zehnder_pb2.GatewayOperation.CloseSessionRequestType
        cmd.reference = self._reference
        self._reference += 1

        msg = zehnder_pb2.CloseSessionRequest()

        # Send the message
        message = Message(cmd, msg, self.local_uuid, self.remote_uuid)
        self._send_message(message)

        return True

    def ListRegisteredApps(self):
        cmd = zehnder_pb2.GatewayOperation()
        cmd.type = zehnder_pb2.GatewayOperation.ListRegisteredAppsRequestType
        cmd.reference = self._reference
        self._reference += 1

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
        cmd.reference = self._reference
        self._reference += 1

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
        cmd.reference = self._reference
        self._reference += 1

        msg = zehnder_pb2.DeregisterAppRequest()
        msg.uuid = uuid

        # Send the message
        message = Message(cmd, msg, self.local_uuid, self.remote_uuid)
        self._send_message(message)

        # Read feedback
        reply = self._read_message()

        return reply

    def VersionRequest(self):
        cmd = zehnder_pb2.GatewayOperation()
        cmd.type = zehnder_pb2.GatewayOperation.VersionRequestType
        cmd.reference = self._reference
        self._reference += 1

        msg = zehnder_pb2.VersionRequest()

        # Send the message
        message = Message(cmd, msg, self.local_uuid, self.remote_uuid)
        self._send_message(message)

        # Read feedback
        reply = self._read_message()

        return {
            'gatewayVersion': reply.msg.gatewayVersion,
            'serialNumber': reply.msg.serialNumber,
            'comfoNetVersion': reply.msg.comfoNetVersion,
        }

    def CnTimeRequest(self):
        cmd = zehnder_pb2.GatewayOperation()
        cmd.type = zehnder_pb2.GatewayOperation.CnTimeRequestType
        cmd.reference = self._reference
        self._reference += 1

        msg = zehnder_pb2.CnTimeRequest()

        # Send the message
        message = Message(cmd, msg, self.local_uuid, self.remote_uuid)
        self._send_message(message)

        # Read feedback
        reply = self._read_message()

        return reply

    def CnRmiRequest(self, nodeId, message):
        cmd = zehnder_pb2.GatewayOperation()
        cmd.type = zehnder_pb2.GatewayOperation.CnRmiRequestType
        cmd.reference = self._reference
        self._reference += 1

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
        cmd.reference = self._reference
        self._reference += 1

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

        return reply

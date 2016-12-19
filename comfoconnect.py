#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import zehnder_pb2
import struct

BRIDGE_PORT = 56747


class BridgeDiscovery(object):
    def __init__(self):
        pass

    def Discover(self):

        # Setup socket
        udpsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udpsocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        udpsocket.settimeout(2)

        # Send broadcast packet
        udpsocket.sendto("\x0a\x00".encode(), ('<broadcast>', BRIDGE_PORT))

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
                    uuid = parser.searchGatewayResponse.uuid.hex()
                    version = parser.searchGatewayResponse.version

                    # Create bridge objects
                    bridge = Bridge(ip_address, uuid, version)
                    bridges.append(bridge)

            except socket.timeout:
                break

        # Return found bridges
        return bridges


class Message(object):
    mapping = {
        'SetAddressRequestType': zehnder_pb2.SetAddressRequest,
        'RegisterAppRequestType': zehnder_pb2.RegisterAppRequest,
        'StartSessionRequestType': zehnder_pb2.StartSessionRequest,
        'CloseSessionRequestType': zehnder_pb2.CloseSessionRequest,
        'ListRegisteredAppsRequestType': zehnder_pb2.ListRegisteredAppsRequest,
        'DeregisterAppRequestType': zehnder_pb2.DeregisterAppRequest,
        'ChangePinRequestType': zehnder_pb2.ChangePinRequest,
        'GetRemoteAccessIdRequestType': zehnder_pb2.GetRemoteAccessIdRequest,
        'SetRemoteAccessIdRequestType': zehnder_pb2.SetRemoteAccessIdRequest,
        'GetSupportIdRequestType': zehnder_pb2.GetSupportIdRequest,
        'SetSupportIdRequestType': zehnder_pb2.SetSupportIdRequest,
        'GetWebIdRequestType': zehnder_pb2.GetWebIdRequest,
        'SetWebIdRequestType': zehnder_pb2.SetWebIdRequest,
        'SetPushIdRequestType': zehnder_pb2.SetPushIdRequest,
        'DebugRequestType': zehnder_pb2.DebugRequest,
        'UpgradeRequestType': zehnder_pb2.UpgradeRequest,
        'SetDeviceSettingsRequestType': zehnder_pb2.SetDeviceSettingsRequest,
        'VersionRequestType': zehnder_pb2.VersionRequest,
        'SetAddressConfirmType': zehnder_pb2.SetAddressConfirm,
        'RegisterAppConfirmType': zehnder_pb2.RegisterAppConfirm,
        'StartSessionConfirmType': zehnder_pb2.StartSessionConfirm,
        'CloseSessionConfirmType': zehnder_pb2.CloseSessionConfirm,
        'ListRegisteredAppsConfirmType': zehnder_pb2.ListRegisteredAppsConfirm,
        'DeregisterAppConfirmType': zehnder_pb2.DeregisterAppConfirm,
        'ChangePinConfirmType': zehnder_pb2.ChangePinConfirm,
        'GetRemoteAccessIdConfirmType': zehnder_pb2.GetRemoteAccessIdConfirm,
        'SetRemoteAccessIdConfirmType': zehnder_pb2.SetRemoteAccessIdConfirm,
        'GetSupportIdConfirmType': zehnder_pb2.GetSupportIdConfirm,
        'SetSupportIdConfirmType': zehnder_pb2.SetSupportIdConfirm,
        'GetWebIdConfirmType': zehnder_pb2.GetWebIdConfirm,
        'SetWebIdConfirmType': zehnder_pb2.SetWebIdConfirm,
        'SetPushIdConfirmType': zehnder_pb2.SetPushIdConfirm,
        'DebugConfirmType': zehnder_pb2.DebugConfirm,
        'UpgradeConfirmType': zehnder_pb2.UpgradeConfirm,
        'SetDeviceSettingsConfirmType': zehnder_pb2.SetDeviceSettingsConfirm,
        'VersionConfirmType': zehnder_pb2.VersionConfirm,
        'GatewayNotificationType': zehnder_pb2.GatewayNotification,
        'KeepAliveType': zehnder_pb2.KeepAlive,
        'FactoryResetType': zehnder_pb2.FactoryReset,
        'CnTimeRequestType': zehnder_pb2.CnTimeRequest,
        'CnTimeConfirmType': zehnder_pb2.CnTimeConfirm,
        'CnNodeRequestType': zehnder_pb2.CnNodeRequest,
        'CnNodeNotificationType': zehnder_pb2.CnNodeNotification,
        'CnRmiRequestType': zehnder_pb2.CnRmiRequest,
        'CnRmiResponseType': zehnder_pb2.CnRmiResponse,
        'CnRmiAsyncRequestType': zehnder_pb2.CnRmiAsyncRequest,
        'CnRmiAsyncConfirmType': zehnder_pb2.CnRmiAsyncConfirm,
        'CnRmiAsyncResponseType': zehnder_pb2.CnRmiAsyncResponse,
        'CnRpdoRequestType': zehnder_pb2.CnRpdoRequest,
        'CnRpdoConfirmType': zehnder_pb2.CnRpdoConfirm,
        'CnRpdoNotificationType': zehnder_pb2.CnRpdoNotification,
        'CnAlarmNotificationType': zehnder_pb2.CnAlarmNotification,
        'CnFupReadRegisterRequestType': zehnder_pb2.CnFupReadRegisterRequest,
        'CnFupReadRegisterConfirmType': zehnder_pb2.CnFupReadRegisterConfirm,
        'CnFupProgramBeginRequestType': zehnder_pb2.CnFupProgramBeginRequest,
        'CnFupProgramBeginConfirmType': zehnder_pb2.CnFupProgramBeginConfirm,
        'CnFupProgramRequestType': zehnder_pb2.CnFupProgramRequest,
        'CnFupProgramConfirmType': zehnder_pb2.CnFupProgramConfirm,
        'CnFupProgramEndRequestType': zehnder_pb2.CnFupProgramEndRequest,
        'CnFupProgramEndConfirmType': zehnder_pb2.CnFupProgramEndConfirm,
        'CnFupReadRequestType': zehnder_pb2.CnFupReadRequest,
        'CnFupReadConfirmType': zehnder_pb2.CnFupReadConfirm,
        'CnFupResetRequestType': zehnder_pb2.CnFupResetRequest,
        'CnFupResetConfirmType': zehnder_pb2.CnFupResetConfirm,
    }

    msg_len = None
    src = None
    dst = None
    cmd_len = None
    cmd = None
    msg = None

    def _lookup_(self, type):
        name = zehnder_pb2.GatewayOperation.OperationType.Name(type)
        return self.mapping.get(name)

    def __str__(self):
        return "%s %s %s %s %s %s" % (
            self.msg_len.hex(),
            self.src.hex(),
            self.dst.hex(),
            self.cmd_len.hex(),
            self.cmd.hex(),
            self.msg.hex()
        )

    def encode(self, local_uuid, uuid, cmd, msg):
        # Construct packet
        cmd_buf = cmd.SerializeToString()
        msg_buf = msg.SerializeToString()
        src_buf = bytearray.fromhex(local_uuid)
        dst_buf = bytearray.fromhex(uuid)
        cmd_len_buf = struct.pack('>H', len(cmd_buf))
        msg_len_buf = struct.pack('>L', 16 + 16 + 2 + len(cmd_buf) + len(msg_buf))

        self.msg_len = msg_len_buf
        self.src = src_buf
        self.dst = dst_buf
        self.cmd_len = cmd_len_buf
        self.cmd = cmd_buf
        self.msg = msg_buf

        return msg_len_buf + src_buf + dst_buf + cmd_len_buf + cmd_buf + msg_buf

    def decode(self, packet):
        # Read packet size
        msg_len_buf = packet[:4]
        msg_len = struct.unpack('>L', msg_len_buf)[0]

        # Read rest of packet
        msg_buf = packet[4:]

        # Extract headers
        src_buf = msg_buf[:16]
        dst_buf = msg_buf[16:32]
        cmd_len_buf = msg_buf[32:34]
        cmd_len = struct.unpack('>H', cmd_len_buf)[0]
        cmd_buf = msg_buf[34:34 + cmd_len]
        msg_buf = msg_buf[34 + cmd_len:]

        # Parse command
        cmd = zehnder_pb2.GatewayOperation()
        cmd.ParseFromString(cmd_buf)

        # Parse message
        msg_type = self._lookup_(cmd.type)
        msg = msg_type()
        msg.ParseFromString(msg_buf)

        self.msg_len = msg_len_buf
        self.src = src_buf
        self.dst = dst_buf
        self.cmd_len = cmd_len_buf
        self.cmd = cmd_buf
        self.msg = msg_buf

        return cmd, msg


class Bridge(object):
    ip = None
    uuid = None
    local_uuid = None
    version = None

    socket = None
    reference = None

    notification_callback = None

    def __init__(self, ip, uuid, version=1, notification_callback=None):
        self.ip = ip
        self.uuid = uuid
        self.version = version

        self.notification_callback = notification_callback

        self.reference = 15  # todo: random value

    def __str__(self):
        return "Bridge %s at %s" % (self.uuid, self.ip)

    def connect(self, local_uuid):
        self.local_uuid = local_uuid

        try:
            # Connect to bridge
            tcpsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcpsocket.settimeout(5)
            tcpsocket.connect((self.ip, BRIDGE_PORT))
            self.socket = tcpsocket

        except OSError:
            raise

        return True

    def _send_message(self, cmd, msg):
        # Construct packet
        message = Message()
        packet = message.encode(self.local_uuid, self.uuid, cmd, msg)

        # Debug message
        print("tx: %s" % message)
        print(cmd)
        print(msg)

        self.socket.sendall(packet)

    def _read_message(self):

        # Read packet size
        msg_len_buf = self.socket.recv(4)
        msg_len = struct.unpack('>L', msg_len_buf)[0]

        # Read rest of packet
        msg_buf = self.socket.recv(msg_len)

        # Extract headers
        message = Message()
        cmd, msg = message.decode(msg_len_buf + msg_buf)

        # Check if the message is for us
        if message.dst.hex() != self.local_uuid:
            raise BaseException(
                "Received message is not for us (us:%s != msg:%s)" % (self.local_uuid, message.dst.hex()))

        # Debug message
        print("rx: %s" % message)
        print(cmd)
        print(msg)

        return cmd, msg

    def ListRegisteredApps(self):
        cmd = zehnder_pb2.GatewayOperation()
        cmd.type = zehnder_pb2.GatewayOperation.OperationType.Value('ListRegisteredAppsRequestType')
        cmd.reference = self.reference

        msg = zehnder_pb2.ListRegisteredAppsRequest()

        # Send the message
        self.reference += 1
        self._send_message(cmd, msg)

        # Read feedback
        reply_cmd, reply_msg = self._read_message()

        if reply_cmd.result != zehnder_pb2.GatewayOperation.GatewayResult.Value('OK'):
            raise Exception('Unknown response')

        apps = []
        for app in reply_msg.apps:
            apps.append({
                'uuid': app.uuid.hex(),
                'devicename': app.devicename
            })

        return apps

    def RegisterApp(self, devicename, pin=0):
        cmd = zehnder_pb2.GatewayOperation()
        cmd.type = zehnder_pb2.GatewayOperation.OperationType.Value('RegisterAppRequestType')
        cmd.reference = self.reference

        msg = zehnder_pb2.RegisterAppRequest()
        msg.uuid = bytes.fromhex(self.local_uuid)
        msg.pin = pin
        msg.devicename = devicename

        # Send the message
        self.reference += 1
        self._send_message(cmd, msg)

        # Read feedback
        reply_cmd, reply_msg = self._read_message()

        # Check feedback
        if reply_cmd.result == zehnder_pb2.GatewayOperation.GatewayResult.Value('NOT_ALLOWED'):
            raise Exception('Access denied. Invalid PIN.')

        if reply_cmd.result != zehnder_pb2.GatewayOperation.GatewayResult.Value('OK'):
            raise Exception('Unknown response')

        return True

    def DeregisterApp(self, uuid):
        cmd = zehnder_pb2.GatewayOperation()
        cmd.type = zehnder_pb2.GatewayOperation.OperationType.Value('DeregisterAppRequestType')
        cmd.reference = self.reference

        msg = zehnder_pb2.DeregisterAppRequest()
        msg.uuid = bytes.fromhex(uuid)

        # Send the message
        self.reference += 1
        self._send_message(cmd, msg)

        # Read feedback
        reply_cmd, reply_msg = self._read_message()

        # Check feedback
        if reply_cmd.result != zehnder_pb2.GatewayOperation.GatewayResult.Value('OK'):
            raise Exception('Unknown response')

        return True

    def StartSession(self, takeover=False):
        cmd = zehnder_pb2.GatewayOperation()
        cmd.type = zehnder_pb2.GatewayOperation.OperationType.Value('StartSessionRequestType')
        cmd.reference = self.reference
        self.reference += 1

        msg = zehnder_pb2.StartSessionRequest()
        if takeover:
            msg.takeover = 1

        # Send the message
        self._send_message(cmd, msg)

        # Read feedback
        reply_cmd, reply_msg = self._read_message()

        # Check feedback
        if reply_cmd.result == zehnder_pb2.GatewayOperation.GatewayResult.Value('NOT_ALLOWED'):
            raise Exception('Access denied. Your app is probably not registered.')

        if reply_cmd.result != zehnder_pb2.GatewayOperation.GatewayResult.Value('OK'):
            raise Exception('Unknown response')

        return True

    def VersionRequest(self):
        cmd = zehnder_pb2.GatewayOperation()
        cmd.type = zehnder_pb2.GatewayOperation.OperationType.Value('VersionRequestType')
        cmd.reference = self.reference
        self.reference += 1

        msg = zehnder_pb2.VersionRequest()

        # Send the message
        self._send_message(cmd, msg)

        # Read feedback
        reply_cmd, reply_msg = self._read_message()

        # Check feedback
        if reply_cmd.result != zehnder_pb2.GatewayOperation.GatewayResult.Value('OK'):
            raise Exception('Unknown response')

        return {
            'gatewayVersion': reply_msg.gatewayVersion,
            'serialNumber': reply_msg.serialNumber,
            'comfoNetVersion': reply_msg.comfoNetVersion

        }

    def CnTimeRequest(self):
        cmd = zehnder_pb2.GatewayOperation()
        cmd.type = zehnder_pb2.GatewayOperation.OperationType.Value('CnTimeRequestType')
        cmd.reference = self.reference
        self.reference += 1

        msg = zehnder_pb2.CnTimeRequest()

        # Send the message
        self._send_message(cmd, msg)

        # Read feedback
        reply_cmd, reply_msg = self._read_message()

        # Check feedback
        if reply_cmd.result != zehnder_pb2.GatewayOperation.GatewayResult.Value('OK'):
            raise Exception('Unknown response')

        return reply_msg.currentTime

    def CloseSession(self):
        cmd = zehnder_pb2.GatewayOperation()
        cmd.type = zehnder_pb2.GatewayOperation.OperationType.Value('CloseSessionRequestType')
        cmd.reference = self.reference
        self.reference += 1

        msg = zehnder_pb2.CloseSessionRequest()

        # Send the message
        self._send_message(cmd, msg)

        return True

    def CnRmiRequest(self, nodeId, message):
        cmd = zehnder_pb2.GatewayOperation()
        cmd.type = zehnder_pb2.GatewayOperation.OperationType.Value('CnRmiRequestType')
        cmd.reference = self.reference
        self.reference += 1

        msg = zehnder_pb2.CnRmiRequest()
        msg.nodeId = nodeId
        msg.message = message

        # Send the message
        self._send_message(cmd, msg)

        # Read feedback
        reply_cmd, reply_msg = self._read_message()

        # Check feedback
        if reply_cmd.result != zehnder_pb2.GatewayOperation.GatewayResult.Value('OK'):
            raise Exception('Unknown response')

        return True

    def CnRpdoRequest(self, pdid, zone, type, timeout=4294967295):
        cmd = zehnder_pb2.GatewayOperation()
        cmd.type = zehnder_pb2.GatewayOperation.OperationType.Value('CnRpdoRequestType')
        cmd.reference = self.reference
        self.reference += 1

        msg = zehnder_pb2.CnRpdoRequest()
        msg.pdid = pdid
        msg.zone = zone
        msg.type = type
        msg.timeout = timeout

        # Send the message
        self._send_message(cmd, msg)

        # Read feedback
        reply_cmd, reply_msg = self._read_message()

        # Check feedback
        if reply_cmd.result != zehnder_pb2.GatewayOperation.GatewayResult.Value('OK'):
            raise Exception('Unknown response')

        return True

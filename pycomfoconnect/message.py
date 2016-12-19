import struct
from . import zehnder_pb2
from .error import *


class Message(object):
    mapping = {
        zehnder_pb2.GatewayOperation.SetAddressRequestType: zehnder_pb2.SetAddressRequest,
        zehnder_pb2.GatewayOperation.RegisterAppRequestType: zehnder_pb2.RegisterAppRequest,
        zehnder_pb2.GatewayOperation.StartSessionRequestType: zehnder_pb2.StartSessionRequest,
        zehnder_pb2.GatewayOperation.CloseSessionRequestType: zehnder_pb2.CloseSessionRequest,
        zehnder_pb2.GatewayOperation.ListRegisteredAppsRequestType: zehnder_pb2.ListRegisteredAppsRequest,
        zehnder_pb2.GatewayOperation.DeregisterAppRequestType: zehnder_pb2.DeregisterAppRequest,
        zehnder_pb2.GatewayOperation.ChangePinRequestType: zehnder_pb2.ChangePinRequest,
        zehnder_pb2.GatewayOperation.GetRemoteAccessIdRequestType: zehnder_pb2.GetRemoteAccessIdRequest,
        zehnder_pb2.GatewayOperation.SetRemoteAccessIdRequestType: zehnder_pb2.SetRemoteAccessIdRequest,
        zehnder_pb2.GatewayOperation.GetSupportIdRequestType: zehnder_pb2.GetSupportIdRequest,
        zehnder_pb2.GatewayOperation.SetSupportIdRequestType: zehnder_pb2.SetSupportIdRequest,
        zehnder_pb2.GatewayOperation.GetWebIdRequestType: zehnder_pb2.GetWebIdRequest,
        zehnder_pb2.GatewayOperation.SetWebIdRequestType: zehnder_pb2.SetWebIdRequest,
        zehnder_pb2.GatewayOperation.SetPushIdRequestType: zehnder_pb2.SetPushIdRequest,
        zehnder_pb2.GatewayOperation.DebugRequestType: zehnder_pb2.DebugRequest,
        zehnder_pb2.GatewayOperation.UpgradeRequestType: zehnder_pb2.UpgradeRequest,
        zehnder_pb2.GatewayOperation.SetDeviceSettingsRequestType: zehnder_pb2.SetDeviceSettingsRequest,
        zehnder_pb2.GatewayOperation.VersionRequestType: zehnder_pb2.VersionRequest,
        zehnder_pb2.GatewayOperation.SetAddressConfirmType: zehnder_pb2.SetAddressConfirm,
        zehnder_pb2.GatewayOperation.RegisterAppConfirmType: zehnder_pb2.RegisterAppConfirm,
        zehnder_pb2.GatewayOperation.StartSessionConfirmType: zehnder_pb2.StartSessionConfirm,
        zehnder_pb2.GatewayOperation.CloseSessionConfirmType: zehnder_pb2.CloseSessionConfirm,
        zehnder_pb2.GatewayOperation.ListRegisteredAppsConfirmType: zehnder_pb2.ListRegisteredAppsConfirm,
        zehnder_pb2.GatewayOperation.DeregisterAppConfirmType: zehnder_pb2.DeregisterAppConfirm,
        zehnder_pb2.GatewayOperation.ChangePinConfirmType: zehnder_pb2.ChangePinConfirm,
        zehnder_pb2.GatewayOperation.GetRemoteAccessIdConfirmType: zehnder_pb2.GetRemoteAccessIdConfirm,
        zehnder_pb2.GatewayOperation.SetRemoteAccessIdConfirmType: zehnder_pb2.SetRemoteAccessIdConfirm,
        zehnder_pb2.GatewayOperation.GetSupportIdConfirmType: zehnder_pb2.GetSupportIdConfirm,
        zehnder_pb2.GatewayOperation.SetSupportIdConfirmType: zehnder_pb2.SetSupportIdConfirm,
        zehnder_pb2.GatewayOperation.GetWebIdConfirmType: zehnder_pb2.GetWebIdConfirm,
        zehnder_pb2.GatewayOperation.SetWebIdConfirmType: zehnder_pb2.SetWebIdConfirm,
        zehnder_pb2.GatewayOperation.SetPushIdConfirmType: zehnder_pb2.SetPushIdConfirm,
        zehnder_pb2.GatewayOperation.DebugConfirmType: zehnder_pb2.DebugConfirm,
        zehnder_pb2.GatewayOperation.UpgradeConfirmType: zehnder_pb2.UpgradeConfirm,
        zehnder_pb2.GatewayOperation.SetDeviceSettingsConfirmType: zehnder_pb2.SetDeviceSettingsConfirm,
        zehnder_pb2.GatewayOperation.VersionConfirmType: zehnder_pb2.VersionConfirm,
        zehnder_pb2.GatewayOperation.GatewayNotificationType: zehnder_pb2.GatewayNotification,
        zehnder_pb2.GatewayOperation.KeepAliveType: zehnder_pb2.KeepAlive,
        zehnder_pb2.GatewayOperation.FactoryResetType: zehnder_pb2.FactoryReset,
        zehnder_pb2.GatewayOperation.CnTimeRequestType: zehnder_pb2.CnTimeRequest,
        zehnder_pb2.GatewayOperation.CnTimeConfirmType: zehnder_pb2.CnTimeConfirm,
        zehnder_pb2.GatewayOperation.CnNodeRequestType: zehnder_pb2.CnNodeRequest,
        zehnder_pb2.GatewayOperation.CnNodeNotificationType: zehnder_pb2.CnNodeNotification,
        zehnder_pb2.GatewayOperation.CnRmiRequestType: zehnder_pb2.CnRmiRequest,
        zehnder_pb2.GatewayOperation.CnRmiResponseType: zehnder_pb2.CnRmiResponse,
        zehnder_pb2.GatewayOperation.CnRmiAsyncRequestType: zehnder_pb2.CnRmiAsyncRequest,
        zehnder_pb2.GatewayOperation.CnRmiAsyncConfirmType: zehnder_pb2.CnRmiAsyncConfirm,
        zehnder_pb2.GatewayOperation.CnRmiAsyncResponseType: zehnder_pb2.CnRmiAsyncResponse,
        zehnder_pb2.GatewayOperation.CnRpdoRequestType: zehnder_pb2.CnRpdoRequest,
        zehnder_pb2.GatewayOperation.CnRpdoConfirmType: zehnder_pb2.CnRpdoConfirm,
        zehnder_pb2.GatewayOperation.CnRpdoNotificationType: zehnder_pb2.CnRpdoNotification,
        zehnder_pb2.GatewayOperation.CnAlarmNotificationType: zehnder_pb2.CnAlarmNotification,
        zehnder_pb2.GatewayOperation.CnFupReadRegisterRequestType: zehnder_pb2.CnFupReadRegisterRequest,
        zehnder_pb2.GatewayOperation.CnFupReadRegisterConfirmType: zehnder_pb2.CnFupReadRegisterConfirm,
        zehnder_pb2.GatewayOperation.CnFupProgramBeginRequestType: zehnder_pb2.CnFupProgramBeginRequest,
        zehnder_pb2.GatewayOperation.CnFupProgramBeginConfirmType: zehnder_pb2.CnFupProgramBeginConfirm,
        zehnder_pb2.GatewayOperation.CnFupProgramRequestType: zehnder_pb2.CnFupProgramRequest,
        zehnder_pb2.GatewayOperation.CnFupProgramConfirmType: zehnder_pb2.CnFupProgramConfirm,
        zehnder_pb2.GatewayOperation.CnFupProgramEndRequestType: zehnder_pb2.CnFupProgramEndRequest,
        zehnder_pb2.GatewayOperation.CnFupProgramEndConfirmType: zehnder_pb2.CnFupProgramEndConfirm,
        zehnder_pb2.GatewayOperation.CnFupReadRequestType: zehnder_pb2.CnFupReadRequest,
        zehnder_pb2.GatewayOperation.CnFupReadConfirmType: zehnder_pb2.CnFupReadConfirm,
        zehnder_pb2.GatewayOperation.CnFupResetRequestType: zehnder_pb2.CnFupResetRequest,
        zehnder_pb2.GatewayOperation.CnFupResetConfirmType: zehnder_pb2.CnFupResetConfirm,
    }

    src = None
    dst = None
    cmd = None
    msg = None

    def __init__(self, cmd, msg, src, dst):
        self.cmd = cmd
        self.msg = msg
        self.src = src
        self.dst = dst

    def __str__(self):
        return "%s -> %s: %s %s\n%s\n%s" % (
            self.src.hex(),
            self.dst.hex(),
            self.cmd.SerializeToString().hex(),
            self.msg.SerializeToString().hex(),
            self.cmd,
            self.msg,
        )

    def encode(self):
        cmd_buf = self.cmd.SerializeToString()
        msg_buf = self.msg.SerializeToString()
        cmd_len_buf = struct.pack('>H', len(cmd_buf))
        msg_len_buf = struct.pack('>L', 16 + 16 + 2 + len(cmd_buf) + len(msg_buf))

        return msg_len_buf + self.src + self.dst + cmd_len_buf + cmd_buf + msg_buf

    @classmethod
    def decode(cls, packet):

        src_buf = packet[4:20]
        dst_buf = packet[20:36]
        cmd_len = struct.unpack('>H', packet[36:38])[0]
        cmd_buf = packet[38:38 + cmd_len]
        msg_buf = packet[38 + cmd_len:]

        # Parse command
        cmd = zehnder_pb2.GatewayOperation()
        cmd.ParseFromString(cmd_buf)

        # Check status code
        if cmd.result == zehnder_pb2.GatewayOperation.OK:
            pass
        elif cmd.result == zehnder_pb2.GatewayOperation.BAD_REQUEST:
            raise PyComfoConnectBadRequest()
        elif cmd.result == zehnder_pb2.GatewayOperation.INTERNAL_ERROR:
            raise PyComfoConnectInternalError()
        elif cmd.result == zehnder_pb2.GatewayOperation.NOT_REACHABLE:
            raise PyComfoConnectNotReachable()
        elif cmd.result == zehnder_pb2.GatewayOperation.CONNECT_OTHER_SESSION:
            raise PyComfoConnectOtherSession()
        elif cmd.result == zehnder_pb2.GatewayOperation.NOT_ALLOWED:
            raise PyComfoConnectNotAllowed()
        elif cmd.result == zehnder_pb2.GatewayOperation.NO_RESOURCES:
            raise PyComfoConnectNoResources()
        elif cmd.result == zehnder_pb2.GatewayOperation.NOT_EXISTS:
            raise PyComfoConnectNotExists()
        elif cmd.result == zehnder_pb2.GatewayOperation.RMI_ERROR:
            raise PyComfoConnectRmiError()

        # Parse message
        cmd_type = cls.mapping.get(cmd.type)
        msg = cmd_type()
        msg.ParseFromString(msg_buf)

        return Message(cmd, msg, src_buf, dst_buf)

    @staticmethod
    def decode_discovery(packet):

        # Parse command
        parser = zehnder_pb2.DiscoveryOperation()
        parser.ParseFromString(packet)

        return {
            'ip_address': parser.searchGatewayResponse.ipaddress,
            'uuid': parser.searchGatewayResponse.uuid,
            'version': parser.searchGatewayResponse.version,
        }

import struct

from .error import *
from .zehnder_pb2 import *


class Message(object):
    class_to_type = {
        SetAddressRequest: GatewayOperation.SetAddressRequestType,
        RegisterAppRequest: GatewayOperation.RegisterAppRequestType,
        StartSessionRequest: GatewayOperation.StartSessionRequestType,
        CloseSessionRequest: GatewayOperation.CloseSessionRequestType,
        ListRegisteredAppsRequest: GatewayOperation.ListRegisteredAppsRequestType,
        DeregisterAppRequest: GatewayOperation.DeregisterAppRequestType,
        ChangePinRequest: GatewayOperation.ChangePinRequestType,
        GetRemoteAccessIdRequest: GatewayOperation.GetRemoteAccessIdRequestType,
        SetRemoteAccessIdRequest: GatewayOperation.SetRemoteAccessIdRequestType,
        GetSupportIdRequest: GatewayOperation.GetSupportIdRequestType,
        SetSupportIdRequest: GatewayOperation.SetSupportIdRequestType,
        GetWebIdRequest: GatewayOperation.GetWebIdRequestType,
        SetWebIdRequest: GatewayOperation.SetWebIdRequestType,
        SetPushIdRequest: GatewayOperation.SetPushIdRequestType,
        DebugRequest: GatewayOperation.DebugRequestType,
        UpgradeRequest: GatewayOperation.UpgradeRequestType,
        SetDeviceSettingsRequest: GatewayOperation.SetDeviceSettingsRequestType,
        VersionRequest: GatewayOperation.VersionRequestType,
        SetAddressConfirm: GatewayOperation.SetAddressConfirmType,
        RegisterAppConfirm: GatewayOperation.RegisterAppConfirmType,
        StartSessionConfirm: GatewayOperation.StartSessionConfirmType,
        CloseSessionConfirm: GatewayOperation.CloseSessionConfirmType,
        ListRegisteredAppsConfirm: GatewayOperation.ListRegisteredAppsConfirmType,
        DeregisterAppConfirm: GatewayOperation.DeregisterAppConfirmType,
        ChangePinConfirm: GatewayOperation.ChangePinConfirmType,
        GetRemoteAccessIdConfirm: GatewayOperation.GetRemoteAccessIdConfirmType,
        SetRemoteAccessIdConfirm: GatewayOperation.SetRemoteAccessIdConfirmType,
        GetSupportIdConfirm: GatewayOperation.GetSupportIdConfirmType,
        SetSupportIdConfirm: GatewayOperation.SetSupportIdConfirmType,
        GetWebIdConfirm: GatewayOperation.GetWebIdConfirmType,
        SetWebIdConfirm: GatewayOperation.SetWebIdConfirmType,
        SetPushIdConfirm: GatewayOperation.SetPushIdConfirmType,
        DebugConfirm: GatewayOperation.DebugConfirmType,
        UpgradeConfirm: GatewayOperation.UpgradeConfirmType,
        SetDeviceSettingsConfirm: GatewayOperation.SetDeviceSettingsConfirmType,
        VersionConfirm: GatewayOperation.VersionConfirmType,
        GatewayNotification: GatewayOperation.GatewayNotificationType,
        KeepAlive: GatewayOperation.KeepAliveType,
        FactoryReset: GatewayOperation.FactoryResetType,
        CnTimeRequest: GatewayOperation.CnTimeRequestType,
        CnTimeConfirm: GatewayOperation.CnTimeConfirmType,
        CnNodeRequest: GatewayOperation.CnNodeRequestType,
        CnNodeNotification: GatewayOperation.CnNodeNotificationType,
        CnRmiRequest: GatewayOperation.CnRmiRequestType,
        CnRmiResponse: GatewayOperation.CnRmiResponseType,
        CnRmiAsyncRequest: GatewayOperation.CnRmiAsyncRequestType,
        CnRmiAsyncConfirm: GatewayOperation.CnRmiAsyncConfirmType,
        CnRmiAsyncResponse: GatewayOperation.CnRmiAsyncResponseType,
        CnRpdoRequest: GatewayOperation.CnRpdoRequestType,
        CnRpdoConfirm: GatewayOperation.CnRpdoConfirmType,
        CnRpdoNotification: GatewayOperation.CnRpdoNotificationType,
        CnAlarmNotification: GatewayOperation.CnAlarmNotificationType,
        CnFupReadRegisterRequest: GatewayOperation.CnFupReadRegisterRequestType,
        CnFupReadRegisterConfirm: GatewayOperation.CnFupReadRegisterConfirmType,
        CnFupProgramBeginRequest: GatewayOperation.CnFupProgramBeginRequestType,
        CnFupProgramBeginConfirm: GatewayOperation.CnFupProgramBeginConfirmType,
        CnFupProgramRequest: GatewayOperation.CnFupProgramRequestType,
        CnFupProgramConfirm: GatewayOperation.CnFupProgramConfirmType,
        CnFupProgramEndRequest: GatewayOperation.CnFupProgramEndRequestType,
        CnFupProgramEndConfirm: GatewayOperation.CnFupProgramEndConfirmType,
        CnFupReadRequest: GatewayOperation.CnFupReadRequestType,
        CnFupReadConfirm: GatewayOperation.CnFupReadConfirmType,
        CnFupResetRequest: GatewayOperation.CnFupResetRequestType,
        CnFupResetConfirm: GatewayOperation.CnFupResetConfirmType,
    }

    class_to_confirm = {
        SetAddressRequest: SetAddressConfirm,
        RegisterAppRequest: RegisterAppConfirm,
        StartSessionRequest: StartSessionConfirm,
        CloseSessionRequest: CloseSessionConfirm,
        ListRegisteredAppsRequest: ListRegisteredAppsConfirm,
        DeregisterAppRequest: DeregisterAppConfirm,
        ChangePinRequest: ChangePinConfirm,
        GetRemoteAccessIdRequest: GetRemoteAccessIdConfirm,
        SetRemoteAccessIdRequest: SetRemoteAccessIdConfirm,
        GetSupportIdRequest: GetSupportIdConfirm,
        SetSupportIdRequest: SetSupportIdConfirm,
        GetWebIdRequest: GetWebIdConfirm,
        SetWebIdRequest: SetWebIdConfirm,
        SetPushIdRequest: SetPushIdConfirm,
        DebugRequest: DebugConfirm,
        UpgradeRequest: UpgradeConfirm,
        SetDeviceSettingsRequest: SetDeviceSettingsConfirm,
        VersionRequest: VersionConfirm,
        CnTimeRequest: CnTimeConfirm,
        CnRmiRequest: CnRmiResponse,
        CnRmiAsyncRequest: CnRmiAsyncConfirm,
        CnRpdoRequest: CnRpdoConfirm,
        CnFupReadRegisterRequest: CnFupReadRegisterConfirm,
        CnFupProgramBeginRequest: CnFupProgramBeginConfirm,
        CnFupProgramRequest: CnFupProgramConfirm,
        CnFupProgramEndRequest: CnFupProgramEndConfirm,
        CnFupReadRequest: CnFupReadConfirm,
        CnFupResetRequest: CnFupResetConfirm,
    }

    request_type_to_class_mapping = {
        GatewayOperation.SetAddressRequestType: SetAddressRequest,
        GatewayOperation.RegisterAppRequestType: RegisterAppRequest,
        GatewayOperation.StartSessionRequestType: StartSessionRequest,
        GatewayOperation.CloseSessionRequestType: CloseSessionRequest,
        GatewayOperation.ListRegisteredAppsRequestType: ListRegisteredAppsRequest,
        GatewayOperation.DeregisterAppRequestType: DeregisterAppRequest,
        GatewayOperation.ChangePinRequestType: ChangePinRequest,
        GatewayOperation.GetRemoteAccessIdRequestType: GetRemoteAccessIdRequest,
        GatewayOperation.SetRemoteAccessIdRequestType: SetRemoteAccessIdRequest,
        GatewayOperation.GetSupportIdRequestType: GetSupportIdRequest,
        GatewayOperation.SetSupportIdRequestType: SetSupportIdRequest,
        GatewayOperation.GetWebIdRequestType: GetWebIdRequest,
        GatewayOperation.SetWebIdRequestType: SetWebIdRequest,
        GatewayOperation.SetPushIdRequestType: SetPushIdRequest,
        GatewayOperation.DebugRequestType: DebugRequest,
        GatewayOperation.UpgradeRequestType: UpgradeRequest,
        GatewayOperation.SetDeviceSettingsRequestType: SetDeviceSettingsRequest,
        GatewayOperation.VersionRequestType: VersionRequest,
        GatewayOperation.SetAddressConfirmType: SetAddressConfirm,
        GatewayOperation.RegisterAppConfirmType: RegisterAppConfirm,
        GatewayOperation.StartSessionConfirmType: StartSessionConfirm,
        GatewayOperation.CloseSessionConfirmType: CloseSessionConfirm,
        GatewayOperation.ListRegisteredAppsConfirmType: ListRegisteredAppsConfirm,
        GatewayOperation.DeregisterAppConfirmType: DeregisterAppConfirm,
        GatewayOperation.ChangePinConfirmType: ChangePinConfirm,
        GatewayOperation.GetRemoteAccessIdConfirmType: GetRemoteAccessIdConfirm,
        GatewayOperation.SetRemoteAccessIdConfirmType: SetRemoteAccessIdConfirm,
        GatewayOperation.GetSupportIdConfirmType: GetSupportIdConfirm,
        GatewayOperation.SetSupportIdConfirmType: SetSupportIdConfirm,
        GatewayOperation.GetWebIdConfirmType: GetWebIdConfirm,
        GatewayOperation.SetWebIdConfirmType: SetWebIdConfirm,
        GatewayOperation.SetPushIdConfirmType: SetPushIdConfirm,
        GatewayOperation.DebugConfirmType: DebugConfirm,
        GatewayOperation.UpgradeConfirmType: UpgradeConfirm,
        GatewayOperation.SetDeviceSettingsConfirmType: SetDeviceSettingsConfirm,
        GatewayOperation.VersionConfirmType: VersionConfirm,
        GatewayOperation.GatewayNotificationType: GatewayNotification,
        GatewayOperation.KeepAliveType: KeepAlive,
        GatewayOperation.FactoryResetType: FactoryReset,
        GatewayOperation.CnTimeRequestType: CnTimeRequest,
        GatewayOperation.CnTimeConfirmType: CnTimeConfirm,
        GatewayOperation.CnNodeRequestType: CnNodeRequest,
        GatewayOperation.CnNodeNotificationType: CnNodeNotification,
        GatewayOperation.CnRmiRequestType: CnRmiRequest,
        GatewayOperation.CnRmiResponseType: CnRmiResponse,
        GatewayOperation.CnRmiAsyncRequestType: CnRmiAsyncRequest,
        GatewayOperation.CnRmiAsyncConfirmType: CnRmiAsyncConfirm,
        GatewayOperation.CnRmiAsyncResponseType: CnRmiAsyncResponse,
        GatewayOperation.CnRpdoRequestType: CnRpdoRequest,
        GatewayOperation.CnRpdoConfirmType: CnRpdoConfirm,
        GatewayOperation.CnRpdoNotificationType: CnRpdoNotification,
        GatewayOperation.CnAlarmNotificationType: CnAlarmNotification,
        GatewayOperation.CnFupReadRegisterRequestType: CnFupReadRegisterRequest,
        GatewayOperation.CnFupReadRegisterConfirmType: CnFupReadRegisterConfirm,
        GatewayOperation.CnFupProgramBeginRequestType: CnFupProgramBeginRequest,
        GatewayOperation.CnFupProgramBeginConfirmType: CnFupProgramBeginConfirm,
        GatewayOperation.CnFupProgramRequestType: CnFupProgramRequest,
        GatewayOperation.CnFupProgramConfirmType: CnFupProgramConfirm,
        GatewayOperation.CnFupProgramEndRequestType: CnFupProgramEndRequest,
        GatewayOperation.CnFupProgramEndConfirmType: CnFupProgramEndConfirm,
        GatewayOperation.CnFupReadRequestType: CnFupReadRequest,
        GatewayOperation.CnFupReadConfirmType: CnFupReadConfirm,
        GatewayOperation.CnFupResetRequestType: CnFupResetRequest,
        GatewayOperation.CnFupResetConfirmType: CnFupResetConfirm,
    }

    def __init__(self, cmd, msg, src, dst):
        self.cmd = cmd
        self.msg = msg
        self.src = src
        self.dst = dst

    @classmethod
    def create(cls, src, dst, command, cmd_params=None, msg_params=None):

        cmd = GatewayOperation()
        cmd.type = cls.class_to_type[command]
        if cmd_params is not None:
            for param in cmd_params:
                if cmd_params[param] is not None:
                    setattr(cmd, param, cmd_params[param])

        msg = command()
        if msg_params is not None:
            for param in msg_params:
                if msg_params[param] is not None:
                    setattr(msg, param, msg_params[param])

        return Message(cmd, msg, src, dst)

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
        cmd = GatewayOperation()
        cmd.ParseFromString(cmd_buf)

        # Parse message
        cmd_type = cls.request_type_to_class_mapping.get(cmd.type)
        msg = cmd_type()
        msg.ParseFromString(msg_buf)

        return Message(cmd, msg, src_buf, dst_buf)

#!/usr/bin/python3
import socket
from zehnder_pb2 import *
import struct

def _lookup_class(type):
    mapping = {
        'SetAddressRequestType': SetAddressRequest,
        'RegisterAppRequestType': RegisterAppRequest,
        'StartSessionRequestType': StartSessionRequest,
        'CloseSessionRequestType': CloseSessionRequest,
        'ListRegisteredAppsRequestType': ListRegisteredAppsRequest,
        'DeregisterAppRequestType': DeregisterAppRequest,
        'ChangePinRequestType': ChangePinRequest,
        'GetRemoteAccessIdRequestType': GetRemoteAccessIdRequest,
        'SetRemoteAccessIdRequestType': SetRemoteAccessIdRequest,
        'GetSupportIdRequestType': GetSupportIdRequest,
        'SetSupportIdRequestType': SetSupportIdRequest,
        'GetWebIdRequestType': GetWebIdRequest,
        'SetWebIdRequestType': SetWebIdRequest,
        'SetPushIdRequestType': SetPushIdRequest,
        'DebugRequestType': DebugRequest,
        'UpgradeRequestType': UpgradeRequest,
        'SetDeviceSettingsRequestType': SetDeviceSettingsRequest,
        'VersionRequestType': VersionRequest,
        'SetAddressConfirmType': SetAddressConfirm,
        'RegisterAppConfirmType': RegisterAppConfirm,
        'StartSessionConfirmType': StartSessionConfirm,
        'CloseSessionConfirmType': CloseSessionConfirm,
        'ListRegisteredAppsConfirmType': ListRegisteredAppsConfirm,
        'DeregisterAppConfirmType': DeregisterAppConfirm,
        'ChangePinConfirmType': ChangePinConfirm,
        'GetRemoteAccessIdConfirmType': GetRemoteAccessIdConfirm,
        'SetRemoteAccessIdConfirmType': SetRemoteAccessIdConfirm,
        'GetSupportIdConfirmType': GetSupportIdConfirm,
        'SetSupportIdConfirmType': SetSupportIdConfirm,
        'GetWebIdConfirmType': GetWebIdConfirm,
        'SetWebIdConfirmType': SetWebIdConfirm,
        'SetPushIdConfirmType': SetPushIdConfirm,
        'DebugConfirmType': DebugConfirm,
        'UpgradeConfirmType': UpgradeConfirm,
        'SetDeviceSettingsConfirmType': SetDeviceSettingsConfirm,
        'VersionConfirmType': VersionConfirm,
        'GatewayNotificationType': GatewayNotification,
        'KeepAliveType': KeepAlive,
        'FactoryResetType': FactoryReset,
        'CnTimeRequestType': CnTimeRequest,
        'CnTimeConfirmType': CnTimeConfirm,
        'CnNodeRequestType': CnNodeRequest,
        'CnNodeNotificationType': CnNodeNotification,
        'CnRmiRequestType': CnRmiRequest,
        'CnRmiResponseType': CnRmiResponse,
        'CnRmiAsyncRequestType': CnRmiAsyncRequest,
        'CnRmiAsyncConfirmType': CnRmiAsyncConfirm,
        'CnRmiAsyncResponseType': CnRmiAsyncResponse,
        'CnRpdoRequestType': CnRpdoRequest,
        'CnRpdoConfirmType': CnRpdoConfirm,
        'CnRpdoNotificationType': CnRpdoNotification,
        'CnAlarmNotificationType': CnAlarmNotification,
        'CnFupReadRegisterRequestType': CnFupReadRegisterRequest,
        'CnFupReadRegisterConfirmType': CnFupReadRegisterConfirm,
        'CnFupProgramBeginRequestType': CnFupProgramBeginRequest,
        'CnFupProgramBeginConfirmType': CnFupProgramBeginConfirm,
        'CnFupProgramRequestType': CnFupProgramRequest,
        'CnFupProgramConfirmType': CnFupProgramConfirm,
        'CnFupProgramEndRequestType': CnFupProgramEndRequest,
        'CnFupProgramEndConfirmType': CnFupProgramEndConfirm,
        'CnFupReadRequestType': CnFupReadRequest,
        'CnFupReadConfirmType': CnFupReadConfirm,
        'CnFupResetRequestType': CnFupResetRequest,
        'CnFupResetConfirmType': CnFupResetConfirm,
    }
    return mapping.get(type)

def decode(message):

    msg_buf = bytes(message)

    # Read full packet
    msg_len_buf = message[:4]
    msg_len = struct.unpack('>L', msg_len_buf)[0]
    msg_buf = message[4:]

    # Extract headers
    src_buf = msg_buf[:16]
    dst_buf = msg_buf[16:32]
    cmd_len_buf = msg_buf[32:34]
    cmd_len = struct.unpack('>H', cmd_len_buf)[0]
    cmd_buf = msg_buf[34:34+cmd_len]
    msg_buf = msg_buf[34+cmd_len:]

    print('Message length: %s' % msg_len)
    print('Source:         %s' % src_buf.hex())
    print('Destination:    %s' % dst_buf.hex())
    print('Command length: %s' % cmd_len)
    print()

    print('Command:')
    cmd = GatewayOperation()
    cmd.ParseFromString(bytes(cmd_buf))
    print(cmd)

    print('Message:')
    msgtype = _lookup_class(GatewayOperation.OperationType.Name(cmd.type))
    msg = msgtype()
    msg.ParseFromString(bytes(msg_buf))
    print(msg)


try:
    while True:
        msg = input()
        msg_bin = bytearray.fromhex(msg)
        decode(msg_bin)
except EOFError:
    exit()


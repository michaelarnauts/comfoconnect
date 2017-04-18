"""
PyComfoConnect: Manage your Zehnder ComfoConnect Q350/Q450/Q650 ventilation unit
"""
from __future__ import print_function

from .bridge import *
from .const import *
from .error import *
from .message import *
from .zehnder_pb2 import *


class ComfoConnect(object):
    def __init__(self, bridge: Bridge, callback=None, debug=False):
        self._bridge = bridge
        self._callback = callback
        self.requests = []

        # Set debug mode
        self._bridge.debug = debug

    def connect(self, local_uuid, local_name, pin):
        """Connect to the bridge and login."""

        try:
            # Open connection
            self._bridge.connect(local_uuid, self._callback_method)

            # Login
            self._bridge.StartSession(False)

        except PyComfoConnectNotAllowed:
            # Register with the bridge
            self._bridge.RegisterApp(local_name, pin)

            # Login
            self._bridge.StartSession(False)

        # Request version info
        version_info = self._bridge.VersionRequest()
        return version_info

    def disconnect(self):
        """Logout and disconnect from the bridge."""

        # Logout
        self._bridge.CloseSession()

        # Close socket connection
        self._bridge.disconnect()

    def is_connected(self):
        """Check if we are still connected to the bridge."""
        return self._bridge.is_connected()

    def _callback_method(self, msg: Message):
        if self._callback is None:
            return False

        if msg.cmd.type != zehnder_pb2.GatewayOperation.CnRpdoNotificationType:
            return False

        data = msg.msg.data.hex()
        if len(data) == 2:
            val = struct.unpack('b', msg.msg.data)[0]
        elif len(data) == 4:
            val = struct.unpack('h', msg.msg.data)[0]
        elif len(data) == 8:
            val = data
        else:
            val = data

        self._callback(msg.msg.pdid, val)

    def set_fan_mode(self, mode: int, node: int = 1):
        if mode == FAN_MODE_AWAY:
            cmd = CMD_FAN_MODE_AWAY
        elif mode == FAN_MODE_LOW:
            cmd = CMD_FAN_MODE_LOW
        elif mode == FAN_MODE_MEDIUM:
            cmd = CMD_FAN_MODE_MEDIUM
        elif mode == FAN_MODE_HIGH:
            cmd = CMD_FAN_MODE_HIGH
        else:
            raise Exception('Unknown fan mode.')

        self._bridge.CnRmiRequest(node, cmd)

    def request(self, parameter, node=1):
        if not parameter in SIZE_MAP:
            raise Exception('Unknown parameter.')

        self._bridge.CnRpdoRequest(parameter, node, SIZE_MAP.get(parameter))

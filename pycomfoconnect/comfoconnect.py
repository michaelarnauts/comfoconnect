import logging
import queue
import struct
import threading
import time

from .bridge import Bridge
from .error import *
from .message import Message
from .zehnder_pb2 import *

KEEPALIVE = 60

DEFAULT_LOCAL_UUID = bytes.fromhex('00000000000000000000000000001337')
DEFAULT_LOCAL_DEVICENAME = 'pycomfoconnect'
DEFAULT_PIN = 0

_LOGGER = logging.getLogger('comfoconnect')

# Sensor variable size
RPDO_TYPE_MAP = {
    16: 1,
    33: 1,
    37: 1,
    49: 1,
    53: 1,
    56: 1,
    65: 1,
    66: 1,
    67: 1,
    70: 1,
    71: 1,
    81: 3,
    82: 3,
    85: 3,
    86: 3,
    87: 3,
    117: 1,
    118: 1,
    119: 2,
    120: 2,
    121: 2,
    122: 2,
    128: 2,
    129: 2,
    130: 2,
    144: 2,
    145: 2,
    146: 2,
    176: 1,
    192: 2,
    208: 1,
    209: 6,
    210: 0,
    211: 0,
    212: 6,
    213: 2,
    214: 2,
    215: 2,
    216: 2,
    217: 2,
    218: 2,
    219: 2,
    221: 6,
    224: 1,
    225: 1,
    226: 2,
    227: 1,
    228: 1,
    274: 6,
    275: 6,
    276: 6,
    277: 6,
    290: 1,
    291: 1,
    292: 1,
    293: 1,
    294: 1,
    321: 2,
    325: 2,
    337: 3,
    338: 3,
    341: 3,
    369: 1,
    370: 1,
    371: 1,
    372: 1,
    384: 6,
    386: 0,
    400: 6,
    401: 1,
    402: 0,
    416: 6,
    417: 6,
    418: 1,
    419: 0,
}

# Product ID Map
PRODUCT_ID_MAP = {
    1: "ComfoAirQ",
    2: "ComfoSense",
    3: "ComfoSwitch",
    4: "OptionBox",
    5: "ZehnderGateway",
    6: "ComfoCool",
    7: "KNXGateway",
    8: "Service Tool",
    9: "Production test tool",
    10: "Design verification test tool"
}

class ComfoConnect(object):
    """Implements the commands to communicate with the ComfoConnect ventilation unit."""

    """Callback function to invoke when sensor updates are received."""
    callback_sensor = None

    def __init__(self, bridge: Bridge, local_uuid=DEFAULT_LOCAL_UUID, local_devicename=DEFAULT_LOCAL_DEVICENAME,
                 pin=DEFAULT_PIN):
        self._bridge = bridge
        self._local_uuid = local_uuid
        self._local_devicename = local_devicename
        self._pin = pin
        self._reference = 1

        self._queue = queue.Queue()
        self._connected = threading.Event()
        self._stopping = False
        self._message_thread = None
        self._connection_thread = None

        self.sensors = {}

    # ==================================================================================================================
    # Core functions
    # ==================================================================================================================

    def connect(self, takeover=False):
        """Connect to the bridge and login. Disconnect existing clients if needed by default."""

        try:
            # Start connection
            self._connect(takeover=takeover)

        except PyComfoConnectNotAllowed:
            raise Exception('Could not connect to the bridge since the PIN seems to be invalid.')

        except PyComfoConnectOtherSession:
            raise Exception('Could not connect to the bridge since there is already an open session.')

        except Exception as exc:
            _LOGGER.error(exc)
            raise Exception('Could not connect to the bridge.')

        # Set the stopping flag
        self._stopping = False
        self._connected.clear()

        # Start connection thread
        self._connection_thread = threading.Thread(target=self._connection_thread_loop)
        self._connection_thread.start()

        if not self._connected.wait(10):
            raise Exception('Could not connect to bridge since it didn\'t reply on time.')

        return True

    def disconnect(self):
        """Disconnect from the bridge."""

        # Set the stopping flag
        self._stopping = True

        # Wait for the background thread to finish
        self._connection_thread.join()
        self._connection_thread = None

    def is_connected(self):
        """Returns whether there is a connection with the bridge."""

        return self._bridge.is_connected()

    def register_sensor(self, sensor_id: int, sensor_type: int = None):
        """Register a sensor on the bridge and keep it in memory that we are registered to this sensor."""

        if not sensor_type:
            sensor_type = RPDO_TYPE_MAP.get(sensor_id)

        if sensor_type is None:
            raise Exception("Registering sensor %d with unknown type" % sensor_id)

        # Register on bridge
        try:
            reply = self.cmd_rpdo_request(sensor_id, sensor_type)

        except PyComfoConnectNotAllowed:
            return None

        # Register in memory
        self.sensors[sensor_id] = sensor_type

        return reply

    def unregister_sensor(self, sensor_id: int, sensor_type: int = None):
        """Register a sensor on the bridge and keep it in memory that we are registered to this sensor."""

        if sensor_type is None:
            sensor_type = RPDO_TYPE_MAP.get(sensor_id)

        if sensor_type is None:
            raise Exception("Unregistering sensor %d with unknown type" % sensor_id)

        # Unregister in memory
        self.sensors.pop(sensor_id, None)

        # Unregister on bridge
        self.cmd_rpdo_request(sensor_id, sensor_type, timeout=0)

    def _command(self, command, params=None, use_queue=True):
        """Sends a command and wait for a response if the request is known to return a result."""

        # Construct the message
        message = Message.create(
            self._local_uuid,
            self._bridge.uuid,
            command,
            {'reference': self._reference},
            params
        )

        # Increase message reference
        self._reference += 1

        # Send the message
        self._bridge.write_message(message)

        try:
            # Check if this command has a confirm type set
            confirm_type = message.class_to_confirm[command]

            # Read a message
            reply = self._get_reply(confirm_type, use_queue=use_queue)

            return reply

        except KeyError:
            return None

    def _get_reply(self, confirm_type=None, timeout=5, use_queue=True):
        """Pops a message of the queue, optionally looking for a specific type."""

        start = time.time()

        while True:
            message = None

            if use_queue:
                try:
                    # Fetch the message from the queue.  The network thread has put it there for us.
                    message = self._queue.get(timeout=timeout)
                    if message:
                        self._queue.task_done()
                except queue.Empty:
                    # We got no message
                    pass

            else:
                # Fetch the message directly from the socket
                message = self._bridge.read_message(timeout=timeout)

            if message:
                # Check status code
                if message.cmd.result == GatewayOperation.OK:
                    pass
                elif message.cmd.result == GatewayOperation.BAD_REQUEST:
                    raise PyComfoConnectBadRequest()
                elif message.cmd.result == GatewayOperation.INTERNAL_ERROR:
                    raise PyComfoConnectInternalError()
                elif message.cmd.result == GatewayOperation.NOT_REACHABLE:
                    raise PyComfoConnectNotReachable()
                elif message.cmd.result == GatewayOperation.OTHER_SESSION:
                    raise PyComfoConnectOtherSession(message.msg.devicename)
                elif message.cmd.result == GatewayOperation.NOT_ALLOWED:
                    raise PyComfoConnectNotAllowed()
                elif message.cmd.result == GatewayOperation.NO_RESOURCES:
                    raise PyComfoConnectNoResources()
                elif message.cmd.result == GatewayOperation.NOT_EXIST:
                    raise PyComfoConnectNotExist()
                elif message.cmd.result == GatewayOperation.RMI_ERROR:
                    raise PyComfoConnectRmiError()

                if confirm_type is None:
                    # We just need a message
                    return message
                elif message.msg.__class__ == confirm_type:
                    # We need the message with the correct type
                    return message
                else:
                    # We got a message with an incorrect type. Hopefully, this doesn't happen to often,
                    # since we just put it back on the queue.
                    self._queue.put(message)

            if time.time() - start > timeout:
                raise ValueError('Timeout waiting for response.')

    # ==================================================================================================================
    # Connection thread
    # ==================================================================================================================
    def _connection_thread_loop(self):
        """Makes sure that there is a connection open."""

        self._stopping = False
        while not self._stopping:

            # Start connection
            if not self.is_connected():

                # Wait a bit to avoid hammering the bridge
                time.sleep(5)

                try:
                    # Connect or re-connect
                    self._connect()

                except PyComfoConnectOtherSession:
                    self._bridge.disconnect()
                    _LOGGER.error('Could not connect to the bridge since there is already an open session.')
                    continue

                except Exception as exc:
                    _LOGGER.error(exc)
                    raise Exception('Could not connect to the bridge.')

            # Start background thread
            self._message_thread = threading.Thread(target=self._message_thread_loop)
            self._message_thread.start()

            # Re-register for sensor updates
            for sensor_id in self.sensors:
                self.cmd_rpdo_request(sensor_id, self.sensors[sensor_id])

            # Send the event that we are ready
            self._connected.set()

            # Wait until the message thread stops working
            self._message_thread.join()

            # Close socket connection
            self._bridge.disconnect()

    def _connect(self, takeover=False):
        """Connect to the bridge and login. Disconnect existing clients if needed by default."""

        try:
            # Connect to the bridge
            self._bridge.connect()

            # Login
            self.cmd_start_session(takeover, use_queue=False)

        except PyComfoConnectNotAllowed:
            # No dice, maybe we are not registered yet...

            # Register
            self.cmd_register_app(self._local_uuid, self._local_devicename, self._pin, use_queue=False)

            # Login
            self.cmd_start_session(takeover, use_queue=False)

        return True

    # ==================================================================================================================
    # Message thread
    # ==================================================================================================================

    def _message_thread_loop(self):
        """Listen for incoming messages and queue them or send them to a callback method."""

        # Reinitialise the queues
        self._queue = queue.Queue()

        next_keepalive = 0

        while not self._stopping:

            # Sends a keepalive every KEEPALIVE seconds.
            if time.time() > next_keepalive:
                next_keepalive = time.time() + KEEPALIVE
                self.cmd_keepalive()

            try:
                # Read a message from the bridge.
                message = self._bridge.read_message()

            except BrokenPipeError as exc:
                # Close this thread. The connection_thread will restart us.
                _LOGGER.warning('The connection was broken. We will try to reconnect later.')
                return

            if message:
                if message.cmd.type == GatewayOperation.CnRpdoNotificationType:
                    self._handle_rpdo_notification(message)

                elif message.cmd.type == GatewayOperation.GatewayNotificationType:
                    _LOGGER.info('Unhandled GatewayNotificationType')
                    # TODO: We should probably handle these somehow
                    pass

                elif message.cmd.type == GatewayOperation.CnNodeNotificationType:
                    _LOGGER.info('CnNodeNotificationType: %s @ Node Id %d [%s]', 
                        PRODUCT_ID_MAP[message.msg.productId], 
                        message.msg.nodeId, 
                        message.msg.NodeModeType.Name(message.msg.mode))
                    # TODO: We should probably handle these somehow
                    pass

                elif message.cmd.type == GatewayOperation.CnAlarmNotificationType:
                    _LOGGER.info('Unhandled CnAlarmNotificationType')
                    # TODO: We should probably handle these somehow
                    pass

                elif message.cmd.type == GatewayOperation.CloseSessionRequestType:
                    _LOGGER.info('The Bridge has asked us to close the connection. We will try to reconnect later.')
                    # Close this thread. The connection_thread will restart us.
                    return

                else:
                    # Send other messages to a queue
                    self._queue.put(message)

        return

    def _handle_rpdo_notification(self, message):
        """Update internal sensor state and invoke callback."""

        # Only process CnRpdoNotificationType
        if message.cmd.type != GatewayOperation.CnRpdoNotificationType:
            return False

        # Extract data
        data = message.msg.data.hex()
        if len(data) == 2:
            val = struct.unpack('b', message.msg.data)[0]
        elif len(data) == 4:
            val = struct.unpack('h', message.msg.data)[0]
        elif len(data) == 8:
            val = data
        else:
            val = data

        # Update local state
        # self.sensors[message.msg.pdid] = val

        if self.callback_sensor:
            self.callback_sensor(message.msg.pdid, val)

        return True

    # ==================================================================================================================
    # Commands
    # ==================================================================================================================

    def cmd_start_session(self, take_over=False, use_queue: bool = True):
        """Starts the session on the device by logging in and optionally disconnecting an already existing session."""

        reply = self._command(
            StartSessionRequest,
            {
                'takeover': take_over
            },
            use_queue=use_queue
        )
        return reply  # TODO: parse output

    def cmd_close_session(self, use_queue: bool = True):
        """Stops the current session."""

        reply = self._command(
            CloseSessionRequest,
            use_queue=use_queue
        )
        return reply  # TODO: parse output

    def cmd_list_registered_apps(self, use_queue: bool = True):
        """Returns a list of all the registered clients."""

        reply = self._command(
            ListRegisteredAppsRequest,
            use_queue=use_queue
        )
        return [
            {'uuid': app.uuid, 'devicename': app.devicename} for app in reply.msg.apps
        ]

    def cmd_register_app(self, uuid, device_name, pin, use_queue: bool = True):
        """Register a new app by specifying our own uuid, device_name and pin code."""

        reply = self._command(
            RegisterAppRequest,
            {
                'uuid': uuid,
                'devicename': device_name,
                'pin': pin,
            },
            use_queue=use_queue
        )
        return reply  # TODO: parse output

    def cmd_deregister_app(self, uuid, use_queue: bool = True):
        """Remove the specified app from the registration list."""

        if uuid == self._local_uuid:
            raise Exception('You should not deregister yourself.')

        try:
            self._command(
                DeregisterAppRequest,
                {
                    'uuid': uuid
                },
                use_queue=use_queue
            )
            return True

        except PyComfoConnectBadRequest:
            return False

    def cmd_version_request(self, use_queue: bool = True):
        """Returns version information."""

        reply = self._command(
            VersionRequest,
            use_queue=use_queue
        )
        return {
            'gatewayVersion': reply.msg.gatewayVersion,
            'serialNumber': reply.msg.serialNumber,
            'comfoNetVersion': reply.msg.comfoNetVersion,
        }

    def cmd_time_request(self, use_queue: bool = True):
        """Returns the current time on the device."""

        reply = self._command(
            CnTimeRequest,
            use_queue=use_queue
        )
        return reply.msg.currentTime

    def cmd_rmi_request(self, message, node_id: int = 1, use_queue: bool = True):
        """Sends a RMI request."""

        reply = self._command(
            CnRmiRequest,
            {
                'nodeId': node_id or 1,
                'message': message
            },
            use_queue=use_queue
        )
        return True

    def cmd_rpdo_request(self, pdid: int, type: int = 1, zone: int = 1, timeout=None, use_queue: bool = True):
        """Register a RPDO request."""

        reply = self._command(
            CnRpdoRequest,
            {
                'pdid': pdid,
                'type': type,
                'zone': zone or 1,
                'timeout': timeout
            },
            use_queue=use_queue
        )
        return reply

    def cmd_keepalive(self, use_queue: bool = True):
        """Sends a keepalive."""

        self._command(
            KeepAlive,
            use_queue=use_queue
        )
        return True

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

# Sensor variable size
RPDO_TYPE_MAP = {
    65: 1,
    81: 3,
    117: 1,
    118: 1,
    119: 2,
    120: 2,
    121: 2,
    122: 2,
    128: 2,
    129: 2,
    130: 2,
    192: 2,
    213: 2,
    214: 2,
    215: 2,
    221: 6,
    274: 6,
    275: 6,
    276: 6,
    290: 1,
    291: 1,
    292: 1,
    294: 1,
}


class ComfoConnect(object):
    """Implements the commands to communicate with the ComfoConnect ventilation unit."""

    """Callback function to invoke when sensor updates are received."""
    callback = None

    def __init__(self, bridge: Bridge, local_uuid=DEFAULT_LOCAL_UUID, local_devicename=DEFAULT_LOCAL_DEVICENAME,
                 pin=DEFAULT_PIN):
        self._bridge = bridge
        self._local_uuid = local_uuid
        self._local_devicename = local_devicename
        self._pin = pin
        self._reference = 1

        self._queue = queue.Queue()
        self._stopping = False
        self._thread = None

        self.sensors = {}

    # ==================================================================================================================
    # Core functions
    # ==================================================================================================================

    def connect(self, takeover=False):
        """Connect to the bridge and login. Disconnect existing clients if needed by default."""

        # Connect to the bridge
        self._bridge.connect()

        # Start background thread
        self._stopping = False
        self._thread = threading.Thread(target=self._threading_loop)
        self._thread.start()

        try:
            # Login
            self.cmd_start_session(takeover)

            return True

        except PyComfoConnectNotAllowed:
            # No dice, maybe we are not registered yet...
            try:
                # Register
                self.cmd_register_app()

                # Login
                self.cmd_start_session(takeover)

            except PyComfoConnectNotAllowed:
                # Nope. Give up.
                self.disconnect()
                raise Exception('Could not connect to the bridge since the PIN seems to be invalid.')

            except:
                self.disconnect()
                raise Exception('Could not connect to the bridge.')

        except PyComfoConnectOtherSession:
            self.disconnect()
            raise Exception('Could not connect to the bridge since there is already an open session.')

        except Exception as e:
            self.disconnect()
            raise Exception('Could not connect to the bridge.')

    def disconnect(self):
        """Disconnect from the bridge."""

        # Set the stopping flag
        self._stopping = True

        # Wait for the background thread to finish
        self._thread.join()
        self._thread = None

    def is_connected(self):
        """Returns weather there is a connection with the bridge."""
        return self._bridge.is_connected()

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
                elif message.cmd.result == GatewayOperation.NOT_EXISTS:
                    raise PyComfoConnectNotExists()
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
    # Background thread
    # ==================================================================================================================

    def _reconnect(self, timeout=5):
        """Make sure that we are connected and ready to roll."""

        # Kill connection to bridge
        self._bridge.disconnect()

        # Initialise countdown to 5 seconds so we have a small delay
        countdown = time.time() + 5

        while not self._stopping:

            if countdown < time.time():

                # Connect to bridge
                self._bridge.connect()

                try:
                    # Login, but don't use the queue for the response.
                    self._command(StartSessionRequest, use_queue=False)

                    # Reinitialise the queues
                    self._queue = queue.Queue()

                    # We made it!
                    return True

                except PyComfoConnectOtherSession:
                    print('We tried to login again but there is still an open session with another device.')
                    pass

                except Exception as e:
                    print('We tried to login again. But it didn\'t work due to some other reason.')
                    pass

                # Restart timer
                countdown = time.time() + timeout

                # Kill connection to bridge
                self._bridge.disconnect()

                continue

            # Wait a second to not flood the CPU.
            time.sleep(1)

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
        self.sensors[message.msg.pdid] = val

        if self.callback:
            self.callback(message.msg.pdid, val)

        return True

    def _threading_loop(self):
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

            except BrokenPipeError:
                # Try to reconnect if this should fail.
                self._reconnect()
                continue

            if message:
                if message.cmd.type == GatewayOperation.CnRpdoNotificationType:
                    self._handle_rpdo_notification(message)

                elif message.cmd.type == GatewayOperation.GatewayNotificationType:
                    # TODO: We should probably handle these somehow
                    pass

                elif message.cmd.type == GatewayOperation.CnNodeNotificationType:
                    # TODO: We should probably handle these somehow
                    pass

                elif message.cmd.type == GatewayOperation.CnAlarmNotificationType:
                    # TODO: We should probably handle these somehow
                    pass

                elif message.cmd.type == GatewayOperation.CloseSessionRequestType:
                    # We got disconnected. Reconnect. And don't return until we have a working connection again.
                    # Now hurry!
                    self._reconnect()

                else:
                    # Send other messages to a queue
                    self._queue.put(message)

        # Close socket connection
        self._bridge.disconnect()

        return

    # ==================================================================================================================
    # Commands
    # ==================================================================================================================

    def cmd_start_session(self, take_over=False):
        """Starts the session on the device by logging in and optionally disconnecting an already existing session."""

        reply = self._command(
            StartSessionRequest,
            {
                'takeover': take_over
            }
        )
        return reply  # TODO: parse output

    def cmd_close_session(self):
        """Stops the current session."""

        reply = self._command(
            CloseSessionRequest
        )
        return reply  # TODO: parse output

    def cmd_list_registered_apps(self):
        """Returns a list of all the registered clients."""

        reply = self._command(
            ListRegisteredAppsRequest
        )
        return [
            {'uuid': app.uuid, 'devicename': app.devicename} for app in reply.msg.apps
        ]

    def cmd_register_app(self, uuid=None, device_name=None, pin=None):
        """Register a new app by specifying our own uuid, device_name and pin code."""

        reply = self._command(
            RegisterAppRequest,
            {
                'uuid': uuid or self._local_uuid,
                'devicename': device_name or self._local_devicename,
                'pin': pin or self._pin,
            }
        )
        return reply  # TODO: parse output

    def cmd_deregister_app(self, uuid):
        """Remove the specified app from the registration list."""

        if uuid == self._local_uuid:
            raise Exception('You should not deregister yourself.')

        try:
            self._command(
                DeregisterAppRequest,
                {
                    'uuid': uuid
                }
            )
            return True

        except PyComfoConnectBadRequest:
            return False

    def cmd_version_request(self):
        """Returns version information."""

        reply = self._command(
            VersionRequest
        )
        return {
            'gatewayVersion': reply.msg.gatewayVersion,
            'serialNumber': reply.msg.serialNumber,
            'comfoNetVersion': reply.msg.comfoNetVersion,
        }

    def cmd_time_request(self):
        """Returns the current time on the device."""

        reply = self._command(
            CnTimeRequest
        )
        return reply.msg.currentTime

    def cmd_rmi_request(self, message, node_id: int = 1):
        """Sends a RMI request."""

        reply = self._command(
            CnRmiRequest,
            {
                'nodeId': node_id or 1,
                'message': message
            }
        )
        return True

    def cmd_rpdo_request(self, pdid: int, type: int = None, zone: int = 1, timeout=None):
        """Register a RPDO request."""

        reply = self._command(
            CnRpdoRequest,
            {
                'pdid': pdid,
                'type': type or RPDO_TYPE_MAP.get(pdid),
                'zone': zone or 1,
                'timeout': timeout
            }
        )
        return True

    def cmd_keepalive(self):
        """Sends a keepalive."""

        self._command(
            KeepAlive,
        )
        return True

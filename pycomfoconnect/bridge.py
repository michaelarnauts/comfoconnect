import logging
import select
import socket

from .message import *

_LOGGER = logging.getLogger('bridge')


class Bridge(object):
    """Implements an interface to send and receive messages from the Bridge."""

    PORT = 56747

    @staticmethod
    def discover(host=None, timeout=5):
        """Broadcast the network and look for local bridges."""

        # Setup socket
        udpsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udpsocket.setblocking(0)
        udpsocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        # Send broadcast packet
        if host is None:
            udpsocket.sendto(b"\x0a\x00", ('<broadcast>', Bridge.PORT))
        else:
            udpsocket.sendto(b"\x0a\x00", (host, Bridge.PORT))

        # Try to read response
        parser = DiscoveryOperation()
        bridges = []
        while True:
            ready = select.select([udpsocket], [], [], timeout)
            if not ready[0]:
                break

            data, source = udpsocket.recvfrom(100)

            # Parse data
            parser.ParseFromString(data)
            ip_address = parser.searchGatewayResponse.ipaddress
            uuid = parser.searchGatewayResponse.uuid

            # Add a new Bridge to the list
            bridges.append(
                Bridge(ip_address, uuid)
            )

            # Don't look for other bridges if we directly discovered it by IP
            if host:
                break

        udpsocket.close()

        # Return found bridges
        return bridges

    def __init__(self, host: str, uuid: str) -> None:
        self.host = host
        self.uuid = uuid

        self._socket = None
        self.debug = False

    def connect(self) -> bool:
        """Open connection to the bridge."""

        if self._socket is None:
            tcpsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcpsocket.connect((self.host, Bridge.PORT))
            tcpsocket.setblocking(0)
            self._socket = tcpsocket

        return True

    def disconnect(self) -> bool:
        """Close connection to the bridge."""

        self._socket.close()
        self._socket = None

        return True

    def is_connected(self):
        """Returns weather there is an open socket."""

        return self._socket is not None

    def read_message(self, timeout=1) -> Message:
        """Read a message from the connection."""

        if self._socket is None:
            raise BrokenPipeError()

        # Check if there is data available
        ready = select.select([self._socket], [], [], timeout)
        if not ready[0]:
            # Timeout
            return None

        # Read packet size
        msg_len_buf = self._socket.recv(4)
        if not msg_len_buf:
            # No data, but there has to be.
            raise BrokenPipeError()

        # Read rest of packet
        msg_len = struct.unpack('>L', msg_len_buf)[0]
        msg_buf = self._socket.recv(msg_len)
        if not msg_buf:
            # No data, but there has to be.
            raise BrokenPipeError()

        # Decode message
        message = Message.decode(msg_len_buf + msg_buf)

        # Debug message
        _LOGGER.debug("RX %s", message)

        return message

    def write_message(self, message: Message) -> bool:
        """Send a message."""

        if self._socket is None:
            raise Exception('Not connected!')

        # Construct packet
        packet = message.encode()

        # Debug message
        _LOGGER.debug("TX %s", message)

        # Send packet
        try:
            self._socket.sendall(packet)
        except BrokenPipeError:
            self.disconnect()
            return False

        return True

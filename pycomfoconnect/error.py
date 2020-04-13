class PyComfoConnectError(Exception):
    """ Base error for PyComfoConnect """
    pass


class PyComfoConnectBadRequest(PyComfoConnectError):
    """ An error occured because the request was invalid. """
    pass


class PyComfoConnectInternalError(PyComfoConnectError):
    """ An error occured because something went wrong inside the bridge. """
    pass


class PyComfoConnectNotReachable(PyComfoConnectError):
    """ An error occured because the bridge could not reach the ventilation unit. """
    pass


class PyComfoConnectOtherSession(PyComfoConnectError):
    """ An error occured because the bridge is already connected to a different device. """

    def __init__(self, devicename):
        self.devicename = devicename


class PyComfoConnectNotAllowed(PyComfoConnectError):
    """ An error occured because you have not authenticated yet. """
    pass


class PyComfoConnectNoResources(PyComfoConnectError):
    pass


class PyComfoConnectNotExist(PyComfoConnectError):
    pass


class PyComfoConnectRmiError(PyComfoConnectError):
    pass

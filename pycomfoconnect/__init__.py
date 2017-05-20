"""
PyComfoConnect: Manage your Zehnder ComfoConnect Q350/Q450/Q650 ventilation unit
"""

DEFAULT_UUID = '00000000000000000000000000000001'
DEFAULT_NAME = 'pycomfoconnect'
DEFAULT_PIN = 0

__author__ = 'Michaël Arnauts <michael.arnauts@gmail.com>'

from .comfoconnect import *
from .error import *
from .const import *
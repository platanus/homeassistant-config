
"""
Allows to configure a switch using RPi GPIO.
For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/switch.trigger_switch/
"""
import logging

import voluptuous as vol

from homeassistant.components.switch import PLATFORM_SCHEMA
import homeassistant.components.rpi_gpio as rpi_gpio
from homeassistant.const import DEVICE_DEFAULT_NAME
from homeassistant.helpers.entity import ToggleEntity
import homeassistant.helpers.config_validation as cv

from time import sleep
from homeassistant.const import (CONF_TIMEOUT)

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ['rpi_gpio']

CONF_PULL_MODE = 'pull_mode'
CONF_PORTS = 'ports'
CONF_INVERT_LOGIC = 'invert_logic'
CONF_TIMEOUT = 'timeout'

DEFAULT_INVERT_LOGIC = False
#ms
DEFAULT_TIMEOUT = "00:00:01" 

_SWITCHES_SCHEMA = vol.Schema({
    cv.positive_int: cv.string,
})

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_PORTS): _SWITCHES_SCHEMA,
    vol.Optional(CONF_INVERT_LOGIC, default=DEFAULT_INVERT_LOGIC): cv.boolean,
    vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): cv.string
})

#Get seconds from string "hours:minutes:seconds"
def seconds(strTime):
    sec = strTime.split(":")
    sec = int(sec[0]) * pow(60, 2) + int(sec[1]) * 60 + int(sec[2])
    return sec

# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Raspberry PI GPIO devices."""
    invert_logic = config.get(CONF_INVERT_LOGIC)
    #In seconds
    timeout = seconds(config.get(CONF_TIMEOUT))

    switches = []
    ports = config.get(CONF_PORTS)
    for port, name in ports.items():
        switches.append(timeoutSwitch(name, port, invert_logic, timeout))
    add_devices(switches)


class timeoutSwitch(ToggleEntity):
    """Representation of a  Raspberry Pi GPIO."""

    def __init__(self, name, port, invert_logic, timeout):
        """Initialize the pin."""
        self._name = name or DEVICE_DEFAULT_NAME
        self._port = port
        self._invert_logic = invert_logic
        self._timeout = timeout
        self._state = False
        rpi_gpio.setup_output(self._port)
        rpi_gpio.write_output(self._port, 1 if self._invert_logic else 0)

    @property
    def name(self):
        """Return the name of the switch."""
        return self._name

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._state

    def turn_on(self, **kwargs):
        """Turn the device on."""
        rpi_gpio.write_output(self._port, 0 if self._invert_logic else 1)
        self._state = True
        self.schedule_update_ha_state()        
        sleep(self._timeout) # Time in seconds.
        self.turn_off(**kwargs)

    def turn_off(self, **kwargs):
        """Turn the device off."""
        rpi_gpio.write_output(self._port, 1 if self._invert_logic else 0)
        self._state = False
        self.schedule_update_ha_state()


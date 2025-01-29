"""Constants for the PID Controller integration."""

from homeassistant.const import Platform

DOMAIN = "pid_controller"
PLATFORMS = [Platform.NUMBER]

ATTR_INPUT1 = "input1"
ATTR_INPUT2 = "input2"
ATTR_OUTPUT = "output"

CONF_NUMBERS = "numbers"
CONF_INPUT1 = "input1"
CONF_INPUT2 = "input2"
CONF_OUTPUT = "output"
CONF_STEP = "step"
CONF_PID_DIR = "direction"

MODE_SLIDER = "slider"
MODE_BOX = "box"
MODE_AUTO = "auto"

SERVICE_SET_KI = "set_ki"
SERVICE_SET_KP = "set_kp"
SERVICE_SET_KD = "set_kd"

PID_DIR_DIRECT = "direct"
PID_DIR_REVERSE = "reverse"

DEFAULT_MODE = MODE_SLIDER
DEFAULT_CYCLE_TIME = {"seconds": 30}

DEFAULT_PID_DIR = PID_DIR_DIRECT
DEFAULT_PID_KI = 1.0
DEFAULT_PID_KP = 0.1
DEFAULT_PID_KD = 0.0

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# LABELS
lDate = "Date"
lT1 = "t° Bas"
lT2  = "t° Haut"
lT3  = "t° Milieu"
lHum1 = "Tx Humidité"
lCoolingOn = "Compresseur"
lHeatingOn = "Chauffage"
lFanOn = "Ventilation"
lIsAuto = "Mode Automatique"

# TEMPERATURES
setTemperatureMax = 12.5
setTemperatureMin = 11.5
threshold = 0.5
fanMaxTempDiff = 1.5

# DEFAULT MODES
DEFAULT_STATE_MODE_AUTO = True # 1 : Auto / 0 : Manual (1 = Default)
DEFAULT_STATE_COOLING = False #
DEFAULT_STATE_HEATING = False #
DEFAULT_STATE_FAN = True #

SENSORS_REFRESH_TIME = 120
AUTO_FORCE_FAN_ON = True
ENABLE_RPI_WATCHDOG = True
WATCHDOG_LOCATION = '/dev/watchdog'
NTP_SERVER = 'pool.ntp.org'
NTP_PORT = 123
HTTP_STDOUT_LOGS = False;

# GPIO
COOL_GPIO = 16
HEAT_GPIO = 20
FAN_GPIO = 26

# COMPRESSOR TIMERS
COMPRESSOR_TOOGLE_TIME = 5400
COMPRESSOR_RECOVERY_TIME = 600
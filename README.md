# Picellar

![My image](https://raw.githubusercontent.com/gbraux/picellar/master/screenshot.png)

Picellar is a Rapsberry-PI based controller (in Python) for homemades wine cellars (based on an old fridge).

It gets data from several sensors (temp & humidity) and have direct control over the fridge (compressor, fan and heating element)
It provides a Web GUI to read sensors history, and also has support for Mini LCD screen to get instant sensors values (ie. mounted on the fridge door).

To protect the wine in case of application/RPi crash, it also has support for the RPi Watchdog timer to initiate a reboot in case of an emergency.

# My setup
- Old Fridge with original temp regulation system removed. Can easily fit 150-180 75cl bottles.
- 2x Dallas 1-Wire temperature sensors (top & bottom of the cellar)
- 1x DHT22 Temperature/Humidity sensor (middle of the cellar)
- 1x 220v Heating cable mounted inside the fridge
- 3x 5v 230v relays (compressor, fan & heater control)
- 1x 2.5' touch enabled lcd screen.

# Running the code
Requires python 2.7.
To start the app : python picellar_controller.py

Guillaume BRAUX.
gbraux@supinfo.com

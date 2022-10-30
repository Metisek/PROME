# Prome
Device usedto randomize numbers for students' workplacs.

## Overview

# Hardware setup
## Devices list

Mandatory:

* [Arduino uno](https://store.arduino.cc/products/arduino-uno-rev3)
* [MOXA NE4110S](https://www.moxa.com/en/products/industrial-edge-connectivity/serial-device-servers/serial-embedded-modules/ne-4100-series/ne-4110s)
* [WHMXE-595-2](https://pl.aliexpress.com/item/4000480352967.html) 2x7-segment display ([programming guide](https://www.ardumotive.com/2-digit-7seg-display-en.html))
* [GAINTA G17081UBK](https://www.gainta.com/en/g17081ubk.html) or other 1U rack case
* [PS-05-5](https://www.tme.com/us/en-us/details/ps-05-5/open-frame-power-supplies/mean-well/) or other 5V PSU with minimum output current of 1A (Phone charger could be used)
* 1x yellow and 1x green LED diodes
* 4x 2N3908 or similar NPN transistors
* Resistors:
  - 4x 4k7Ω
  - 2x 6k8Ω
  - 2x 470Ω

Optional:
* Any [Arduino solder shield](https://learn.adafruit.com/adafruit-proto-shield-arduino/solder-it)
* Any universal solder board
* 2x GP 2x5-pin sockets
* 2x GP 2x7-pin sockets
* 1x IDC10 - IDC10 cable
* 1x IDC14 - IDC14 cable
* 4x CRIMP 5-pin socket
* 1x CRIMP 2-pin socket
* 2x CRIMP 5-pin cable
* 1x CRIMP 2-pin cable

## Required packages
Excluding sqlite3 dll (bundled with source code) you should install the following packages (tested on Python 3.9.10):
* pysimplegui
* tk
* pyserial
* configparser

You can install proper packages using following command

```python
pip install pysimplegui tk pyserial configparser

```

## Running application
After installing packages you can start application as long as working directory is in application/python script folder. To check this terminal automatically print current working directory, for example:

```
PROME cwd: C:\Users\Guest\GIT\PROME\Code

```

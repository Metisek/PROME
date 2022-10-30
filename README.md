# Prome
Device used to randomize numbers for students' workplacs. This README combines overview of this device with instructions how to setup it by yourself.

## Overview
![Device photo](Photos/Overview1.png)

# Hardware setup

To run 

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

# Software setup

To control device, you have to:
* Setup MOXA NE4110S device with proper IP address
* Configure proper COM port(s)
* Compile python app OR use already compiled one

## MOXA NE4110S IP configuration
In order to change the IP address of the MOXA NE4110S device, you need to write down its MAC address and connect it to the computer / switch.

After these steps, you should:

1. In CMD type *arp –s <IP address> 00-90-E8-tt-tt-tt* (where t are the characters of the MAC address).
2. In CMD type *telnet <IP address> 6000* or similarly try to connect to PuTTY. It should drop the connection.
3. Reset the device.

From now on, MOXA will have an IP entered by us. It can be configured via telnet or a browser.

## COM port setup

To properly use device you have to install [NPort](https://www.moxa.com/en/products/industrial-edge-connectivity/serial-device-servers/serial-embedded-modules/ne-4100-series#resources). 

## Installing PROME software (optional)

Currently only polish language is supported, it is possible to implement other languages if necessary.

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

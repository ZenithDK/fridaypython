#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is a crude and simple battery simulator.
It can be charged and discharged, and it also has a cutoff-voltage.
"""

import hameg
import every
import time
import sys

TOTAL_CAPACITY = 205 # mAh
MULTIPLIER = 80 # Charging will happen this much (times) faster.
HAMEG_PORT = "/dev/ttyUSB0"
HAMEG_OUTPUT = 1

MAXIMUM_VOLTAGE = 4.2
MINIMUM_VOLTAGE = 2.7
BATTERY_VOLTAGE = 2.7 # volts

psu = hameg.Hameg(HAMEG_PORT)
every = every.Every()

def mapValues(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def printValues():
    sys.stdout.write("AV1: %0.2f SV1: %0.2f AC1: %0.3f SC1: %0.3f AV2: %0.2f SV2: %0.2f AC2: %0.3f SC2: %0.3f\n"%(
            psu.getMeasuredVoltage(1),
            psu.getVoltage(1),
            psu.getMeasuredCurrent(1),
            psu.getCurrent(1),
            psu.getMeasuredVoltage(2),
            psu.getVoltage(2),
            psu.getMeasuredCurrent(2),
            psu.getCurrent(2)
            ))


last_time = time.time()
battery_capacity = mapValues(BATTERY_VOLTAGE, MINIMUM_VOLTAGE, MAXIMUM_VOLTAGE, 0, TOTAL_CAPACITY)

psu.setCurrent(HAMEG_OUTPUT, 0.5)
psu.setVoltage(HAMEG_OUTPUT, 0.0)
psu.setOutputState(True)

sys.stderr.write("Press <enter> to continue\n")
raw_input()
every.func_lock()
psu.setVoltage(HAMEG_OUTPUT, BATTERY_VOLTAGE)
every.func_release()
every.add(printValues, 500)
every.start()

while True:
    every.func_lock()
    current = (psu.getMeasuredCurrent(HAMEG_OUTPUT)*1000)*MULTIPLIER # converted to mA
    every.func_release()

    current_time = time.time()
    battery_capacity = battery_capacity - (current / ((current_time-last_time)) / 3600)
    battery_voltage = mapValues(battery_capacity, 0, TOTAL_CAPACITY, MINIMUM_VOLTAGE, MAXIMUM_VOLTAGE)

    every.func_lock()
    psu.setVoltage(HAMEG_OUTPUT, min(battery_voltage, MAXIMUM_VOLTAGE)) # Make sure we don't go over voltage.
    every.func_release()

    if battery_voltage < MINIMUM_VOLTAGE:
        every.func_lock()
        psu.setOutputState(False) # Cutoff voltage
        every.func_release()
    else:
        every.func_lock()
        psu.setOutputState(True)
        every.func_release()

    last_time = current_time
    sys.stderr.write("\r%d / %d"%(battery_capacity, TOTAL_CAPACITY))
    time.sleep(1)
